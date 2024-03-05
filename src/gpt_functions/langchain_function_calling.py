from langchain_openai import ChatOpenAI
from langchain_openai.output_parsers import JsonOutputKeyToolsParser, JsonOutputToolsParser
from langchain.schema import HumanMessage, AIMessage, ChatMessage
import json
import os
import openai
from langchain.agents import Tool
from langchain.tools import tool

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
gpt_model = "gpt-3.5-turbo-0125"
#gpt_model = "gpt-4-0125-preview"

def print_blue(text):
    print("\033[94m{}\033[0m".format(text))

def extract_updated_java_class(response):
    try:
        parsed_json = json.loads(response)
        updated_java_class = parsed_json.get('updated_java_class', '')
        return updated_java_class
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    return ''

# def format_code_as_json(java_class):
#     try:
#         return json.dumps({"updated_java_class": java_class})
#     except Exception as e:
#         return json.dumps({"error": str(e)})
    
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

# tools = [
#     Tool(
#         name="format_code_as_json",
#         description="Format given Java code into a strict JSON structure. Useful when you need to encapsulate the Java code into a JSON object.",
#         func=format_code_as_json())
# ]

messages = [
    ChatMessage(role="system", content="You are a software developer working on a project.Your Task is to modify / update java classes based on specific instructions you will get. After adjusting the java class you will return a JSON Object, ecapsulating the whole updated java class including imports and class declaration"),
    HumanMessage(content="""I have this following class which I want you to add some describing inline comments and then return the updated class as a JSON object:
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
            }""")
]

llm = ChatOpenAI(model=gpt_model, temperature=0)
llm_with_tools = llm.bind_tools([format_code_as_json], tool_choice="format_code_as_json")

chain = (
    llm_with_tools
    | JsonOutputKeyToolsParser(key_name="format_code_as_json", return_single=True)
    )

response = chain.invoke("What's the updated Java class?")

print(60*"-")
print_blue(response)
print(60*"-")

# if response.additional_kwargs.get("function_call"):
#     function_response_content = response.additional_kwargs["function_call"]["content"]
#     updated_java_class = extract_updated_java_class(function_response_content)
#     print_blue(updated_java_class)
# else:
#     print("No function call was made.")

