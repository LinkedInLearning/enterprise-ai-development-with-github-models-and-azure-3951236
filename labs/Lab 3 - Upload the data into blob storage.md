#### Step 3: Upload the data to Azure blob storage

In this lab we are going to use Azure Blob Storage to store the data, so that Azure AI Search can use it for indexing and querying. Azure AI search can work with different sources, index them, and then run the queries on the indexed data. Since we already have markdown files from lab 1, we can upload those files into Azure Blob Storage.

See the implementation in the script [upload-data.py](../upload-data.py).
