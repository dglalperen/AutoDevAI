from utils.setup_qa_retriever import setup_qa_retriever

def start_conversation(qa):
    print("\x1b[32m%s\x1b[0m" % "Welcome to the Java Repository QA Chatbot!")
    print("\x1b[32m%s\x1b[0m" % "You can ask me any question about the repository, or type 'exit' to end.")
    #print("\x1b[33m%s\x1b[0m" % "yellow color")  # Gelb
    #print("\x1b[31m%s\x1b[0m" % "red color") # Rot
    #print("\x1b[32m%s\x1b[0m" % "green color") # Grün
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("\x1b[32m%s\x1b[0m" % "Chatbot: Goodbye!")
            break
        
        response = qa(user_input)
        print(f"\x1b[32m%s\x1b[0m" % "Chatbot: {response['answer']}")

if __name__ == "__main__":
    repo_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/car-rental"
    model = "gpt-4-0125-preview"
    qa = setup_qa_retriever(repo_path, model)
    print("QA retriever set up successfully!")

    start_conversation(qa)