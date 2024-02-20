import dotenv
from langchain.text_splitter import Language
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.chat_models import ChatOpenAI
from utils.colored_print.colored_print import print_green
from utils.load_java_documents_from_repo import load_java_documents_from_repo
from langchain_core.output_parsers import JsonOutputParser
from utils.prepare_prompt import JavaClassModel
from langchain_community.vectorstores import chroma

dotenv.load_dotenv()

def setup_qa_retriever(repo_path, model='gpt-4-0125-preview'):
    """
    Set up the QA retriever with documents from a given Java repository.

    Parameters:
    - repo_path (str): Path to the repository containing Java files.
    - model (str): The GPT model to be used.

    Returns:
    - qa (ConversationalRetrievalChain): The QA retrieval chain object.
    """

    # Load all java files from repo
    documents = load_java_documents_from_repo(repo_path)
    print(f"Number of documents: {len(documents)}")

    # Split documents
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JAVA, chunk_size=2000, chunk_overlap=200
    )
    texts = splitter.split_documents(documents=documents)
    print_green(texts)
    print(f"Number of chunks: {len(texts)}")
    
    embeddings = OpenAIEmbeddings(disallowed_special=())

    # Initialize vector database
    db = chroma.Chroma.from_documents(documents=texts, embedding=embeddings)

    # Set up retriever
    retriever = db.as_retriever(search_types=["mmr"], search_kwargs={"k": 8})
    
    # Initialize language model for QA retrieval
    llm = ChatOpenAI(model=model, temperature=0.4)
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)

    return qa

