# Legal Analysis App

## Overview
The Legal Analysis App is designed to assist legal professionals, students, and the 
public in understanding complex legal scenarios by providing instant analysis based 
on user queries. Utilizing the Retrieval Augmented Generation (RAG) methodology, this
application is connected with all published cases from 1947 to 2022. The RAG framework 
connects with the vectors of case laws and generates a legal analysis based on the semantic 
search results.
![RAG Workflow](images/legal_app_workflow.png)


## Key Features
- **Advanced Query Understanding**: Leverages natural language processing to interpret complex legal questions accurately.
- **RAG-Powered Responses**: Combines powerful retriever models to fetch relevant legal documents and a generator model to synthesize responses that are both accurate and contextually relevant.
- **Comprehensive Legal Database**: Accesses an extensive database of legal documents, cases, and precedents.
- **User-Friendly Interface**: Simple and intuitive interface ensuring ease of use for all users regardless of their technical expertise.


## Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- OpenAI API Key
- Docker

## Setup for backend
The backend consists of two major components:
- **Vector + NoSQL Databse**
- **Semantic search API**

### Database
The NoSQL database is created to store and organize a large collection of legal judgments and related metadata, collected from many legal sources across Pakistan. These sources are essential for providing detailed legal information regarding different court decisions. The main sources of the data include:
- [Supreme Court of Pakistan](https://www.supremecourt.gov.pk/)
- [Sindh High Court](https://caselaw.shc.gov.pk/caselaw/public/home)
- [Islamabad High Court](https://mis.ihc.gov.pk/)
- [Lahore High Court](https://www.lhc.gov.pk/)
- [Peshawar High Court](https://www.peshawarhighcourt.gov.pk/PHCCMS/reportedJudgments.php)
- [Balochistan High Court](https://portal.bhc.gov.pk/judgments/)
- [Azad Jammu Kashmir High Court](https://ajkhighcourt.gok.pk/Userside/Judgement)
- [Federal Shariat Court](https://www.federalshariatcourt.gov.pk/alljud.php)

To build the NoSQL database, data from the specified legal sources need to be extracted and stored in MongoDB. Additionally, a separate VectorDB should be created, which will hold the vector embeddings of these judgments along with a unique ID. This ID will match the ID assigned to each case in MongoDB, ensuring a consistent link between the databases. The vector embeddings are generated using the [Instructor-xl](https://huggingface.co/hkunlp/instructor-xl) model from Hugging Face, which is designed to create meaningful representations of the text data.

### API
To set up the semantic API for the legal analysis application, you need to configure the connection settings in the `api.py` file, located at `legal_analysis_app\backend\api.py`. Follow these steps to complete the configuration:

**MongoDB Connection**: Insert the MongoDB connection URL to connect to your database. This URL should be placed in the `api.py` file as follows:
```python
url = '' #enter your mongo URL
```
Replace `''` with your actual MongoDB connection string.

**Elasticsearch Credentials**: Provide the credentials for Elasticsearch to enable text search and indexing capabilities. Update the cred variable in the `api.py` file:
```python
cred = ""
```
Replace `""` with your Elasticsearch credentials.

## Setup for Frontend
The Frontend can be run alone to experience the look and feel of the app and if you want to connect the frontend to the backend then follow the [Setup for backend](#setup-for-backend)
### Setup
Clone the repository to your local machine:
```bash
git clone https://theaisystems-private@github.com/theaisystems/legal_analysis_app.git
cd legal_analysis_app\frontend
```

### Configuration
Before running the application, you must configure a few settings in the `config.py` file. This file contains essential configuration details such as the OpenAI API key and the port number on which the app will run.

### Setting Up `config.py`
1. **OpenAI API Key**: The application requires an API key from OpenAI to access language models for processing legal queries.
   - Obtain an API key from [OpenAI](https://platform.openai.com/api-keys).
   - Open the `config.py` file located in the root directory of this project.
   - Find the line `apiKey = 'enter-your-api-key'` and replace 'enter-your-api-key' with your actual OpenAI API key.

2. **Port Number**: The port number determines where your application will be accessible on your local machine.
   - Choose a port number that is not in use by other applications.
   - In the `config.py` file, locate the line `port = 9010`.
   - Replace `9010` with your desired port number if 9010 already in use or if you prefer a different port.

### Example `config.py`
Here's what your `config.py` might look like after you've added your configurations:

### `config.py` 
```python
apiKey = 'sk-4b1c3D2EfGH567ijK890LMnOp12qrST3uvWXyz45678'
port = 9010  # Default port, change this if needed
```

## Running the app
Navigate to the folder where Docker Compose file is present and run the command by setting the container and image name of your choice. Use the same port as defined in 
the `config.py` file which is "9010"
```bash
docker build . --tag <name_of_docker_image> 
docker run -p 9010:9010 --name <name_of__docker_container> <name_of_docker_image>

```

## Live App

Live experience of the app can be experienced on https://legalanalysis-app.azurewebsites.net
