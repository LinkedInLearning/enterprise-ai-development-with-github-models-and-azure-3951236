# Enterprise AI Development with GitHub Models and Azure
This is the repository for the LinkedIn Learning course Enterprise AI Development with GitHub Models and Azure. The full course is available from [LinkedIn Learning][lil-course-url].

## Getting started
To get started with this repositor, open it using a GitHub Codespace. It has all the tools you need to start working with the data and GitHub Models.

After opening the repository in a Codespace, you can run the following command to install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the script
To run the script, you can use the following command:

```bash
python script.py
```

## Local process
To run the embedding and inference steps on you local machine, start here. This will show you the basic moving parts.
The script will execute the following steps:

- Download and index the data: See [lab 1](/labs/Lab%201%20-%20Download%20and%20index%20the%20data.md)
- Query the vector store: See [lab 2](/labs/Lab%202%20-%20Query%20the%20vector%20store.md)

## Using Azure Resources
Now that we have seen the moving parts, we can start leveling up and run this with Azure resources.

- Use Azure Blob Storage to store the data: See [lab 3](/labs/Lab%203%20-%20Upload%20the%20data%20into%20blob%20storage.md)
- Use Azure Cognitive Services to create embeddings: See [lab 4](/labs/Lab%204%20-%20Create%20embeddings%20with%20Azure%20OpenAI.md)
- Use Azure Machine Learning to run the inference

### Running the scripts
1. Look at the scripts for the documented parameters on the top
1. Configure the necesary environment variables (also see `.env-example` that can be copied to `.env` and filled in)
1. Run the download of the dependencies with `pip install -r requirements.txt`
1. Run the scripts one by one with `python <script-name>.py`

### Extra information
All along the way, the most interesting durationss for each step is shown to give you an idea of the performance of the script.
At the end of the script, the used API requests to GitHub Models are printed, together with the information about the used tokens, as this is all dependent on the [rate limit for GitHub Models](https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits).