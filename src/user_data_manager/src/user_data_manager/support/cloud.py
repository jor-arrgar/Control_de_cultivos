import os

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient 

from lib.support import SingletonMeta


# MARK: Azure - main
class AzureCloudManager():

    def __init__(self):

        super().__init__()

        self.credential = DefaultAzureCredential()


# MARK: Azure Storage
class AzureBlobStorageManager(AzureCloudManager, metaclass=SingletonMeta):

    value = 0
    account_url = os.getenv('ACCOUNT_URL')

    def __init__(self):
        super().__init__()

        self.blob_service_client = BlobServiceClient(
            account_url=self.account_url,
            credential=self.credential
            )

    def download_blob(self, container_name: str, blob_path: str) -> bytes:
        """Download a blob from a container as raw bytes."""
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        blob_data = blob_client.download_blob()
        return blob_data.readall()

    def upload_blob(self, container_name: str, blob_path: str, data: bytes | str):
        """Upload bytes or text content to a blob path within a container."""
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)

        if isinstance(data, str):
            data = data.encode("utf-8")

        blob_client.upload_blob(data, overwrite=True)
        return blob_client.url

    def create_container(self, container_name: str):
        """Create a new container in the storage account."""
        return self.blob_service_client.create_container(name=container_name)

    def get_blobs_list(self, container_name: str, path: str | None = None):
        """List blobs in a container, optionally filtered to a specific folder path."""
        container_client = self.blob_service_client.get_container_client(container_name)

        if path is None:
            return list(container_client.list_blobs())

        folder_path = path.strip("/")
        if folder_path:
            folder_path = f"{folder_path}/"

        return list(container_client.list_blobs(name_starts_with=folder_path))






    