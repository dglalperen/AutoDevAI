import os
import dotenv
from openai import OpenAI

from utils.print_utils.colored_print import print_blue


class OpenAIConversationHandler:
    def __init__(self, api_key, model="gpt-4-1106-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def ask_question(self, question):
        """
        Ask a question and get a response based on the current conversation history.

        Parameters:
        - question (str): The question or issue description.

        Returns:
        - response (str): The model's response.
        """
        # self.conversation_history.append({"role": "user", "content": question})

        system_message = {
            "role": "system",
            "content": """
                As an expert Java developer tasked with correcting SonarQube issues, your role is to analyze Java classes and apply necessary fixes directly. When responding, ensure you:

                - Return the complete Java class code, including all imports and package declarations.
                - Address the specified issue comprehensively, ensuring the fix maintains the class's functionality and adheres to Java best practices.
                - Follow this JSON response format precisely to encapsulate the updated Java class code:
                  ```json
                  {
                      "updated_java_class": "Complete Java class code here."
                  }
                  ```
                It's crucial to include the entire corrected class code in your response, without indicating parts of the code as 'unchanged' or using placeholders. Aim for detailed, precise fixes that fully resolve the issue while keeping the class fully operational.
                """,
        }

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[system_message, {"role": "user", "content": question}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        try:
            # Extract the response and append it to the conversation history
            model_response = response.choices[0].message.content
            print(40 * "=")
            print_blue(f"Model response: {model_response}")
            print(40 * "=")

            return model_response
        except Exception as e:
            print(f"Error processing the API response: {e}")
            return None

    def reset_conversation(self):
        """
        Resets the conversation history, starting fresh.
        """
        self.conversation_history = [self.conversation_history[0]]
