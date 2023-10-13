# 538Bot

## Purpose

538bot is designed to answer student questions about course content based on lecture recordings.
The functionality of the app is quite limited.
1. It adds new audio to the datastore
2. It answers questions based on the datastore

The bot leverages `whisper` (Openai) for transcription and `langchain` for question answering.

538bot's additional details can be found in [Project Description.md](https://github.com/kpister/538bot/blob/trunk/Project%20Description.md)

### Install

`brew install ffmpeg`

`pip install -r requirements.txt`

### Run

- **Transcribe audio in \<audio file\> and put the result in \<transcription folder\>**
  
      python bot.py --audio_filename <audio file> --transcription_folder <transcription folder>

- **Create a vector database named \<vector database\> using text files in \<transcription folder\>**

      python chain.py --transcription_folder <transcription folder> --cache_dir <vector database>

- **Answer \<question\> using context from \<vector database\>**
  
      python bot.py --question <question> --cache_dir <vector database>

- **Answer questions on Piazza**
  
    The subject of a Piazza post will be a question while the content of that question currently has to be "gpt." This question will be answered using context from \<vector database\>
  
      python main.py --email <Piazza username> --password <Piazza password> --network_id <Piazza course id> --openai_api_key <OpenAI api key> --cache_dir <vector database>
  
    TODO: Automatically detect Piazza posts that will be answered by this program (Currently, that post has to be manually picked.)

- **Write Piazza posts and their replies to \<Piazza post file\>**
  
    Besides lecture transcriptions, Piazza posts and their replies might be used as context for answering questions since they usually contain Q&As between students and teachers/TAs. 
  
      python fetch_piazza.py --email <Piazza username> --password <Piazza password> --network_id <Piazza course id> --post_file_name <Piazza post file>
