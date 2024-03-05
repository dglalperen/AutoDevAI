import openai
import json
import os
from tqdm import tqdm
import dotenv
import re

def print_blue(text):
    print("\x1b[34m{}\x1b[0m".format(text))

def print_red(text):
    print("\x1b[31m{}\x1b[0m".format(text))

def print_green(text):
    print("\x1b[32m{}\x1b[0m".format(text))

def print_yellow(text):
    print("\x1b[33m{}\x1b[0m".format(text))
    
def extract_updated_java_class(response):
    """
    Extracts the updated Java class from the JSON content.

    Parameters:
    - response (str): The JSON string containing the updated Java class.

    Returns:
    - str: The extracted Java class code, or an empty string if not found.
    """
    try:
        # Directly parse the JSON string into a Python dictionary
        parsed_json = json.loads(response)
            
        # Extract the 'updated_java_class' field containing the Java code
        updated_java_class = parsed_json.get('updated_java_class', '')
        if updated_java_class:
            return updated_java_class

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    return ''

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
gpt_model = "gpt-3.5-turbo-0125"
#gpt_model = "gpt-4-0125-preview"
    
def format_code_as_json(java_class):
    """
    Formats Java code into a JSON structure.

    :param java__class: String containing Java class code.
    :return: JSON string with the Java code encapsulated.
    """
    try:
        formatted_json = json.dumps({"updated_java_class": java_class})
        return formatted_json
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [
    {"role": "system", "content": "You are a software developer working on a project.Your Task is to modify / update java classes based on specific instructions you will get. After adjusting the java class you will return a JSON Object, ecapsulating the whole updated java class including imports and class declaration"},
    {
        "role": "user",
        "content": """I have this following class which i want you to add some describing inline comments.
        Here is the class you need to modify:
            {{
            package com.pairlearning.expensetracker;

            import com.pairlearning.expensetracker.filters.AuthFilter;
            import org.springframework.boot.SpringApplication;
            import org.springframework.boot.autoconfigure.SpringBootApplication;
            import org.springframework.boot.web.servlet.FilterRegistrationBean;
            import org.springframework.context.annotation.Bean;
            import org.springframework.web.cors.CorsConfiguration;
            import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
            import org.springframework.web.filter.CorsFilter;

            @SpringBootApplication
            public class ExpenseTrackerApiApplication {

                public static void main(String[] args) {
                    SpringApplication.run(ExpenseTrackerApiApplication.class, args);
                }

                @Bean
                public FilterRegistrationBean<CorsFilter> corsFilter() {
                    FilterRegistrationBean<CorsFilter> registrationBean = new FilterRegistrationBean<>();
                    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
                    CorsConfiguration config = new CorsConfiguration();
                    config.addAllowedOrigin("*");
                    config.addAllowedHeader("*");
                    source.registerCorsConfiguration("/**", config);
                    registrationBean.setFilter(new CorsFilter(source));
                    registrationBean.setOrder(0);
                    return registrationBean;
                }

                @Bean
                public FilterRegistrationBean<AuthFilter> filterRegistrationBean() {
                    FilterRegistrationBean<AuthFilter> registrationBean = new FilterRegistrationBean<>();
                    AuthFilter authFilter = new AuthFilter();
                    registrationBean.setFilter(authFilter);
                    registrationBean.addUrlPatterns("/api/categories/*");
                    return registrationBean;
                }

            }
            }}
        """
    }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "format_code_as_json",
                "description": "Format given Java code into a strict JSON structure",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "java_class": {
                            "type": "string",
                            "description": "Java class code to be formatted into JSON structure"
                        }
                    },
                    "required": ["java_class"]
                }
            }
        }
    ]
    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        print("Model wants to call a function")
        # Step 3: call the function
        available_functions = {
            "format_code_as_json": format_code_as_json,
        }
        messages.append(response_message)
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(java_class=function_args.get("java_class"))
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        # second_response = openai.ChatCompletion.create(
        #     model=gpt_model,
        #     messages=messages,
        # )
        print("Finished calling function")
        print("Extracting updated Java class")
        print(60*"-")
        print_yellow(messages[-1]["content"])
        print(60*"-")
        print(60*"-")
        updated_java_class = extract_updated_java_class(messages[-1]["content"])
        print_blue(updated_java_class)
        # return second_response
    

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

if __name__ == "__main__":
    # Run the test for a specified number of iterations
    # success, failure = test_gpt_function(iterations=20)
    # print(f"Success: {success}, Failure: {failure}")
    run_conversation()
