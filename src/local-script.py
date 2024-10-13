import sys, requests, time, os, json
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from llama_index.core import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core import load_index_from_storage
from utils import call_model_with_context, get_documents, setup, get_blogging_directory, get_index, log_duration, parse_blog_header_date, convert_filename_to_url, get_github_rate_limit

# Main script
if __name__ == "__main__":
    """
    This script is going to retrieve the documents that contain the fragments that answer a specific question.
    It is going to use the OpenAI model to generate the answer based on the either the context of the fragments or the entire content of the documents.

    The script is going to use the following command line parameters:
    - The question to be answered, e.g. python script.py "How can you use GitHub Actions with security in mind?"
    - A flag to run with the entire content of the documents, e.g. python script.py "How can you use GitHub Actions with security in mind?" True
    """

    # read the user prompt from the command line parameters
    default_user_prompt = "How can you use GitHub Actions with security in mind?"
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else default_user_prompt
    # prevent issue when the user prompt is not given, but only the flag
    if user_prompt == "True":
        user_prompt = default_user_prompt
    # if there is a second argument, we are going to run with the entire content of the documents instead of the fragments
    run_with_documents = len(sys.argv) > 2

    # Set up the environment and initialize the models
    setup()

    # Check the current rate limit of using GitHub Models
    start_remaining_tokens, start_remaining_requests = get_github_rate_limit()

    # Get the blogging directory
    blogging_directory = get_blogging_directory()

    # Get the index
    index = get_index(blogging_directory)

    startTime = time.time()
    
    # Get the retriever from the index
    retriever = index.as_retriever()
    print()

    # Retrieve the fragments that match the question
    fragments = retriever.retrieve(f"Find the documentens that answer the question: {user_prompt}")
    log_duration(startTime, "Retrieval")

    # Get the documents that contain the fragments
    documents_content = get_documents(fragments, index, blogging_directory)

    if run_with_documents:
        # Join the documents_content list into a single string
        documents_content_str = "\n------\n".join(documents_content)
        call_model_with_context(user_prompt, documents_content_str, "and the context in all file content", "Model call")
    else:
        # Join the fragments into a single context string
        context = "\n------\n".join([ fragment.text for fragment in fragments ])
        call_model_with_context(user_prompt, context, "and the context in all fragments", "Model call")
    
    # Check the remaining rate limits
    remaining_tokens, remaining_requests = get_github_rate_limit()
    # show the used tokens and requests
    print(f"Total tokens used: {start_remaining_tokens - remaining_tokens}")
    print(f"Total requests used: {start_remaining_requests - remaining_requests}")
