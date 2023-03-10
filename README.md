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

`python bot.py --transcribe <audio-file>`

`python bot.py --answer <question>`