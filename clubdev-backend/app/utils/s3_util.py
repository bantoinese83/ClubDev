import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException, status
from uuid import uuid4
from ..core.config import settings

class S3Util:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            region_name=settings.aws_region_name,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        self.bucket_name = settings.aws_bucket_name

    def upload_file(self, file, folder: str) -> str:
        try:
            file_extension = file.filename.split('.')[-1]
            file_key = f"{folder}/{uuid4()}.{file_extension}"
            self.s3.upload_fileobj(file.file, self.bucket_name, file_key)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
        except NoCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AWS credentials not available"
            )

    def delete_file(self, file_url: str):
        try:
            file_key = file_url.split(f"{self.bucket_name}.s3.amazonaws.com/")[-1]
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_key)
        except NoCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AWS credentials not available"
            )