import json
from langchain_core.tools import tool
from dotenv import load_dotenv
#from langchain_openai import ChatOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai.output_parsers import JsonOutputKeyToolsParser, JsonOutputToolsParser
from java_doc_loader import load_java_documents_from_repo_new
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.vectorstores import Chroma

@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int

@tool
def format_code_as_json(java_class: str) -> str:
    """
    Format a given Java class code as a JSON string.
    
    Parameters:
    - java_class (str): The Java class code to be formatted.
    
    Returns:
    - (str): A JSON string representation of the updated Java class.
    """
    try:
        return json.dumps({"updated_java_class": java_class})
    except Exception as e:
        return json.dumps({"error": str(e)})
    
def multiply_test():
    print(multiply.name)
    print(multiply.description)
    print(multiply.args)

    print(multiply.invoke({"first_int": 4, "second_int": 5}))

    model = ChatOpenAI(model="gpt-3.5-turbo-1106")
    
    model_with_tools = model.bind_tools([multiply], tool_choice ='multiply')
    
    print(model_with_tools.kwargs["tools"])
    print(model_with_tools.kwargs["tool_choice"])
    
    chain = (
    model_with_tools 
    | JsonOutputKeyToolsParser(key_name="multiply", return_single=True)
    )
    chain_response = chain.invoke("What's four times 23")
    res = chain_response[0]
    first_int = res.get("first_int")
    second_int = res.get("second_int")
    
    response = multiply.invoke({"first_int": first_int, "second_int": second_int})
    print(response)

def setup_qa_retriever_new(repo_path, model='gpt-4-0125-preview'):
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
    print(f"Number of chunks: {len(splitted_java_documents)}")
    
    embedding_function = OpenAIEmbeddings(disallowed_special=())
    
    # Initialize vector database
    vectorstore = Chroma.from_documents(documents=splitted_java_documents,
                                        embedding=embedding_function)

    # Set up retriever
    retriever = vectorstore.as_retriever(search_types=["mmr"], search_kwargs={"k": 8})
    # Initialize language model for QA retrieval
    llm = ChatOpenAI(model=model, temperature=0.4)
    #llm_with_tools = llm.bind_tools([format_code_as_json], tool_choice ='format_code_as_json')
    print("test0")
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
    print("test1")
    qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory)
    print("test2")
    qa_with_tools = qa.bind(tools=[format_code_as_json], tool_choice ='format_code_as_json')
    chain = (qa_with_tools 
            | JsonOutputToolsParser(key_name="format_code_as_json",return_single=True))

    return chain

if __name__ == "__main__":
    load_dotenv()
    repo_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/expense-tracker-api"
    setup_qa_retriever_new(repo_path)

    