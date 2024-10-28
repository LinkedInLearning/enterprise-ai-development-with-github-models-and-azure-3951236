#### Step 4: Create a vector search index with Azure OpenAI

Azure OpenAI offers a service to create, store, and manage embeddings and vectors for you. This is available through Azure AI Search.

## Steps:
- Create an Azure OpenAI resource
- Deploy a ChatGPT model in it for the model to use
- Deploy an embedding model to use to create the vector store and fill it with the embeddings
- Create an Azure AI Search index
- Fill the search index using the "Import and vectorize data" button
  - Select the Blob storage account and container
  - Skip the vectorization of images step as we're not going to use it
