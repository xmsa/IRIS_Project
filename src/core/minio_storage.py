from typing import Iterator, List

from minio import Minio
from minio.datatypes import Bucket, Object
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
        """Create and return MinIO client"""
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

    def list_buckets(self) -> List[str]:
        """List all buckets and return their names"""
        try:
            buckets: List[Bucket] = self.client.list_buckets()
            bucket_names: List[str] = [bucket.name for bucket in buckets]
            minio_logger.debug(f"Found {len(bucket_names)} buckets")
            return bucket_names
        except S3Error as e:
            minio_logger.error(f"Failed to list buckets: {e}", exc_info=True)
            return []

    def check_connection(self) -> bool:
        """Check if MinIO connection is working"""
        try:
            # Try to list buckets as a connection test
            self.client.list_buckets()
            minio_logger.info("✅ MinIO connection check successful")
            return True
        except Exception as e:
            minio_logger.error(f"❌ MinIO connection check failed: {e}")
            return False

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete a bucket

        Args:
            bucket_name: Name of the bucket to delete
            force: If True, delete all objects in bucket first
        """
        if not self.bucket_exists(bucket_name):
            app_logger.warning(f"Bucket '{bucket_name}' does not exist")
            return False

        try:
            if force:
                # Delete all objects in bucket first
                objects: Iterator[Object] = self.client.list_objects(
                    bucket_name, recursive=True)
                for obj in objects:
                    if obj.object_name is None:
                        continue
                    self.client.remove_object(bucket_name, obj.object_name)
                app_logger.info(
                    f"🗑️  Removed all objects from bucket '{bucket_name}'")

            self.client.remove_bucket(bucket_name)
            app_logger.info(f"🗑️  Bucket deleted: {bucket_name}")
            return True
        except S3Error as e:
            minio_logger.error(
                f"Failed to delete bucket '{bucket_name}': {e}",
                exc_info=True
            )
            return False


minio_storage = MinIOStorage()
app_logger.info("MinIO storage instance created successfully")
