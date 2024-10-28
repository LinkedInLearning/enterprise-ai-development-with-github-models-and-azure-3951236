"""
    This script is going to upload the blogposts from the downloaded blog repository to an Azure Blob Storage.

    See the documentation for Lab 3 for more details.
"""
import os
from azure.storage.blob import BlobServiceClient
from utils import get_blogging_directory

# Check if the AZURE_STORAGE_CONNECTION_STRING is set
if not os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set")

# Main code
blogging_directory = get_blogging_directory()
# push the blogging directory into an Azure Blob Storage
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = "blogposts"
container_client = blob_service_client.get_container_client(container_name)

# Iterate over files in the blogging directory and upload each one
for root, dirs, files in os.walk(blogging_directory):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        blob_client = container_client.get_blob_client(file_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)
        print(f"Uploaded {file_name} to the Azure Blob Storage")

print("Uploaded all blogposts to the Azure Blob Storage")
