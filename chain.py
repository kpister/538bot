import glob
import os
import click

from langchain.chains import VectorDBQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


def basic_parser(filename, model):
    """
    Take in a .txt file and returns a list of strings, each string being a sentence.
        
    Parameters
    ----------
    filename
        file whose content is to be splitted into chunks and then embedded
    model
        model used to embed those chunks
    """
    path = os.path.join(os.getcwd(), "transcriptions", filename)
    with open(path, "r") as f:
        content = f.read()
        sentences = content.split("\n")

    embeddings = model.encode(sentences)
    return sentences, embeddings


def create_vectorstore(transcription_folder: str, cache_dir: str):
    """
    Grab all text files in transcription_folder, split those texts into chunks,
    then embed those texts into vectors which are then stored in a vector database.
        
    Parameters
    ----------
    transcription_folder
        folder in which text files are placed 
    cache_dir
        the name of the directory of a vector database
    """
    files = glob.glob(transcription_folder + "/*.txt")
    texts = []
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=512, chunk_overlap=64
    )
    for file in files:
        with open(file) as f:
            text = f.read()
            texts.extend(text_splitter.split_text(text))

    embeddings = HuggingFaceEmbeddings()

    chroma_db = Chroma.from_texts(
        texts,
        embeddings,
        metadatas=[{"source": f"{i}-pl"} for i in range(len(texts))],
        persist_directory=cache_dir,
    )
    chroma_db.persist() # persist the database
    return chroma_db


def load_vecstore(cache_dir: str):
    """
    Load a vector database.
        
    Parameters
    ----------
    cache_dir
        the name of the directory of a vector database
    """
    return Chroma(
        persist_directory=cache_dir, embedding_function=HuggingFaceEmbeddings()
    )


def get_chain(cache_dir: str):
    """
    Make a chain which will then be used to answer questions.
        
    Parameters
    ----------
    cache_dir
        the name of the directory of a vector database
    """
    system_template = """Use the following pieces of context to answer the users question. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    ALWAYS return a "SOURCES" part in your answer.
    The "SOURCES" part should be a reference to the source of the document from which you got your answer.

    Example of your response should be:

    ```
    The answer is foo
    SOURCES: xyz
    ```

    Begin!
    ----------------
    {summaries}"""

    # TODO allow for back and forth responses / conversation
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    chain_type_kwargs = {"prompt": prompt}
    return VectorDBQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0, model_name="gpt-4"),
        chain_type="stuff",
        vectorstore=load_vecstore(cache_dir),
        chain_type_kwargs=chain_type_kwargs,
        return_source_documents=True
    )

@click.command()
@click.option(
    "--transcription_folder",
    default="./transcriptions",
    help="Folder that saved transcribed audio recordings",
)
@click.option(
    "--cache_dir", default="cache", help="The name of the folder that will store embeddings"
)
def main(transcription_folder: str, cache_dir: str):
    create_vectorstore(transcription_folder, cache_dir)


if __name__ == "__main__":
    main()
    # db = load_vecstore("./cache")
    # results = db.similarity_search("What is functional programming?", 5)
    # print(results)
