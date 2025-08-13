import os
from urllib.parse import quote


class MinioClient:
    def __init__(self, endpoint: str, bucket: str):
        self.endpoint = endpoint
        self.bucket = bucket

    def presign_put(self, key: str, content_type: str) -> str:
        return f"https://{self.endpoint}/{self.bucket}/{quote(key)}?content-type={quote(content_type)}"

    def file_url(self, key: str) -> str:
        return f"https://{self.endpoint}/{self.bucket}/{quote(key)}"


def default_client() -> MinioClient:
    return MinioClient(
        os.getenv("MINIO_ENDPOINT", "minio"),
        os.getenv("MINIO_BUCKET", "avatars"),
    )
