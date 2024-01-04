from openai import OpenAI
import json
import os
from tqdm import tqdm
import dotenv

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
gpt_model = "gpt-3.5-turbo"
#gpt_model = "gpt-4-1106-preview"

# Example dummy function to format Java code into JSON
def format_code_as_json(java_code):
    """Format Java code into a strict JSON structure"""
    try:
        # This is a dummy implementation. 
        # In a real scenario, you would implement proper JSON formatting here.
        return json.dumps({"result": java_code})
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [
    {
        "role": "user",
        "content": "Please use the 'format_code_as_json' function to format this Java code into a JSON string:\n\npublic class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello World!\");\n    }\n}"
    }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "format_code_as_json",
                "description": "Format a given Java code snippet into a strict JSON structure",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "java_code": {
                            "type": "string",
                            "description": "The corrected Java class code to be formatted"
                        }
                    },
                    "required": ["java_code"]
                }
            }
        }
    ]
    response = client.chat.completions.create(
        model=gpt_model,
        messages=messages,
        tools=tools,
        tool_choice="auto"  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        available_functions = {
            "format_code_as_json": format_code_as_json,
        }
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(java_code=function_args.get("java_code"))
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model=gpt_model,
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response

# Running the conversation
#response = run_conversation()

# # Check if response is valid and has content
# if response and response.choices and response.choices[0].message.content:
    
#     response_content = response.choices[0].message.content

#     # Check if the response contains a JSON block
#     if "```json" in response_content:
#         # Extract JSON string from the Markdown code block
#         json_string = response_content.split('```json')[1].split('```')[0].strip()

#         try:
#             # Parse the extracted JSON string
#             formatted_code_json = json.loads(json_string)
#             print("Parsed JSON Data:", formatted_code_json)
#         except json.JSONDecodeError as e:
#             print("Error decoding JSON:", e)
#             print("Extracted JSON String:", json_string)
#     else:
#         print("No JSON block found in the response.")
        
# else:
#     print("No valid response content received.")
    
    

def test_gpt_function(iterations=10):
    success_count = 0
    failure_count = 0

    for _ in tqdm(range(iterations), desc="Processing", unit="iteration"):
        response = run_conversation()

        # Check if response is valid and has content
        if response and response.choices and response.choices[0].message.content:
            response_content = response.choices[0].message.content

            # Check if the response contains a JSON block
            if "```json" in response_content:
                json_string = response_content.split('```json')[1].split('```')[0].strip()
                try:
                    json.loads(json_string)
                    success_count += 1
                except json.JSONDecodeError:
                    failure_count += 1
            else:
                failure_count += 1
        else:
            failure_count += 1

    return success_count, failure_count

# Run the test for a specified number of iterations
success, failure = test_gpt_function(iterations=20)
print(f"Success: {success}, Failure: {failure}")