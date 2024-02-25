from pydantic import BaseModel, Field
from utils.langchain_helper.setup_qa_retriever import setup_qa_retriever
from utils.print_utils.colored_print import print_blue, print_green, print_red

def start_conversation(qa):
    print_blue("Welcome to the Java Repository QA Chatbot!")
    print_blue("You can ask me any question about the repository, or type 'exit' to end.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break
        
        response = qa(user_input)
        print_blue(f"Chatbot: {response['answer']}")

if __name__ == "__main__":
    repo_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/maven-web-application-master"
    model = "gpt-3.5-turbo-0613"
    #model = "gpt-4-1106-preview"
    qa = setup_qa_retriever(repo_path, model)
    print_blue("QA retriever set up successfully!")
    start_conversation(qa)