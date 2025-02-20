
import os
# import streamlit as st
from dto.ChatRequest import ChatRequest
from dto.GetMessagesRequest import GetMessagesRequest
from groq import Groq
import graphviz
from dotenv import load_dotenv
import Database  as db
# import tiktoken


# Load environment variables from .env file
load_dotenv()

# Groq API configuration
apiKey = os.getenv("GROQ_TOKEN")
client = Groq(api_key=apiKey)

# if not apiKey:
#     st.error("Error: GROQ_TOKEN is not set. Please check your environment variables.")
#     st.stop()


# Function to query 
def query_groq(question : str,req: ChatRequest , isDotCode: bool , isexplanation : bool ) -> str:
    try:
        # print("Request : ",req)
        # print("isDotCode : ",isDotCode)
        # print("isexplanation : ",isexplanation)
        prompt : str = req.input_question
        # print("Prompt : ",prompt)
        req =  GetMessagesRequest(
            conversation_id = req.conversation_id,
            user_id =req.user_id
        )
        chat_messages = []

        print("1")       
        db_msgs = db.get_messages(req)
        # print("DB Messages : ",str(db_msgs))
        db_msgs = db_msgs or [] 
        print("2")       
        if isexplanation :
            db_msgs = [msg for msg in db_msgs if (msg['isexplanation'] != 0 and msg['isdotcode'] == 0) or (msg['isexplanation'] == 0 and msg['isdotcode'] == 0)]
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
            db_msgs = [msg for msg in db_msgs if (msg['isdotcode'] != 0 and msg['isexplanation'] == 0) or (msg['isdotcode'] == 0 and msg['isexplanation'] == 0)]
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
        if chat_completion.choices[0].message.content.strip() is not None and chat_completion.choices[0].message.content.strip() != "":
            # chat_messages.append({"role": "assistant", "content": chat_completion.choices[0].message.content.strip()})
            if isexplanation:
                print("7")
                db.insert_message(conversation_id= req.conversation_id,sender_id= req.user_id,message= question,isexplanation=0, isdotcode=0 , imgid = None )
                db.insert_message(conversation_id=req.conversation_id,sender_id= 1, message = chat_completion.choices[0].message.content.strip(),isexplanation=1 ,  isdotcode=0, imgid = None ) 
                print("8")
            if isDotCode:
                # db.insert_message(conversation_id= req.conversation_id,sender_id= req.user_id, message = prompt , isdotcode=0 , isexplanation=0)
                db.insert_message(conversation_id=req.conversation_id, sender_id= 1,message= chat_completion.choices[0].message.content.strip(),isdotcode=1 , isexplanation=0 , imgid= None)
                
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

async def getDotCode(request: ChatRequest):
    try:    
        formatted_prompt_diagram_type =  PROMPT_TEMPLATE_DIAGRAM_TYPE.format(input=request.input_question)
        request2 = request
        request2.input_question = formatted_prompt_diagram_type
        response = query_groq(question="", req=request2, isDotCode=False , isexplanation=False)
        # Validate diagram classification response
        response_index = int(response)
        if response_index is None:
            return {"error": "Got a null response for diagram classification."}
        if response_index not in range(len(diagram_types)):
            response_index = 0
            # return {"error": "Received an invalid response for diagram classification."}

        diagram_type = diagram_types[response_index]

        # Get the Graphviz code
        formatted_prompt =   PROMPT_TEMPLATE_GRAPHVIZ.format(type=diagram_type, input=request.input_question)
        request3 = request
        request3.input_question = formatted_prompt
        response2 = query_groq(question="",req=request3 , isDotCode=True , isexplanation=False)
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
        question = request.input_question
        formatted_prompt_explaination =  PROMPT_TEMPLATE_PROMPT_EXPLAINATION.format(input=request.input_question)
        print("request in getExplain : ",request)
        request.input_question = formatted_prompt_explaination
        print("request after change in  getExplain : ",request)
        response_explaination =  query_groq(question=question, req=request , isDotCode=False , isexplanation=True)
        print("Response Explaination : ",response_explaination)
        return response_explaination 
    except ValueError:
        return {"error": "Invalid response"}
    
# Prompt Templates
PROMPT_TEMPLATE_GRAPHVIZ = (
    "Generate a Detailed Graphviz DOT language code for a \"{type}\" illustrating \"{input}\". "
    "Enclose the code within triple backticks (```). "
    "No preamble or additional explanations. Only return the DOT code block."
)

PROMPT_TEMPLATE_DIAGRAM_TYPE = (
    "Classify the input \"{input}\" into one of the following diagram types based on which best represents "
    "the information in a neat, clean, and easy-to-understand manner:\n\n"
    "0 - Flowchart\n1 - Hierarchical Diagram\n2 - Mind Map\n3 - Network Diagram\n4 - Entity-Relationship Diagram\n5 - Table\n\n"
    "Only return the corresponding number (0, 1, 2, 3, 4, or 5). No preamble or additional text."
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

# # Streamlit Interface
# st.title("CodeForsight-AI Cybersecurity Model")
# st.subheader("Input your cybersecurity-related query or scenario below.")

# # Input Section
# input_question = st.text_area("Enter your question/scenario:")

# if st.button("Generate Diagram"):
#     if input_question.strip():
#         with st.spinner("Processing..."):
#             formatted_prompt_diagram_type = PROMPT_TEMPLATE_DIAGRAM_TYPE.format(input=input_question)
#             response = query_groq(formatted_prompt_diagram_type)

#             formatted_prompt_explaination = PROMPT_TEMPLATE_PROMPT_EXPLAINATION.format(input=input_question)
#             response_explaination = query_groq(formatted_prompt_explaination)

#             try:
#                 print("Response : ",response )
#                 if isinstance(response, dict) and "error" in response:
#                     st.error(response["error"])
#                     st.stop()
#                 response_index = int(response)
#                 if response_index not in range(len(diagram_types)):
#                     st.error("Received an invalid response for diagram classification.")
#                     st.stop()

#                 diagram_type = diagram_types[response_index]

#                 # Get the Graphviz code
#                 formatted_prompt = PROMPT_TEMPLATE_GRAPHVIZ.format(type=diagram_type, input=input_question)
#                 response = query_groq(formatted_prompt)

#                 if response:
#                     dot_code = clean_dot_code(response)  # Clean the Graphviz code
#                     if not dot_code:
#                         st.error("Failed to generate a valid Graphviz diagram.")
#                         st.stop()

#                     # Render and display the Graphviz diagram
#                     dot = graphviz.Source(dot_code)
#                     dot_path = "generated_graph"
#                     dot.render(dot_path, format="png", cleanup=True)  # Save as PNG

#                     # Display the image
#                     st.subheader("Visual Representation")
#                     st.image(f"{dot_path}.png")

#                     # Display the Graphviz code
#                     st.subheader("Explanation")
#                     st.write(response_explaination)

#                 else:
#                     st.error("Failed to generate Graphviz code.")

#             except ValueError:
#                 st.error("Invalid response for diagram type classification.")
#     else:
#         st.warning("Please enter a question or scenario.")
