from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


def load_vectorstore(transcription_folder: str):
    # TODO use transcription folder
    with open("../../state_of_the_union.txt") as f:
        state_of_the_union = f.read()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(state_of_the_union)

    embeddings = OpenAIEmbeddings()

    # TODO cache this, only load on new transcription files
    return Chroma.from_texts(
        texts, embeddings, metadatas=[{"source": f"{i}-pl"} for i in range(len(texts))]
    )


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
