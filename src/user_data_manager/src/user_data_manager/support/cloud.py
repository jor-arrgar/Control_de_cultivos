import os
import struct
import logging
from time import sleep

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient 
from sqlalchemy import create_engine, event, text


from support.support import SingletonMeta


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


# MARK: Azure SQL
class AzureSQLManager(AzureCloudManager, metaclass=SingletonMeta):

    SQL_COPT_SS_ACCESS_TOKEN = 1256
    TOKEN_SCOPE = "https://database.windows.net/.default"


    status = None

    def __init__(self):
        super().__init__()

        self.engine = self.get_engine()


    def get_engine(self):

        logging.warning("=> Creating Azure SQL engine...")
        engine = create_engine(
                    os.getenv('SQL_CONNSTRING'),
                    pool_pre_ping=True
                )

        # Inyectar el token de Microsoft Entra ID
        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):

            # SQLAlchemy añade Trusted_Connection automáticamente
            cargs[0] = cargs[0].replace(
                ";Trusted_Connection=Yes", ""
            )

            # Obtener token usando la sesión de az login
            token = self.credential.get_token(self.TOKEN_SCOPE).token

            # Codificación requerida por el driver ODBC
            token_bytes = token.encode("utf-16-le")

            token_struct = struct.pack(
                f"<I{len(token_bytes)}s",
                len(token_bytes),
                token_bytes
            )

            cparams["attrs_before"] = {
                self.SQL_COPT_SS_ACCESS_TOKEN: token_struct
            }

        logging.warning("=> Testing Azure SQL connection...")
        # Probar conexión
        try:
            with engine.connect() as connection:
                result = connection.execute(
                    text("SELECT SYSTEM_USER, DB_NAME()")
                )
                if len(result.fetchall()) == 0:
                    logging.error("=> Error connecting to Azure SQL Database: No results returned.")
                    return None
            logging.warning("=> Azure SQL connection successful.")
            return engine

        except Exception as e:
            if e.args[0] == 'HYT00':
                logging.error("=> Error connecting to Azure SQL Database: Connection timed out. Waiting 10 seconds before retrying...")
                try:
                    sleep(10)
                    with engine.connect() as connection:
                        result = connection.execute(
                            text("SELECT SYSTEM_USER, DB_NAME()")
                        )
                        if len(result.fetchall()) == 0:
                            logging.error("=> Error connecting to Azure SQL Database: No results returned.")
                            return None
                    logging.warning("=> Azure SQL connection successful on retry.")
                    return engine
                except Exception as retry_e:
                    logging.error(f"=> Error connecting to Azure SQL Database on retry: {retry_e}")
                    self.status = e
                    return None
            logging.error(f"=> Error connecting to Azure SQL Database: {e}")
            self.status = e
            return None

        

    