import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import HTTPException, status
from uuid import uuid4
from PIL import Image
from io import BytesIO
from ..core.config import settings
from ..core.tasks import celery_app
import logging

logger = logging.getLogger(__name__)

class S3Util:
    def __init__(self):
        try:
            self.s3 = boto3.client(
                's3',
                region_name=settings.aws_region_name,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            self.bucket_name = settings.aws_bucket_name
        except NoCredentialsError as e:
            logger.error(f"AWS credentials not available: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AWS credentials not available"
            )
        except Exception as e:
            logger.error(f"Error initializing S3 client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error initializing S3 client"
            )

    @staticmethod
    def optimize_image(file, width: int, height: int, quality: int) -> BytesIO:
        try:
            image = Image.open(file.file)
            image = image.resize((width, height), Image.LANCZOS)
            optimized_image = BytesIO()
            image.save(optimized_image, format=image.format, quality=quality)
            optimized_image.seek(0)
            return optimized_image
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error optimizing image"
            )

    @celery_app.task
    def upload_file(self, file, folder: str, width: int, height: int, quality: int) -> str:
        try:
            optimized_image = self.optimize_image(file, width, height, quality)
            file_extension = file.filename.split('.')[-1]
            file_key = f"{folder}/{uuid4()}.{file_extension}"
            self.s3.upload_fileobj(optimized_image, self.bucket_name, file_key)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
        except NoCredentialsError as e:
            logger.error(f"AWS credentials not available: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AWS credentials not available"
            )
        except ClientError as e:
            logger.error(f"Client error during file upload: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading file to S3"
            )
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error during file upload"
            )

    def delete_file(self, file_url: str):
        try:
            file_key = file_url.split(f"{self.bucket_name}.s3.amazonaws.com/")[-1]
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_key)
        except NoCredentialsError as e:
            logger.error(f"AWS credentials not available: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AWS credentials not available"
            )
        except ClientError as e:
            logger.error(f"Client error during file deletion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting file from S3"
            )
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error during file deletion"
            )

    def get_files(self, folder: str):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=folder)
            return [f"https://{self.bucket_name}.s3.amazonaws.com/{obj['Key']}" for obj in response.get('Contents', [])]
        except NoCredentialsError as e:
            logger.error(f"AWS credentials not available: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AWS credentials not available"
            )
        except ClientError as e:
            logger.error(f"Client error during listing files: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error listing files from S3"
            )
        except Exception as e:
            logger.error(f"Unexpected error during listing files: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error during listing files"
            )