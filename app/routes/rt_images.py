import io
import boto3
from fastapi import APIRouter, HTTPException, status, Depends, Response, UploadFile
from PIL import Image
from datetime import datetime

from app.utils.u_db import query
from app.utils.u_auth import get_current_user
from app.utils.u_images import resize_image
from app.schemas import UserDB
from app.config import settings

router = APIRouter(prefix="", tags=["images"],)

S3_ACCESS_KEY = settings.S3_ACCESS_KEY
S3_SECRET_KEY = settings.S3_SECRET_KEY
s3 = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

bucket_name = 'forgate'

@router.post("/upload")
def upload_image(file: UploadFile, user: UserDB = Depends(get_current_user)):
    
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file was uploaded")
    
    img = Image.open(file.file)

    # Resize the image
    img = resize_image(img,500)
    extension = file.filename.lower().rsplit('.', 1)[1]
    format='JPEG' if extension != 'png' else 'PNG'

    # Save the resized image to memory
    img_bytes = io.BytesIO()
    if format == 'PNG':
        img = img.convert('RGBA')
        content_type = "image/png"
    else:
        img = img.convert('RGB')
        content_type = "image/jpeg"
    img.save(img_bytes, format=format)
    img_bytes = img_bytes.getvalue()
    # Generate a unique image name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Generate a unique path for the image
    image_path = f"items/{str(user.hotel_id)}/{timestamp}/original/{file.filename}"
    
    s3.put_object(Body=img_bytes,
            Bucket=bucket_name,
            Key=image_path,
            ContentType=content_type
            )
    
    return {'img_url':image_path}