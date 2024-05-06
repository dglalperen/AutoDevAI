import dotenv
from langchain.text_splitter import Language
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from utils.langchain_helper.java_doc_loader import load_java_documents_from_repo_new
from utils.print_utils.colored_print import print_green
from langchain_community.vectorstores import chroma
from langchain_core.pydantic_v1 import BaseModel, Field

dotenv.load_dotenv()


class JsonResponseSchema(BaseModel):
    updated_java_class: str = Field(
        description="The updated Java class code.",
        example="public class MyClass { ... }",
    )


def setup_qa_retriever(repo_path, model="gpt-4-0125-preview"):
    """
    Set up the QA retriever with documents from a given Java repository.

    Parameters:
    - repo_path (str): Path to the repository containing Java files.
    - model (str): The GPT model to be used.

    Returns:
    - qa (ConversationalRetrievalChain): The QA retrieval chain object.
    """

    # Load all java files from repo
    java_documents = load_java_documents_from_repo_new(repo_path)
    # print(f"Number of documents: {len(documents)}")

    # Split documents
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JAVA, chunk_size=2000, chunk_overlap=200
    )
    splitted_java_documents = splitter.split_documents(documents=java_documents)
    print_green(f"Number of chunks: {len(splitted_java_documents)}")

    embedding_function = OpenAIEmbeddings(disallowed_special=())

    # Initialize vector database
    vectorstore = chroma.Chroma.from_documents(
        documents=splitted_java_documents, embedding=embedding_function
    )

    # Set up retriever
    retriever = vectorstore.as_retriever(search_types=["mmr"], search_kwargs={"k": 8})

    # Initialize language model for QA retrieval
    llm = ChatOpenAI(model=model, temperature=0.4)
    memory = ConversationSummaryMemory(
        llm=llm, memory_key="chat_history", return_messages=True
    )
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, memory=memory
    )

    return qa
