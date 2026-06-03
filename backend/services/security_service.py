import os
import magic
import boto3
from uuid import uuid4

# Allowlist configuration
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.csv', '.txt'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/png',
    'image/jpeg',
    'text/csv',
    'text/plain'
}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

class SecurityValidationException(Exception):
    pass

def validate_and_upload_attachment(filename: str, file_data: bytes, mime_type: str) -> dict:
    """
    Validates the attachment for size, extension, and magic bytes.
    If valid, uploads to S3 and returns metadata.
    Raises SecurityValidationException if invalid.
    """
    # 1. Size Validation
    if len(file_data) > MAX_FILE_SIZE_BYTES:
        raise SecurityValidationException(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.")

    # 2. Extension Validation
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise SecurityValidationException(f"File extension '{ext}' is not allowed.")

    # 3. Mime Type Validation (Basic)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise SecurityValidationException(f"MIME type '{mime_type}' is not allowed.")

    # 4. Magic Bytes Validation
    magic_mime = magic.from_buffer(file_data[:2048], mime=True)
    if magic_mime not in ALLOWED_MIME_TYPES:
        raise SecurityValidationException(f"Detected MIME type '{magic_mime}' does not match allowed types.")

    # Upload to S3
    bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
    if not bucket_name:
        raise Exception("AWS_S3_BUCKET_NAME is not configured.")

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )

    # Generate unique key
    safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in '._-']).rstrip()
    s3_key = f"attachments/{uuid4()}_{safe_filename}"

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file_data,
            ContentType=magic_mime
        )
    except Exception as e:
        raise Exception(f"Failed to upload to S3: {str(e)}")

    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"

    return {
        "filename": filename,
        "file_type": magic_mime,
        "size": len(file_data),
        "s3_key": s3_key,
        "s3_url": s3_url
    }
