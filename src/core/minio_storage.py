from typing import List

from minio import Minio
from minio.error import S3Error

from .logger import app_logger, minio_logger
from .settings import MinIOSettings, minio_settings


class MinIOStorage:
    """Connector for MinIO/S3 operations"""

    def __init__(
        self,
        settings: MinIOSettings = minio_settings
    ) -> None:
        self._settings: MinIOSettings = settings
        self.client: Minio = self.__client_maker(self._settings)
        app_logger.info(
            f"MinIO client initialized with endpoint: {settings.endpoint}"
        )

    def __client_maker(self, settings: MinIOSettings) -> Minio:
        try:
            client = Minio(
                settings.endpoint,
                access_key=settings.access_key,
                secret_key=settings.get_secret_key,
                secure=settings.secure
            )
            minio_logger.debug("MinIO client created successfully")
        except Exception as e:
            minio_logger.error(f"Failed to connect to MinIO: {e}")
            raise e

        return client

    def setup_buckets(self) -> None:
        """Create all buckets if they don't exist"""
        app_logger.info("Starting bucket setup...")
        for bucket in self._settings.buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                app_logger.info(f"Bucket created: {bucket}")
            else:
                app_logger.info(f"Bucket exists: {bucket}")
        app_logger.info("Bucket setup completed")

    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if bucket exists"""
        try:
            exists: bool = self.client.bucket_exists(bucket_name)
            minio_logger.debug(f"Bucket '{bucket_name}' exists: {exists}")
            return exists
        except S3Error as e:
            minio_logger.error(
                f"Error checking bucket '{bucket_name}': {e}",
                exc_info=True
            )
            return False

    def create_bucket(self, bucket_name: str) -> bool:
        """Create bucket if not exists"""
        if self.bucket_exists(bucket_name):
            app_logger.info(f"Bucket '{bucket_name}' already exists")
            return True
        try:
            self.client.make_bucket(bucket_name)
            app_logger.info(f"Bucket created: {bucket_name}")
            return True
        except S3Error as e:
            minio_logger.error(
                f"Failed to create bucket '{bucket_name}': {e}",
                exc_info=True
            )
            return False

    def list_buckets(self) -> List:
        return self.client.list_buckets()


minio_storage = MinIOStorage()
app_logger.info("MinIO storage instance created successfully")
