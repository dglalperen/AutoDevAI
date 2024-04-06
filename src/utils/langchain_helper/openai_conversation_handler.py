import os
import dotenv
from openai import OpenAI


class OpenAIConversationHandler:
    def __init__(self, api_key, model="gpt-4-1106-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = [
            {
                "role": "system",
                "content": """
                You are an expert Java developer correcting SonarQube issues. Your responses should be in the following JSON format:
                ```json
                {
                    "updated_java_class": "The updated Java class code."
                }
                ```
                Please provide detailed fixes for code issues as described, and return the whole Java class including imports, without any shortenings.
                """,
            }
        ]

    def ask_question(self, question):
        """
        Ask a question and get a response based on the current conversation history.

        Parameters:
        - question (str): The question or issue description.

        Returns:
        - response (str): The model's response.
        """
        self.conversation_history.append({"role": "user", "content": question})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            n=1,
            temperature=0.4,
            response_format={"type": "json_object"},
        )

        # Assuming the API response is structured with the response in the expected format
        try:
            # Extract the response and append it to the conversation history
            model_response = response.choices[0].message
            self.conversation_history.append(
                {"role": "assistant", "content": model_response}
            )

            print("Successfully retrieved the response.")
            return model_response
        except Exception as e:
            print(f"Error processing the API response: {e}")
            return None

    def reset_conversation(self):
        """
        Resets the conversation history, starting fresh.
        """
        self.conversation_history = [self.conversation_history[0]]
