import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


class VaultManager():
    
    def __init__(self, keyVaultName):
        
        KVUri = f"https://{keyVaultName}.vault.azure.net"
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=KVUri, credential=credential)
        
        
    def set_secret(self, secret_name, secret_value):
        
        self.client.set_secret(secret_name, secret_value)
        
    def get_secret(self, secret_name):
        
        retrieved_secret = self.client.get_secret(secret_name)
        
        return retrieved_secret
    
    def delete_secret(self, secret_name):
        
        poller = self.client.begin_delete_secret(secret_name)
        deleted_secret = poller.result()
        
        return deleted_secret