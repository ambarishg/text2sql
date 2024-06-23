from openai import AzureOpenAI

from dotenv import load_dotenv
from dotenv import dotenv_values

from azureopenaimanager.prompts import *

class AzureOpenAIManager:
    
    def __init__(self,endpoint,api_key,deployment_id,api_version):
        
        self.client = AzureOpenAI(
            azure_endpoint = endpoint,
            api_key=api_key,  
            api_version=api_version
        )

        self.deployment_id = deployment_id


    def generate_answer(self,conversation):
        response = self.client.chat.completions.create(
        model=self.deployment_id,
        messages=conversation,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop = [' END']
        )
        
        return (response.choices[0].message.content).strip(), \
            response.usage.total_tokens, \
            response.usage.prompt_tokens,response.usage.completion_tokens
    

    def generate_answer_document(self,query):
        messages=[{"role": "assistant", "content": question},
                {"role": "user", "content": query}
                ]
        return self.generate_answer(messages)
    
    def create_prompt(self,context,query):
        header = "If the answer is not found within the context, please mention \
        that the answer is not found \
        Do not answer anything which is not in the context"
       
        return header + context + "\n\n" + query + "\n"
     
    
    def generate_reply_from_context(self,user_input, content, conversation):
        prompt = self.create_prompt(content,user_input)            
        conversation.append({"role": "assistant", "content": prompt})
        conversation.append({"role": "user", "content": user_input})
        reply = self.generate_answer(conversation)
        return reply

