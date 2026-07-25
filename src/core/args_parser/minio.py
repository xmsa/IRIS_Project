

from typing import List, Optional

import click

from core.minio_storage import MinIOStorage

from .base import BaseCommand


class MinioCommand(BaseCommand):
    """Handle MinIO storage commands"""

    def register(self, cli_group: click.Group) -> None:
        @cli_group.command()
        @click.option('--summary', is_flag=True, help='Show MinIO settings summary')
        @click.option('--check', is_flag=True, help='Check MinIO connection')
        @click.option('--create-bucket', help='Create a bucket with specified name')
        @click.option('--list-buckets', is_flag=True, help='List all buckets')
        @click.option('--delete-bucket', help='Delete a bucket with specified name')
        def minio(summary: bool, check: bool, create_bucket: Optional[str],
                  list_buckets: bool, delete_bucket: Optional[str]) -> None:
            self.execute(
                summary=summary,
                check=check,
                create_bucket=create_bucket,
                list_buckets=list_buckets,
                delete_bucket=delete_bucket
            )

    def execute(self, summary: bool = False,
                check: bool = False,
                create_bucket: Optional[str] = None,
                list_buckets: bool = False,
                delete_bucket: Optional[str] = None) -> None:

        if summary:
            self._handle_summary(self.settings.minio, "MinIO")
            return

        if not any([check, create_bucket, list_buckets, delete_bucket]):
            click.echo(
                "ℹ️  Please specify an action. Use --help for more information.")
            return

        from core.minio_storage import minio_storage
        if check:
            try:
                if minio_storage.check_connection():
                    click.echo("✅ MinIO connection successful")
                else:
                    click.echo("❌ MinIO connection failed")
            except Exception as e:
                click.echo(f"❌ MinIO connection error: {e}")

        if create_bucket:
            self._create_bucket(minio_storage, create_bucket)

        if list_buckets:
            self._list_buckets(minio_storage)

        if delete_bucket:
            self._delete_bucket(minio_storage, delete_bucket)

    def _create_bucket(self, minio_storage: MinIOStorage, bucket_name: str) -> None:
        """Create a new bucket"""
        try:
            minio_storage.create_bucket(bucket_name)
            click.echo(f"✅ Bucket '{bucket_name}' created successfully")
        except Exception as e:
            click.echo(f"❌ Failed to create bucket: {e}")

    def _list_buckets(self, minio_storage: MinIOStorage) -> None:
        """List all buckets"""
        try:
            buckets: List[str] = minio_storage.list_buckets()
            if buckets:
                click.echo("📦 Available buckets:")
                for bucket in buckets:
                    click.echo(f"  - {bucket}")
            else:
                click.echo("ℹ️  No buckets found")
        except Exception as e:
            click.echo(f"❌ Failed to list buckets: {e}")

    def _delete_bucket(self, minio_storage: MinIOStorage, bucket_name: str) -> None:
        """Delete a bucket"""
        try:
            result: bool = minio_storage.delete_bucket(bucket_name)
            if result:
                click.echo(f"✅ Bucket '{bucket_name}' deleted successfully")
        except Exception as e:
            click.echo(f"❌ Failed to delete bucket: {e}")
