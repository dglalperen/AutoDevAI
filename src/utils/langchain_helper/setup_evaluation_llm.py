import os
from openai import OpenAI

def evaluate_llm_response(prompt: str, model: str = "gpt-4-0125-preview"):
    """
    Sends an evaluation prompt to the OpenAI model and returns the response.

    :param prompt: The prompt to send to the model for evaluation.
    :param model: The model version to use for the evaluation.
    :return: The response from the model.
    """
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that compares two Java classes and evaluates the updated class."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    print("EVALUATION RESPONSE")
    print(60*"-")
    response_text = response.choices[0].message.content if response.choices else None
    print(response_text)
    print(60*"-")
    
    return response_text

if __name__ == "__main__":
    original_java_class = """
    package com.example;

    public class Example {
        public void printMessage() {
            System.out.println("Original message");
        }
        
        public void printAge(int age) {
            System.out.println(age);
        }
    }
    """
    
    updated_java_class = """
    package com.example;

    public class Example {
        public void printMessage() {
            System.out.println("Updated message");
        }
    }
    """

    issue_description = "Please update the print message from 'Original message' to 'Updated message'."
    
    prompt = f"""
    Let me provide you with the original and updated versions of a Java class after addressing a specific sonarqube issue.
    
    I need you to evaluate the updated class and determine if it has been correctly updated. Especially pay attention to whether or not the updated class has no missing or incorrect parts.
    
    Please review both versions and the issue description to determine if the update is complete and accurate.
    
    Original Java Class:
    {original_java_class}

    Updated Java Class:
    {updated_java_class}

    Issue Description:
    {issue_description}
    
    return the response in this JSON format:
    
    ```json
    {{
        "correctly_updated_class": boolean  // Boolean, whether the updated class has no missing or incorrect parts.
    }}
    """

    evaluate_llm_response(prompt)
