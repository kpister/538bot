# 538Bot

## Purpose

538bot is designed to answer student questions about course content based on lecture recordings.
The functionality of the app is quite limited.
1. It adds new audio to the datastore
2. It answers questions based on the datastore

The bot leverages `whisper` (Openai) for transcription and `langchain` for question answering.

### Install

`brew install ffmpeg`

`pip install -r requirements.txt`

### Run

Audio Transcription
`python bot.py --audio_filename <audio file> --transcription_folder <transcription folder>`

Answer question
`python bot.py --question <question> --cache_folder <vector database>`

Answer question on Piazza (currently, the content of that question has to be "gpt")
`python main.py --email <Piazza username> --password <Piazza password> --network_id <Piazza course id> --openai_api_key <OpenAI api key>`
TODO: Automatically detect Piazza posts that want to be answered by this program (Currently, the post is manually picked.)
