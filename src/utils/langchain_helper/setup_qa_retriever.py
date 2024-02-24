import dotenv
from langchain.text_splitter import Language
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.chat_models import ChatOpenAI
from utils.langchain_helper.java_doc_loader import load_java_documents_from_repo_new
from utils.print_utils.colored_print import print_blue, print_green
from langchain.vectorstores import Chroma

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
    java_documents = load_java_documents_from_repo_new(repo_path)
    #print(f"Number of documents: {len(documents)}")

    # Split documents
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JAVA, chunk_size=2000, chunk_overlap=200
    )
    splitted_java_documents = splitter.split_documents(documents=java_documents)
    print("Chunks: ")
    print_blue(60*"-")
    print_green(splitted_java_documents)
    print_blue(60*"-")
    print_green(f"Number of chunks: {len(splitted_java_documents)}")
    
    embedding_function = OpenAIEmbeddings(disallowed_special=())
    
    # Initialize vector database
    persist_directory = "chroma_db"
    vectorstore = Chroma.from_documents(documents=splitted_java_documents,
                                        embedding=embedding_function,
                                        persist_directory=persist_directory)

    # Set up retriever
    retriever = vectorstore.as_retriever(search_types=["mmr"], search_kwargs={"k": 8})
    
    # Initialize language model for QA retrieval
    llm = ChatOpenAI(model=model, temperature=0.4)
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory)

    return qa

