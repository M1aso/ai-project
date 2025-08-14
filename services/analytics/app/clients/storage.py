from pathlib import Path


class StorageClient:
    def __init__(self, base_path: str = "storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload_bytes(self, data: bytes, object_name: str) -> str:
        path = self.base_path / object_name
        path.write_bytes(data)
        return str(path)

    def presigned_get(self, object_name: str) -> str:
        path = self.base_path / object_name
        return path.as_uri()
