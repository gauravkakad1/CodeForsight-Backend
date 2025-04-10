
import os
# import streamlit as st
from dto.ChatRequest import ChatRequest
from dto.GetMessagesRequest import GetMessagesRequest
from groq import Groq
import graphviz
from dotenv import load_dotenv

# import tiktoken
import MongoDB_database as mongodb


# Load environment variables from .env file
load_dotenv()

# Groq API configuration
apiKey = os.getenv("GROQ_TOKEN")
client = Groq(api_key=apiKey)

# if not apiKey:
#     st.error("Error: GROQ_TOKEN is not set. Please check your environment variables.")
#     st.stop()


# Function to query 
async def query_groq(question : str,req: ChatRequest , isDotCode: bool , isexplanation : bool ) -> str:
    try:
        print("Request : ",req)
        print("isDotCode : ",isDotCode)
        print("isexplanation : ",isexplanation)
        prompt : str = req.input_question
        print("Prompt : ",prompt)
        req =  GetMessagesRequest(
            conversation_id = req.conversation_id,
            user_id =req.user_id
        )
        chat_messages = []

        print("1")       
        db_msgs = await mongodb.get_all_messages(req.conversation_id)
        print("DB Messages : ",str(db_msgs))
        db_msgs = db_msgs or [] 
        print("2")       
        if isexplanation :
            db_msgs = [msg for msg in db_msgs if (msg['isExplanation'] != 0 and msg['isDotCode'] == 0) or (msg['isExplanation'] == 0 and msg['isDotCode'] == 0)]
            chat_messages.append({"role": "system", "content": "You are a helpful assistant expert in the cybersecurity domain."})
            # print("Chat Messages2 : ",chat_messages)
            # print("DB Messages2 : ",db_msgs)
            print("2.5")
            for msg in db_msgs:
                # print("Msg : ",msg)
                print("*")
                print("sender_id : ",str(msg["sender_id"]))
                role = "user" if msg['sender_id'] != 0 else "assistant"
                chat_messages.append({"role": role, "content": msg['message']})
            chat_messages.append({"role": "user", "content": prompt})
            print("3")
            print("4")
            # print("Chat Messages3 : ",chat_messages)
        if isDotCode :
            db_msgs = [msg for msg in db_msgs if (msg['isDotCode'] != 0 and msg['isExplanation'] == 0) or (msg['isDotCode'] == 0 and msg['isExplanation'] == 0)]
            chat_messages.append({"role": "system", "content": "You are a helpful assistant expert in generating DOT language Graphviz code."})
            for msg in db_msgs:
                role = "user" if msg['sender_id'] != 0 else "assistant"
                chat_messages.append({"role": role, "content": msg['message']})
            chat_messages.append({"role": "user", "content": prompt})
        else :
            chat_messages.append({"role": "system", "content": "You are a helpful assistant expert in text classification."})
            chat_messages.append({"role": "user", "content": prompt})
        print("5")
        print("Chat Messages : ",str(chat_messages))
         # Calculate token size
        # enc = tiktoken.get_encoding("gpt-3.5-turbo")
        # token_size = sum(len(enc.encode(message["content"])) for message in chat_messages)
        # print("Token size: ", token_size)
        # if token_size > 6000:
        #     return "start_new_conversation"

        chat_completion =   client.chat.completions.create(
            # messages=[
            #     {"role": "system", "content": "You are a helpful assistant expert in the cybersecurity domain."},
            #     {"role": "user", "content": prompt},
            # ],
            messages = chat_messages,
            model="llama-3.3-70b-versatile",
            max_tokens=6000,

        )
        
        print("6")
        # print("Chat Completion : ",chat_completion.choices[0].message.content.strip())
        # if chat_completion.choices[0].message.content.strip() is not None and chat_completion.choices[0].message.content.strip() != "":
        #     # chat_messages.append({"role": "assistant", "content": chat_completion.choices[0].message.content.strip()})
        #     if isexplanation:
        #         print("7")
        #         mongodb.insert_message(conversation_id= req.conversation_id,sender_id= req.user_id,message= question,isexplanation=0, isdotcode=0 , imgid = None )
        #         mongodb.insert_message(conversation_id=req.conversation_id,sender_id= "user", message = chat_completion.choices[0].message.content.strip(),isexplanation=1 ,  isdotcode=0, imgid = None ) 
        #         print("8")
        #     if isDotCode:
        #         # db.insert_message(conversation_id= req.conversation_id,sender_id= req.user_id, message = prompt , isdotcode=0 , isexplanation=0)
        #         mongodb.insert_message(conversation_id=req.conversation_id, sender_id= "user",message= chat_completion.choices[0].message.content.strip(),isdotcode=1 , isexplanation=0 , imgid= None)
                
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        # st.error(f"API Error: {e}")
        return ""

