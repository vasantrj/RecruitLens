import uuid
import boto3
from botocore.client import Config

from src.config import settings

BUCKET_NAME = "resumes"

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.minio_endpoint,
    aws_access_key_id=settings.minio_access_key,
    aws_secret_access_key=settings.minio_secret_key,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


def ensure_bucket_exists():
    existing = [b["Name"] for b in s3_client.list_buckets().get("Buckets", [])]
    if BUCKET_NAME not in existing:
        s3_client.create_bucket(Bucket=BUCKET_NAME)


def upload_resume(file_bytes: bytes, original_filename: str) -> str:
    ensure_bucket_exists()
    extension = original_filename.split(".")[-1]
    key = f"{uuid.uuid4()}.{extension}"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=file_bytes)
    return key


def get_resume_bytes(key: str) -> bytes:
    obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
    return obj["Body"].read()