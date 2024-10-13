import os, time, dotenv, logging, sys, requests, subprocess
from openai import AzureOpenAI

def setup_local():
    """
    Sets up the environment and initializes the necessary models and logging.

    This function performs the following steps:
    1. Loads environment variables from a .env file.
    2. Checks if the `GITHUB_TOKEN` environment variable is set and raises a `ValueError` if not.
    3. Sets the `OPENAI_API_KEY` environment variable to the value of `GITHUB_TOKEN`.
    4. Sets the `OPENAI_BASE_URL` environment variable to the Azure inference URL.
    5. Configures logging to output to standard output with an INFO level by default.
    6. Initializes the OpenAI language model (`llm`) and embedding model (`embed_model`) with the specified API key and base URL.
    7. Assigns the initialized models to the `Settings` class attributes `llm` and `embed_model`.

    Raises:
        ValueError: If the `GITHUB_TOKEN` environment variable is not set.
    """
    # Load the environment variables
    dotenv.load_dotenv()

    # Check if the GITHUB_TOKEN is set
    if not os.getenv("GITHUB_TOKEN"):
        raise ValueError("GITHUB_TOKEN is not set")

    # Set the OPENAI_API_KEY to the GITHUB_TOKEN
    os.environ["OPENAI_API_KEY"] = os.getenv("GITHUB_TOKEN")
    os.environ["OPENAI_BASE_URL"] = "https://models.inference.ai.azure.com/"

    # Set up the logging
    logging.basicConfig(
        stream=sys.stdout, level=logging.INFO
    )  # change the logging.DEBUG for more verbose output
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    # Set up the LLM model configuration to use
    llm = OpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_BASE_URL"),
    )

    # Set up the embedding model configuration to use
    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_BASE_URL"),
    )

    Settings.llm = llm
    Settings.embed_model = embed_model

def get_github_rate_limit():
    """
    Sends a POST request to the OpenAI API to check if the provided API key is valid and retrieves rate limit information.

    The function sends a request to the OpenAI API endpoint for chat completions using the API key stored in the 
    environment variable 'OPENAI_API_KEY'. It checks the validity of the API key based on the response status code.
    If the API key is invalid, it raises a ValueError with the response text. If the API key is valid, it extracts 
    and prints the rate limit information from the response headers.

    Raises:
        ValueError: If the API key is not valid, with the response text as the error message.
    """
    # send a get request to the openai api to check if the api key is valid
    response = requests.post("https://models.inference.ai.azure.com/chat/completions", headers={
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }, json={
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions"
            },
            {
                "role": "user",
                "content": "What is the capital of the Netherlands?"
            }]
    })
    if response.status_code != 200:
        raise ValueError(f"OPENAI_API_KEY is not valid: {response.text}")
    else:
        # Extract headers into a dictionary
        headers_dict = {header: value for header, value in response.headers.items()}
        remaining_tokens = headers_dict.get('x-ratelimit-remaining-tokens')
        remaining_requests = headers_dict.get('x-ratelimit-remaining-requests')
        print(f"Ratelimit remaining tokens: {remaining_tokens}")
        print(f"Ratelimit remaining requests: {remaining_requests}")

        return int(remaining_tokens), int(remaining_requests)

def log_duration(start_time, message):
    """
    Logs the duration of an operation in milliseconds.

    Args:
        start_time (float): The start time of the operation, typically obtained from time.time().
        message (str): A message describing the operation.

    Prints:
        A message indicating the duration of the operation in milliseconds.
    """
    duration = round((time.time() - start_time) * 1000)
    print(f"{message} took [{duration}] ms")
    print()

def get_blogging_directory():
    """
    Ensures the blogging directory is present and up-to-date.

    This function performs the following steps:
    1. Checks if the "blog" directory exists.
    2. If the directory does not exist, it clones the blogging repository from GitHub.
    3. If the directory exists but is older than 24 hours, it pulls the latest changes from the repository.
    4. Displays the size of the files in the "_posts" subdirectory of the blogging directory.

    Returns:
        str: The path to the "_posts" subdirectory within the blogging directory.
    """
    # Create a new directory to clone the repository
    blogging_directory = "blog"
    if not os.path.exists(blogging_directory):
        print("Cloning the blogging repository")
        os.makedirs(blogging_directory)
        # Clone the blogging repository from github.com/rajbos/rajbos.github.io
        os.system(
            f"git clone https://github.com/rajbos/rajbos.github.io.git {blogging_directory}"
        )
    else:
        # check if the directory is more then 24 hours old
        if os.path.getmtime(blogging_directory) < time.time() - 60 * 60 * 24:
            print("Pulling the latest changes from the blogging repository")
            os.system(f"cd {blogging_directory} && git pull")

    # show the size of the files in the persist_dir
    blogging_directory = f"{blogging_directory}/_posts/"
    print("Size of the blogging directory:")
    os.system(f"du -shc {blogging_directory}")
    show_files_in_directory(blogging_directory, "files in the blogging directory")
    return blogging_directory

