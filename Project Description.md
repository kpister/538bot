# Project Description

## Current Goal

Build a system that automatically answer students’ questions posted on Piazza.

## How?

We will use GPT to answer students’ questions. However, to make GPT’s answers more accurate, we will send along “context” that can help GPT answer the questions. This context is a chunk of transcription of Prof. Kaiser’s lecture.

## Inner Working of the Current System

![image](https://github.com/kpister/538bot/assets/71933012/e5ee9b53-7039-4e06-80a1-6177cb615d56)

**Data preparation**
  - Transcription
  1.	Transcribe Prof. Kaiser’s lectures using Whisper from OpenAI. 
      Result = a lot of text files

  - Prepare a database of vectors (vectors = embeddings of text chunks)
  1.	Split all of the text into chunks
  2.	Embed all those chunks using SBERT (in the code, you will see HuggingFaceEmbeddings, but it is just a wrapper of SBERT) into vectors
  3.	Save those vectors in the Chroma database

**Real-time response**
  1.	Fetch a student’s question from Piazza
  2.	Embed that question text using SBERT into a vector (called vector Q)
  3.	Perform similarity search -> find k nearest neighbors to vector Q (by default k = 4). Neighbors = Vectors saved in Chroma
  4.	Send that question, along with the text associated with the closest vector (a context), to GPT
  5.	Post GPT’s answer back to Piazza

## Current Problems
  1.	Sometimes, the context vector that has the answer isn't nearest to vector Q, e.g. answer is in the second nearest vector.
      -> We can try fixing this by sending more than one context vector to GPT.
  2.	It is hard to know how we should split the transcriptions (what chunk size/overlap to use).
      -> We can split texts with different parameters, embed and store all of them in the database. (Certain sentences might appear in multiple vectors.)

## Recommended Readings

Transcription - https://github.com/openai/whisper/blob/main/whisper/transcribe.py
Question Answering - https://python.langchain.com/docs/use_cases/question_answering/how_to/vector_db_qa

## Comments

- Current code is using VectorDBQAWithSourcesChain, but it is deprecated. Please change it to RetrievalQAWithSourcesChain.
- Currently, there are no official Piazza APIs, so we will use unofficial ones (https://github.com/hfaran/piazza-api/tree/develop) to fetch questions from Piazza and post answers back to it.


