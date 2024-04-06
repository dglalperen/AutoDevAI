import json
from openai import OpenAI
import autogen
 
apiKey = '<api-key>'
config_list = [
    {
        'model': 'gpt-4-1106-preview',
        'api_key': apiKey
    }
]
 
messages = [
    {"role": "system", "content": 'You are an experienced business consultant. One of your major methodologies in order to kickstart new projects are profound brainstorming techniques. In this case, you will use the "Role Storming" technique.' }
]
 
functions = [
    {
        "name": "defineStakeholders",
        "description": "This method defines the roles of stakeholders participating in the brainstorming session! The result includes a role and a description of his role in the process!",
        "parameters": {
            "type": "object",
            "properties": {
                "stakeholders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "description": "The role of the stakeholder!"
                            },
                            "roleDescription": {
                                "type": "string",
                                "description": "A description of the role of the stakeholder in the process!"
                            }
                        }
                    }
                }
            }
        },
        "required": ["stakeholders"]
    },
    {
        "name": "getClusters",
        "description": "This method identifies clusters in a given brainstorming discussion!",
        "parameters": {
            "type": "object",
            "properties": {
                "clusters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The topic of the cluster!"
                            },
                            "points": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "A point describing details of the given cluster!"
                                }
                            }
                        }
                    }
                }
            }
        },
        "required": ["clusters"]
    }
]
 
def getStakeholders(question):
    prompt = 'Your first task is to identify the top five most important stakeholders, including a description of their role in the brainstorming process, to brainstorm the following question:\n\n"""' + question + '"""\n\nThe stakeholders should all be different subject matter experts for the topic that should be brainstormed. All stakeholders need to be experts of the subject that should be brainstormed here and you need to define their role descriptions accordingly.\n\nThe result is an array of the identified roles and their corresponding descriptions of the roles! Format the result in a JSON array that has objects with a role and a decscription key, as in the following example: { "stakeholders": [ { "role": "name of the role", "roleDescription": "a description of the role", ... }]}\n\nEnsure not to forget the description of the roles and STRONGLY adhere to the given JSON format in which for each stakeholder you need to have a JSON object including the role and the description of the role!'
 
    messages.append({"role": "user", "content": prompt })
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0.1,
        functions=functions,
        function_call={"name": "defineStakeholders"}
    )
 
    choice = response.choices[0]
    returnObject = json.loads(choice.message.function_call.arguments)
 
    return returnObject['stakeholders']
 
def clusterIdeas(groupChatMessages):
    for msg in groupChatMessages:
        messages.append({ "role": msg['role'], "content": msg['content']})
    prompt = 'Your final task is to identify clusters from the current brainstorming session. Identify different clusters, provide meaningful names for each cluster and summarize the major points for each cluster!'
 
    messages.append({"role": "user", "content": prompt })
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0.1,
        functions=functions,
        function_call={"name": "getClusters"}
    )
 
    returnObject = json.loads(response.choices[0].message.function_call.arguments)
    return returnObject['clusters']
 
 
client = OpenAI(api_key = apiKey)
question = 'What is the best marketing strategy for a startup in the domain of blockchain and AI?'
#question = 'What might happen if humanity suddenly invents AGI?'
stakeholders = getStakeholders(question)
print(stakeholders)
gpt4_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}
user_proxy = autogen.UserProxyAgent(
    name='User',
    system_message='A user who needs a profound brainstorming session about a certain topic. The user uses the "Role Storming" methodology for brainstorming! The different roles participating in this brainstorming session should clearly focus on the topic at hand and not discuss different topics within this brainstorming session!',
    code_execution_config=False
)
agents = []
agents.append(user_proxy)
for stakeholder in stakeholders:
    name = stakeholder['role'].replace(' ', '-')
    agents.append(autogen.AssistantAgent(name=name, llm_config=gpt4_config, system_message=stakeholder['roleDescription']))
 
groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=5)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)
user_proxy.initiate_chat(manager, message=question)
 
clusters = clusterIdeas(groupchat.messages)
 
result = {
    'question': question,
    'clusters': clusters
}
 
print(result)