def show_files_in_directory(directory, message):
    """
    Displays the number of files in the specified directory along with a custom message.

    Args:
        directory (str): The path to the directory whose files are to be counted.
        message (str): The custom message to be displayed alongside the file count.

    Returns:
        None
    """
    nr_of_files = subprocess.run(f"ls -1 {directory} | wc -l", shell=True, capture_output=True, text=True)
    print(f"{nr_of_files.stdout.strip()} {message}")

def get_index(blogging_directory): 
    """
    Generates or loads an index from a specified blogging directory.

    This function checks if a persistent directory for the index exists. If it does not exist,
    it loads data from the specified blogging directory, creates a new index, and persists it.
    If the persistent directory exists, it rebuilds the storage context from the directory and
    loads the index from storage.

    Args:
        blogging_directory (str): The path to the directory containing blog posts.

    Returns:
        index: The generated or loaded index.
    """
    persist_dir="blog_index"
    if not os.path.exists(persist_dir):
        print("Loading the data from the blogposts and create the index")
        startTime = time.time()
        documents = SimpleDirectoryReader(f"{blogging_directory}").load_data()
        index = VectorStoreIndex.from_documents(documents) # decrease batch size if needed for ratelimiting, insert_batch_size=150)
        log_duration(startTime, "Indexing")
                
        print("Persisting the index to the folder")
        startTime = time.time()
        # Persist the index to the folder
        index.storage_context.persist(persist_dir)
        log_duration(startTime, "Persisting")
        # show the size of the files in the persist_dir
        print("Size of the persisted directory:")
        os.system(f"du -sh {persist_dir}/*")
        show_files_in_directory(persist_dir, "files in the persist directory")
    else:
        print("Rebuilding storage context from directory")
        startTime = time.time()
        storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore.from_persist_dir(persist_dir),
            vector_store=SimpleVectorStore.from_persist_dir(persist_dir),
            index_store=SimpleIndexStore.from_persist_dir(persist_dir),
        )
        index = load_index_from_storage(storage_context)
        log_duration(startTime, "Rebuilding storage context")
        # show the size of the files in the persist_dir
        print("Size of the persist directory:")
        os.system(f"du -sh {persist_dir}/*")
        show_files_in_directory(persist_dir, "files in the persist directory")
    return index

def get_documents(fragments, index, blogging_directory):
    # Load the documents that contain the fragments
    documents = []
    for fragment in fragments:
        # Find the document based on the node_id
        document = index.storage_context.docstore.get_document(fragment.node_id)
        if document:
            # find the file name from this document
            file_name = document.metadata.get("file_name")
            print(f"> Document with [{fragment.node_id}] was found in file [{file_name}]. Fragment relevance score: {round(fragment.score, 2)}")
            #print(f"> Fragment content: {fragment.text}")
            documents.append(file_name)
        else:
            print(f"[ERROR] Document with {fragment.node_id} was not found")

    # Deduplicate the documents
    documents = list(set(documents))
    print()
    print(f"Found [{len(documents)}] documents that match the question:")

    # Load the content of the documents
    documents_content = []
    for document in documents:
        # check if the file exists to prevent errors
        if not os.path.exists(f"{blogging_directory}{document}"):
            print(f"- [ERROR] File [{blogging_directory}{document}] does not exist")
            continue

        # Load the file from the documents directory
        with open(f"{blogging_directory}{document}", "r") as file:
            content = file.read()
            documents_content.append(content)

        # Load the information from the content to show a reference
        date = parse_blog_header_date(content)
        url = convert_filename_to_url(document, date, "https://devopsjournal.io/blog")
        print(f"\t- File: [{blogging_directory}{document}] which leads to [{url}]")

        return documents_content


