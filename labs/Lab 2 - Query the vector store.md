
#### Step 2: Query the vector store
1. Query the vector store with the user prompt, e.g. "Explain GitHub tokens and how to use them"
1. The script will return the document fragments from the vector store that are most similar to the query
1. The fragments and the user prompt are now send to the `gpt-4o-mini` model to generate a natural language response on the query, using the fragments found in the vector store
1. The model response is printed

See the script [local-script.py](../local-script.py) for the implementation.