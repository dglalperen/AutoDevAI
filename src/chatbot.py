from pydantic import BaseModel, Field
from utils.colored_print.colored_print import print_blue, print_green, print_red
from utils.extract_corrected_code import extract_corrected_code_json
from utils.setup_qa_retriever import setup_qa_retriever
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from utils.prepare_prompt import JavaClassModel, setup_json_output_parser

def setup_prompt():
    """
    Set up the prompt for the QA retriever.
    """
    format_instructions = setup_json_output_parser()

    prompt=f"""
        System message: You are tasked with updating a Java class. Specifically, modify the 'getExercise' method in the 'ExerciseController' class to include a new log statement.
        Provide the complete class without any shortenings and any explanatory text.
        
        Format instructions:
        
        ```{format_instructions}```
        
        Task: Add a log statement to print "Exercise generated successfully" right after the 'ExerciseResponseTO' object is created in the 'getExercise' method. Ensure the log level is set to 'info'.
        
        Do the Task exactly how it is described or you will get a wrong answer.
        
    """
    return prompt
        

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
        print(f"\x1b[32m%s\x1b[0m" % response)
        print(f"\x1b[32m%s\x1b[0m" % f"Chatbot: {response['answer']}")

if __name__ == "__main__":
    repo_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/exercise-generator-2"
    #model = "gpt-3.5-turbo-0613"
    model = "gpt-4-1106-preview"
    qa = setup_qa_retriever(repo_path, model)
    print("QA retriever set up successfully!")
    
    response = qa(setup_prompt())
    
    corrected_code = extract_corrected_code_json(response['answer'])
    print(60*"-")
    print_green(f"Corrected Code: {corrected_code}")
    print(60*"-")
    
    # Setting up output parser
    json_output_parser = JsonOutputParser(pydantic_object=JavaClassModel)
    print("JSON Output Parser set up successfully!")
    print(60*"-")
    print_blue(json_output_parser.parse(response['answer']))
    print(60*"-")
    parsed_response = json_output_parser.parse(response['answer'])
    
    print(60*"-")
    print_green(f"DEBUG Parsed Response: {parsed_response}")
    print(60*"-")
    print(60*"-")
    print_red(f"DEBUG OPENAI Response: {response['answer']}")
    print(60*"-")
    
    #start_conversation(qa)