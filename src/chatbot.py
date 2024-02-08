from utils.setup_qa_retriever import setup_qa_retriever


def start_conversation(qa):
    print("Welcome to the Java Repository QA Chatbot!")
    print("You can ask me any question about the repository, or type 'exit' to end.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break
        
        response = qa(user_input)
        print(f"Chatbot: {response['answer']}")

if __name__ == "__main__":
    repo_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/car-rental"
    model = "gpt-4"
    qa = setup_qa_retriever(repo_path, model)
    print("QA retriever set up successfully!")

    start_conversation(qa)