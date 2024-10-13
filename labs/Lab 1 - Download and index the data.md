
#### Step 1: Download and index the data
1. Download the data from my blogging repository at https://github.com/rajbos/rajbos.github.io
1. The data size from the repository is printed
1. Load the data using the LLamaIndex SDK from a folder in the blogging repository, into a VectorStoreIndex
1. Use the `text-embedding-3-small` OpenAI model from the GitHub Models to create embeddings for the data
1. Persists the embeddings in the `blog_index` folder to retrieve for the next run (if needed)
1. After persisting, the size of the new folder is printed

See the script [local-script.py](../local-script.py) for the implementation.
