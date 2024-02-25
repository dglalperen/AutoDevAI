from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage
import json
from gpt_function_calling import get_pizza_info

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

llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0.4)
message = llm.predict_messages(
    [HumanMessage(content="What is the capital of France?")], functions=functions
)
print("Message 1:",message)
print("Additional Kwargs:",message.additional_kwargs)

query = "What is the price of Tonno Pizza?"

response_pizza = llm.predict_messages([HumanMessage(content=query)],
                                      functions=functions)

print(30*"-")
print("Message 2:",response_pizza)
print("Additional Kwargs:",response_pizza.additional_kwargs)

print(30*"-")
pizza_name = json.loads(
    response_pizza.additional_kwargs["function_call"]["arguments"]).get("pizza_name")

print("Pizza Name:",pizza_name)


print(30*"-")
pizza_api_response = get_pizza_info(pizza_name)
print("Pizza API Response:",pizza_api_response)

second_response = llm.predict_messages(
    [
        HumanMessage(content=query),
        AIMessage(content=str(response_pizza.additional_kwargs)),
        ChatMessage(
            role="function",
            additional_kwargs={
                "name": response_pizza.additional_kwargs["function_call"]["name"],
            },
            content=pizza_api_response,
        )
    ],
    functions=functions
)

print(30*"-")
print("Second Response:",second_response)


