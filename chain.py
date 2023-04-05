import glob
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os

def basic_parser(filename, model):
    """
    Takes in a .txt file and returns a list of strings, each string being a sentence.
    """
    path = os.path.join(os.getcwd(), "transcriptions", filename)
    with open(path, 'r') as f:
        content = f.read()
        sentences = content.split('\n')
    
    embeddings = model.encode(sentences)
    return sentences, embeddings

def create_vectorstore(transcription_folder: str):
    files = glob.glob(transcription_folder + "/*.txt")
    texts = []
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=512, chunk_overlap=64)
    for file in files:
        with open(file) as f:
            text = f.read()
            texts.extend(text_splitter.split_text(text))

    embeddings = HuggingFaceEmbeddings()

    return Chroma.from_texts(
        texts, embeddings, metadatas=[{"source": f"{i}-pl"} for i in range(len(texts))], persist_directory="./cache"
    )

def load_vecstore():
    return Chroma(persist_directory="./cache")

def get_chain(transcription_folder: str):
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
        ChatOpenAI(temperature=0),
        chain_type="stuff",
        vectorstore=load_vectorstore(transcription_folder),
        chain_type_kwargs=chain_type_kwargs,
    )


if __name__  == "__main__":
    create_vectorstore("./transcriptions")