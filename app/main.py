from fastapi import FastAPI, UploadFile, HTTPException, Request
import boto3
import os
from typing import Dict

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "qrcode-test-jd")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
    raise RuntimeError("AWS credentials are not configured")

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

app = FastAPI()
# Utilities to parse PIX QR codes

def parse_tlv(data: str) -> Dict[str, str]:
    pos = 0
    result: Dict[str, str] = {}
    while pos < len(data):
        tag = data[pos:pos+2]
        length = int(data[pos+2:pos+4])
        value = data[pos+4:pos+4+length]
        pos += 4 + length
        result[tag] = value
    return result

def extract_s3_key_from_qr(qr: str) -> str:
    tags = parse_tlv(qr)
    unreserved = tags.get("80")
    if not unreserved:
        raise ValueError("Field 80 not found")
    sub_tags = parse_tlv(unreserved)
    url = sub_tags.get("25")
    if not url:
        raise ValueError("Field 25 not found")
    prefix = "qrcode-h.jdpsti.com.br/"
    if url.startswith(prefix):
        return url[len(prefix):]
    return url


@app.post("/upload/{filename}")
async def upload_file(filename: str, request: Request):
    content_type = request.headers.get("content-type")
    if content_type != "application/jose":
        raise HTTPException(status_code=400, detail="Invalid content-type")
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty payload")
    key = filename
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=body,
            ContentType="application/jose",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Uploaded", "key": key}

@app.post("/upload_by_qr")
async def upload_by_qr(qr_string: str, request: Request):
    """Upload payload using the key parsed from a PIX QR code string."""
    content_type = request.headers.get("content-type")
    if content_type != "application/jose":
        raise HTTPException(status_code=400, detail="Invalid content-type")
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty payload")
    try:
        key = extract_s3_key_from_qr(qr_string)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=body,
            ContentType="application/jose",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Uploaded", "key": key}
