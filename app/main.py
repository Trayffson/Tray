from fastapi import FastAPI, UploadFile, HTTPException, Request
import boto3
import os

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
