import dotenv
from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.chat_models import ChatOpenAI
from utils.load_java_documents_from_repo import load_java_documents_from_repo
import os

#dotenv.load_dotenv()

#repo_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/java2022-kodlamaio"

if __name__ == "__main__":
    # Load all java files from repo
    documents = load_java_documents_from_repo(repo_path)
    print(f"Number of documents: {len(documents)}")

    # Split
    splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JAVA,
                                                            chunk_size=2000,
                                                            chunk_overlap=200)

    texts = splitter.split_documents(documents=documents)
    print(f"Number of chunks: {len(texts)}")

    # init vectordb
    db = Chroma.from_documents(texts, OpenAIEmbeddings(disallowed_special=()))

    retriever = db.as_retriever(
        search_types=["mmr"],
        search_kwargs={"k": 8}
    )

    # QA Retrieval
    model_gpt3 = "gpt-3.5-turbo-16k"
    model_gpt4 = "gpt-4"
    llm = ChatOpenAI(model=model_gpt4)
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever,memory=memory)


    example_issue = {
                "key": "AYtJVpm-KPReuWXKhjR_",
                "rule": "java:S2293",
                "severity": "MINOR",
                "component": "dglalperen_JavaKamp2022-Dersler:src/main/java/kodlama/io/rentacar/business/concretes/BrandManager.java",
                "project": "dglalperen_JavaKamp2022-Dersler",
                "line": 28,
                "hash": "481b1097f16bc00b437963898e60145a",
                "textRange": {
                    "startLine": 28,
                    "endLine": 28,
                    "startOffset": 65,
                    "endOffset": 87
                },
                "flows": [],
                "status": "OPEN",
                "message": "Replace the type specification in this constructor call with the diamond operator (\"<>\").",
                "effort": "1min",
                "debt": "1min",
                "author": "pelinhangisi@gmail.com",
                "tags": [
                    "clumsy"
                ],
                "transitions": [
                    "confirm",
                    "resolve",
                    "falsepositive",
                    "wontfix"
                ],
                "actions": [
                    "set_type",
                    "set_tags",
                    "comment",
                    "set_severity",
                    "assign"
                ],
                "comments": [],
                "creationDate": "2022-11-02T21:05:21+0100",
                "updateDate": "2023-10-19T21:07:53+0200",
                "type": "CODE_SMELL",
                "organization": "dglalperen",
                "cleanCodeAttribute": "CLEAR",
                "cleanCodeAttributeCategory": "INTENTIONAL",
                "impacts": [
                    {
                        "softwareQuality": "MAINTAINABILITY",
                        "severity": "LOW"
                    }
                ]
            }

    # Noch unsicher welches besser ist
    # - Line: {example_issue['line']}
    # - Location: Line {example_issue['line']} (Start offset: {example_issue['textRange']['startOffset']}, End offset: {example_issue['textRange']['endOffset']})
    
    prompt_text = f"""
    Task: Correct the identified issue in the provided Java class
        and return the corrected class in its entirety.

    Issue Details:
    - Rule: {example_issue['rule']}
    - Component: {example_issue['component']}
    - Location: Line {example_issue['line']} (Start offset: {example_issue['textRange']['startOffset']}, End offset: {example_issue['textRange']['endOffset']})
    - Message: {example_issue['message']}
    - Effort: {example_issue['effort']}
    - Issue Type: {example_issue['type']}

    Please return the corrected Java class.
    """


    # Chat
    result = qa(prompt_text)
    print(f"Answer: {result['answer']}")