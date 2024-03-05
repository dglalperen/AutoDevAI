from langchain.output_parsers import ResponseSchema, StructuredOutputParser

def build_error_fix_prompt(error_message):
    # Define a response schema for the corrected Java code
    response_schema = ResponseSchema(name="corrected_java_class", description="The corrected Java class code, encapsulated in a JSON object.")
    
    # Instantiate an output parser using the defined response schema
    output_parser = StructuredOutputParser.from_response_schemas([response_schema])
    
    # Retrieve format instructions from the output parser
    format_instructions = output_parser.get_format_instructions()
    
    # Construct the prompt with detailed instructions and formatting requirements
    prompt = f"""
        System message: You are a Java programming expert. Correct the issue in the Java code that caused the build error and provide the corrected code.

        Build Error Details:
        - Error Message: '{error_message}'

        Task: Analyze the error message and provide the corrected Java code to fix this build error. Ensure the solution addresses the specific issue mentioned in the error message.

        Instructions:
        1. Review the build error details.
        2. Provide the corrected Java class code addressing the mentioned issue.
        3. Format the corrected code as a JSON object with the key 'corrected_java_class'.

        Return Format:
        {format_instructions}

        Note: The solution should be directly applicable to fix the error and allow the build to succeed without introducing new issues.
        %
        
        YOUR RESPONSE:
    """.strip()
    
    print(f"DEBUG: Prompt: {prompt}")
    return prompt
