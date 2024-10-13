"""
    This script will call the Azure OpenAI model to generate the answer to a specific question based on the context of the that we uploaded to Azure AI Index.
"""

import sys, time, json
from utils import setup_azure_client, get_github_rate_limit

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

    # Set up the Azure OpenAI connection
    client, deployment, search_endpoint, search_key, search_index = setup_azure_client()

    startTime = time.time()
    start_remaining_tokens = 0
    start_remaining_requests = 0
        
    # Get the completion from the Azure OpenAI model
    completion = client.chat.completions.create(
        model=deployment,
        messages= [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people find information in the given documents."
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ],
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    ,
        extra_body={
        "data_sources": [{
            "type": "azure_search",
            "parameters": {
                "endpoint": search_endpoint,
                "index_name": search_index,
                "semantic_configuration": "default",
                "query_type": "simple",
                "fields_mapping": {},
                "in_scope": True,
                "role_information": "You are an AI assistant that helps people find information.",
                "filter": None,
                "strictness": 3,
                "top_n_documents": 5,
                "authentication": {
                    "type": "api_key",
                    "key": search_key
                }
            }
            }]
        })

    #print(completion.to_json())
    # loop over the completion.choices and show the answer
    for choice in completion.choices:
        print()
        print("Answer:")
        # break up the answer in lines
        for line in choice.message.content.splitlines():
            print(f"\t{line}")
        print()
        print("Citations:")
        citations = choice.message.context.get('citations', [])
        i=0
        for citation in citations:
            i+=1
            print(f"\t[doc{i}] - {citation.get('title')}")

    print()
    print("Token usage:")
    print(completion.usage.to_json())