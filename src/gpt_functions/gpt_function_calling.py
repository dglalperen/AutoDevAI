from dotenv import load_dotenv
import os
import openai
import json

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# 1 Define the function
def get_pizza_info(pizza_name:str):
        pizza_info = {
            "name": pizza_name,
            "price": "10.99",
        }
        return json.dumps(pizza_info)


if __name__ == "__main__":
    # 2 Describe the function

    functions = [
        {
            "name": "get_pizza_info",
            "description": "Get name and price of a pizza of the restaurant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pizza_name": {
                        "type": "string",
                        "description": "The name of the pizza for example 'Margherita'."
                    }
                },
                "required": ["pizza_name"]
            }
        }
    ]

    # 3 Call the function inside a chat

    def chat(query):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": "query"}],
            functions=functions
        )
        message=response["choices"][0]["message"]
        return message

    # 4 Call the chat function
    query = "What is the price of Margherita?"
    response = chat(query)

    # 5 Check if the function was called

    if response.get("function_call"):
        function_name = response["function_call"]["name"]
        pizza_name = json.loads(response["function_call"]["arguments"]).get("pizza_name")
        function_response = get_pizza_info(pizza_name)
        
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": query},
                    response,
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response
                    }]
        )
        
    print(second_response)