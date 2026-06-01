from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models

app = FastAPI(title="CX Flow API", description="Customer Experience Automation Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.auth import router as auth_router
from api.ingestion import router as ingestion_router

app.include_router(auth_router)
app.include_router(ingestion_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "CX Flow API is running."}

import asyncio
from models.database import SessionLocal
from models.interaction import Customer, Interaction, ActionLog
from services.gmail_service import fetch_unread_emails
from graph.workflow import app_graph

async def gmail_polling_task():
    print("Started background Gmail polling task...")
    while True:
        try:
            # We must handle the case where token.json doesn't exist yet safely
            try:
                emails = fetch_unread_emails()
            except Exception as e:
                print(f"Gmail Polling Skiped: {e}")
                emails = []

            if emails:
                db = SessionLocal()
                try:
                    for email_data in emails:
                        sender = email_data["sender"]
                        # Clean up typical email format 'Name <email@domain.com>'
                        if "<" in sender and ">" in sender:
                            clean_email = sender.split("<")[1].split(">")[0]
                        else:
                            clean_email = sender

                        text = email_data["subject"] + "\n\n" + email_data["body"]
                        
                        customer = db.query(Customer).filter(Customer.email == clean_email).first()
                        if not customer:
                            customer = Customer(email=clean_email, name=sender.split("<")[0].strip())
                            db.add(customer)
                            db.commit()
                            db.refresh(customer)
                        
                        interaction = Interaction(
                            customer_id=customer.id,
                            channel="Gmail",
                            original_message=text
                        )
                        db.add(interaction)
                        db.commit()
                        db.refresh(interaction)
                        
                        try:
                            initial_state = {
                                "interaction_id": interaction.id,
                                "text": text,
                                "customer_email": clean_email
                            }
                            final_state = app_graph.invoke(initial_state)
                            
                            interaction.ai_intent = final_state.get("intent")
                            interaction.ai_sentiment = final_state.get("sentiment")
                            interaction.confidence_score = final_state.get("confidence_score", 1.0)
                            interaction.priority = final_state.get("priority", "P3")
                            interaction.feature_tag = final_state.get("feature_tag")
                            interaction.status = final_state.get("status", "Processed")
                            db.commit()
                            
                            action_log = ActionLog(
                                interaction_id=interaction.id,
                                action_type=final_state.get("action_type"),
                                outgoing_message=final_state.get("outgoing_message"),
                                status="Success"
                            )
                            db.add(action_log)
                            db.commit()
                            print(f"✅ Processed email from {clean_email} -> Intent: {interaction.ai_intent}")
                        
                        except Exception as ai_err:
                            print(f"❌ CRITICAL AI PIPELINE ERROR for {clean_email}: {ai_err}")
                            interaction.ai_intent = "Pipeline_Error"
                            interaction.ai_sentiment = "Pipeline_Error"
                            interaction.status = "Failed_AI_Analysis"
                            db.commit()
                            
                            action_log = ActionLog(
                                interaction_id=interaction.id,
                                action_type="System_Alert",
                                outgoing_message=f"System failed to process interaction due to AI engine failure: {ai_err}",
                                status="Failed"
                            )
                            db.add(action_log)
                            db.commit()
                            
                finally:
                    db.close()
        except Exception as e:
            print(f"Error in overall polling task loop: {e}")
            
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(gmail_polling_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
