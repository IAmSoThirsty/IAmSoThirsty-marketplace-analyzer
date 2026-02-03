import aioboto3
import asyncio
from typing import BinaryIO, Optional
from io import BytesIO
from backend.core.config import settings
import uuid


class S3Service:
    """Async S3/MinIO service for image storage."""
    
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint = settings.S3_ENDPOINT
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.bucket = settings.S3_BUCKET
        self.region = settings.S3_REGION
        self._bucket_created = False
    
    async def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists, create if it doesn't."""
        if self._bucket_created:
            return
        
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ) as client:
            try:
                await client.head_bucket(Bucket=self.bucket)
                self._bucket_created = True
            except Exception:
                # Bucket doesn't exist, create it
                try:
                    await client.create_bucket(Bucket=self.bucket)
                    self._bucket_created = True
                except Exception as e:
                    print(f"Error creating bucket: {e}")
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload a file to S3 and return the key."""
        await self._ensure_bucket_exists()
        
        # Generate unique key
        ext = filename.split('.')[-1] if '.' in filename else ''
        key = f"images/{uuid.uuid4()}.{ext}" if ext else f"images/{uuid.uuid4()}"
        
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ) as client:
            await client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_content,
                ContentType=content_type
            )
        
        return key
    
    async def download_file(self, key: str) -> bytes:
        """Download a file from S3."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ) as client:
            response = await client.get_object(Bucket=self.bucket, Key=key)
            async with response['Body'] as stream:
                return await stream.read()
    
    async def delete_file(self, key: str) -> None:
        """Delete a file from S3."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ) as client:
            await client.delete_object(Bucket=self.bucket, Key=key)
    
    async def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for a file."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        ) as client:
            url = await client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url


# Global S3 service instance
s3_service = S3Service()
