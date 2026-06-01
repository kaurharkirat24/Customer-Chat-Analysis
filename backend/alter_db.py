import sqlite3

conn = sqlite3.connect('cxflow.db')
try:
    conn.execute('ALTER TABLE interactions ADD COLUMN confidence_score FLOAT DEFAULT 1.0')
except Exception as e:
    print(e)

try:
    conn.execute("ALTER TABLE interactions ADD COLUMN priority VARCHAR DEFAULT 'P3'")
except Exception as e:
    print(e)

try:
    conn.execute('ALTER TABLE interactions ADD COLUMN feature_tag VARCHAR')
except Exception as e:
    print(e)

conn.commit()
conn.close()
print("Database altered successfully.")
