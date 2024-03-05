import json
from langchain_core.tools import tool
from dotenv import load_dotenv
#from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openai.output_parsers import JsonOutputToolsParser,JsonOutputKeyToolsParser
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
    
def output_parser_test():
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106")
    llm_with_tools = llm.bind_tools([format_code_as_json], tool_choice ='format_code_as_json')
    chain = (
    llm 
    | JsonOutputKeyToolsParser(key_name="multiply", return_single=True)
    )
    chain_response = chain.invoke("What's four times 23")
    res = chain_response[0]
    first_int = res.get("first_int")
    second_int = res.get("second_int")
    
    response = multiply.invoke({"first_int": first_int, "second_int": second_int})
    print(response)

if __name__ == "__main__":
    load_dotenv()
    repo_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/expense-tracker-api"

    