# Function to clean Graphviz DOT code
def clean_dot_code(response: str) -> str:
    response = response.strip("```").replace("dot", "").strip()
    if not response.startswith("digraph") and not response.startswith("graph"):
        # st.error("Invalid Graphviz code received.")
        return ""
    return response

import copy
async def getDotCode(request: ChatRequest):
    try:    
        formatted_prompt_diagram_type =  PROMPT_TEMPLATE_DIAGRAM_TYPE.format(input=request.input_question)
        request2 = copy.deepcopy(request)
        request2.input_question = formatted_prompt_diagram_type
        print("request2 in getDotCode : ",request2)
        response =await query_groq(question="", req=request2, isDotCode=False , isexplanation=False)
        # Validate diagram classification response
        print("response in getDotCode : ",response)

        
        if response is None or response.strip() == "":
            response = "Herarchical Diagram"
        
        diagram_type = response.strip()

        # Get the Graphviz code
        formatted_prompt =   PROMPT_TEMPLATE_GRAPHVIZ.format(type=diagram_type, input=request.input_question)
        request3 = request
        request3.input_question = formatted_prompt
        print("request3 in getDotCode : ",request3)
        response2 = await query_groq(question="",req=request3 , isDotCode=True , isexplanation=False)
         # Validate dot_code
        if isinstance(response2, dict) and "error" in response2:
            return {"error": response2["error"]}
        if response2:
            dot_code =  clean_dot_code(response2)  # Clean the Graphviz code
            if not dot_code:
                return {"error": "Failed to generate a valid Graphviz diagram."}
            
            return dot_code

        else:
            return {"error": "Failed to generate Graphviz code."}
    except ValueError:
        return {"error": "Invalid response for diagram type classification."}
    

async def getExplaination(request: ChatRequest):
    try:
        chatReq = copy.deepcopy(request)
        question = request.input_question
        formatted_prompt_explaination =  PROMPT_TEMPLATE_PROMPT_EXPLAINATION.format(input=request.input_question)
        print("request in getExplain : ",request)
        chatReq.input_question = formatted_prompt_explaination
        print("request after change in  getExplain : ",chatReq)
        response_explaination = await query_groq(question=question, req=chatReq , isDotCode=False , isexplanation=True)
        print("Response Explaination : ",response_explaination)
        return response_explaination 
    except ValueError:
        return {"error": "Invalid response"}
    
# Prompt Templates
PROMPT_TEMPLATE_GRAPHVIZ = (
    "Generate a Graphviz DOT language code for a \"{type}\" illustrating \"{input}\". "
    "Enclose the code within triple backticks (```). "
    "No preamble or additional explanations. Only return the DOT code block."
)

PROMPT_TEMPLATE_DIAGRAM_TYPE = (
    "Classify the input \"{input}\" into one of the following diagram types based on which best represents "
    "the information in a neat, clean, and easy-to-understand manner:\n\n"
    "Flowchart\nHierarchical Diagram\nMind Map\nNetwork Diagram\nEntity-Relationship Diagram\nTable\n\n"
    "Only return the corresponding diagram type. No preamble or additional text."
)

PROMPT_TEMPLATE_PROMPT_EXPLAINATION = (
    "Explain the input prompt \"{input}\" in detail. "
    "Provide a comprehensive explanation covering the key points and concepts. "
    "Ensure the explanation is clear, concise, and easy to understand. "
    "No preamble or additional text."
)

diagram_types = [
    "Flowchart",
    "Hierarchical Diagram",
    "Mind Map",
    "Network Diagram",
    "Entity-Relationship Diagram",
    "Table"
]