def convert_filename_to_url(document, date, base_url):
    """
    Converts a filename to a blog URL.

    Args:
        document (str): The file path of the document. Example: 'blog/_posts//2022-10-09-Enabling-GitHub-Actions-on-Enterprise-Server.md'.
        date (str): The date in the format 'Date: yyyy-mm-dd'. Example: 'Date: 2022-10-09'.
        base_url (str): The base URL of the blog. Example: 'https://devopsjournal.io'.

    Returns:
        str: The constructed blog URL. Example: 'https://devopsjournal.io/blog/2022/10/09/Enabling-GitHub-Actions-on-Enterprise-Server'.
    """
    # convert the filename to the blog url
    # file_name example: blog/_posts//2022-10-09-Enabling-GitHub-Actions-on-Enterprise-Server.md
    # actual blog url example: https://devopsjournal.io/blog/2022/10/08/Enabling-GitHub-Actions-on-Enterprise-Server
    file_name = document.split("/")[-1]
    file_name = file_name.replace(".md", "")
    # get the three date fields in the file name
    parts = file_name.split("-")
    year, month, day = parts[:3]
    title = "-".join(parts[3:])
    # remove the date from the filename
    file_name = file_name.replace(f"{year}-{month}-{day}-", "")
    # insert the date from the file itself in yyyy/mm/dd format
    # get year from date
    year = date.split(": ")[1].split("-")[0]
    month = date.split(": ")[1].split("-")[1]
    day = date.split(": ")[1].split("-")[2]
    # insert the date in the file name
    file_name = f"{year}/{month}/{day}/{file_name}"    
    return f"{base_url}/{file_name}"

def parse_blog_header_date(content):
    """
    Parses the date from the header of a blog post.

    The header is expected to be in the following format:
    ---
    layout: post
    title: "Blog Post Title"
    date: YYYY-MM-DD
    tags: [tag1, tag2, ...]
    ---
    blog content...

    Args:
        content (str): The content of the blog post including the header.

    Returns:
        str: The date string in the format 'YYYY-MM-DD' extracted from the header.

    Raises:
        IndexError: If the date field is not found in the header.
    """
    header = content.split("---")[1]
    header = header.split("\n")
    header = [line.strip() for line in header if line.strip()]
    # find the date tag
    try:
        date = [line for line in header if line.startswith("date")][0]
    except IndexError:
        date = None  # or you can use a default value or message
    return date

def call_model_with_context(user_prompt, context, prompt_log_message, log_duration_message):
    print()
    startTime = time.time()
    
    # Prepare the prompt messages with the context data
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant that answers some questions with the help of some context data.\n\nHere is the context data:\n\n" + context),
        ChatMessage(role="user", content=user_prompt)
    ]

    print(f"Calling the model with the following prompt: [{user_prompt}] {prompt_log_message}")
    response = Settings.llm.chat(messages)
    print()
    for line in response.message.content.splitlines():
        print(f"\t{line}")
    print()
    ratelimit_info = response.additional_kwargs
    print(f"{ratelimit_info["total_tokens"]} tokens used")
    log_duration(startTime, log_duration_message)

def setup_azure_client():
    """
    Sets up and initializes an Azure OpenAI client using environment variables for configuration.
    Environment Variables:
    - ENDPOINT_URL: The endpoint URL for the Azure OpenAI service (default: "https://xms-openai.openai.azure.com/").
    - DEPLOYMENT_NAME: The deployment name for the Azure OpenAI service (default: "gpt-4o").
    - SEARCH_ENDPOINT: The endpoint URL for the Azure AI Search service (default: "https://xms-azure-search.search.windows.net").
    - SEARCH_KEY: The admin key for the Azure AI Search service (default: "put your Azure AI Search admin key here").
    - SEARCH_INDEX_NAME: The index name for the Azure AI Search service (default: "vector-1727189048533").
    - AZURE_OPENAI_API_KEY: The subscription key for the Azure OpenAI service.
    Raises:
    - ValueError: If the ENDPOINT_URL or AZURE_OPENAI_API_KEY environment variables are not set.
    Returns:
    - AzureOpenAI: An initialized Azure OpenAI client with key-based authentication.
    """
    dotenv.load_dotenv()
    endpoint = os.getenv("ENDPOINT_URL", "https://xms-openai.openai.azure.com/")
    deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    search_endpoint = os.getenv("SEARCH_ENDPOINT", "https://xms-azure-search.search.windows.net")
    search_key = os.getenv("SEARCH_KEY", "put your Azure AI Search admin key here")
    search_index = os.getenv("SEARCH_INDEX_NAME", "vector-1727189048533")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

    # validate the endpint and API Key
    if not endpoint:
        raise ValueError("ENDPOINT_URL is not set")
    
    if not subscription_key:
        raise ValueError("AZURE_OPENAI_API_KEY is not set")
    
    # Show the info we got
    print(f"Endpoint: [{endpoint}] and lenght of the key: [{len(subscription_key)}]")
    print(f"Using [{search_index}] with key length [{len(search_key)}] and endpoint [{search_endpoint}]")

    # Initialize Azure OpenAI client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint = endpoint,
        api_key = subscription_key,
        api_version = "2024-05-01-preview",
    )

    return client, deployment, search_endpoint, search_key, search_index