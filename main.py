from dto.CreateAccountRequest import CreateAccountRequest
from dto.CreateConversationRequest import CreateConversationRequest
from dto.GetConversationsRequest import GetConversationsRequest
from dto.GetMessagesRequest import GetMessagesRequest
from dto.LoginRequest import LoginRequest
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import base64
import tempfile
import Dev_CodeForsight as model
import setArg as setArg
from dto.ChatRequest import ChatRequest
from dto.GraphRequest import GraphRequest
from dto.SetArgRequest import SetArgRequest
import MongoDB_database as mongodb
import asyncio

# Define the FastAPI app
app = FastAPI()

# Initialize the MongoDB database
@app.on_event("startup")
async def startup_event():
    print("Initializing MongoDB database")
    await mongodb.initialize_database()
    print("MongoDB database initialized")

async def convertImgToBase64(dot_code: str) -> str:
    """
    Converts a Graphviz DOT code string into a base64-encoded PNG image.
    """
    try:
        process = subprocess.run(
            ["dot", "-Tpng"],
            input=dot_code.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if process.returncode != 0:
            return {"error": process.stderr.decode()}
        return base64.b64encode(process.stdout).decode("utf-8")
    except Exception as e:
        # raise HTTPException(status_code=500, detail=str(e))
        return {"error": str(e)}

@app.post("/codeforsight/v1/chat/")
async def chat(request: ChatRequest):
    try:
        await mongodb.insert_message(request.conversation_id, request.user_id, request.input_question )
        
        explanation = await model.getExplaination(request)
        
        if explanation is not None:
            await mongodb.insert_message(request.conversation_id, "admin", explanation , isExplanation=1)
        else :
            await mongodb.insert_message(request.conversation_id, "admin", "No explanation found." , isExplanation=1)
        
        dot_code = await model.getDotCode(request)
        print("************",dot_code , "************")
        print(dot_code)
        if dot_code is not None:
            await mongodb.insert_message(request.conversation_id, "admin", dot_code , isDotCode=1)
        else:
            await mongodb.insert_message(request.conversation_id, "admin", "Incorrect or No Dot Code generated." , isDotCode=1)
        encodedData = await convertImgToBase64(dot_code)
        if encodedData is not None:
            imgid = await mongodb.insert_image("admin", request.conversation_id, encodedData)
            print("Image ID : ",imgid)
            # if imgid is not None:
            await mongodb.insert_message(request.conversation_id, "admin", encodedData, img_id = imgid, isImage=1)
        else:
            await mongodb.insert_message(request.conversation_id, "admin", "No Image Found." , isImage=1)
        return {"explanation": explanation, "dot_code": dot_code, "image_base64": encodedData}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/codeforsight/v1/setToken/")
async def setToken(token: SetArgRequest):
    try:
        setArg.set_env_token(token.key, token.val)
        return {"message": "Token updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/codeforsight/v1/login/")
async def login(request: LoginRequest):
    user_data = await mongodb.check_login(request)
    print(user_data)
    if user_data:
        res = {
            
            "userid": str(user_data["_id"]),
            "username": user_data["username"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"]
        }
        return {"message": "Login successful.", "user": res}
    raise HTTPException(status_code=500, detail="Invalid username or password")

@app.post("/codeforsight/v1/createAccount/")
async def create_account(request: CreateAccountRequest):
    try:
        await mongodb.insert_user(request)
        return {"message": "Account created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/codeforsight/v1/getAllConversations/")
async def get_all_conversations(request: GetConversationsRequest):
    try:
        conversations = await mongodb.get_all_conversations(request.user_id)
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/codeforsight/v1/getAllMessages/")
async def get_all_messages(request: GetMessagesRequest):
    try:
        messages = await mongodb.get_all_messages(request.conversation_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/codeforsight/v1/createConversation/")
async def create_conversation(request: CreateConversationRequest):
    try:
        conversation_id = await mongodb.insert_conversation(request.user_id, request.conversation_name)
        return {"conversation_id": conversation_id, "conversation_name": request.conversation_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# from dto.CreateAccountRequest import CreateAccountRequest
# from dto.CreateConversationRequest import CreateConversationRequest
# from dto.GetConversationsRequest import GetConversationsRequest
# from dto.GetMessagesRequest import GetMessagesRequest
# from dto.LoginRequest import LoginRequest
# from fastapi import FastAPI , HTTPException
# from pydantic import BaseModel
# import subprocess
# import base64
# import tempfile
# import Dev_CodeForsight as model
# import setArg as setArg
# from dto.ChatRequest import ChatRequest
# from dto.GraphRequest import GraphRequest
# from dto.SetArgRequest import SetArgRequest
# import Database as db
# import MongoDB_database as mongodb
# import asyncio
# # Define the FastAPI app
# app = FastAPI()

# # Initailize the database
# db.initialize_database()
# # mongodb.initialize_database()
# @app.on_event("startup")
# async def startup_event():
#     print("Initializing MongoDB database")
#     await mongodb.initialize_database()
#     print("MongoDB database initialized")


# async def convertImgToBase64(dot_code: str) -> dict:
#     """
#     Converts a Graphviz DOT code string into a base64-encoded PNG image.

#     Args:
#         dot_code (str): The Graphviz DOT code.

#     Returns:
#         dict: A dictionary containing either the base64 image string or an error message.
#     """
#     try:
#         # Create a temporary file for the PNG output
#         with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_png:
#             # Run Graphviz without saving to disk
#             process = subprocess.run(
#                 ["dot", "-Tpng"],
#                 input=dot_code.encode(),
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )

#             # Check for Graphviz errors
#             if process.returncode != 0:
#                 return {"error": process.stderr.decode()}

#             # Encode the image in base64
#             encoded_image = base64.b64encode(process.stdout).decode("utf-8")
     
#         return encoded_image

#     except Exception as e:
#         return HTTPException(status_code=500, detail=str(e))


# @app.post("/codeforsight/v1/chat/")
# async def chat(request: ChatRequest):
#     try:
#         print("Request : ",request)
#         explanation = await model.getExplaination(request)
#         # print("Explanation : ",explanation)
#         dot_code = await model.getDotCode(request)
#         # print("Dot Code : ",dot_code)
#         encodedData = await convertImgToBase64(dot_code)
#         # print("EncodedData : ",encodedData)
#         if encodedData is not None : 
#             imgid = db.insert_img(img_base64=encodedData,user_id=1,conversation_id=request.conversation_id)
#             db.insert_message(conversation_id=request.conversation_id,sender_id=request.user_id,message=encodedData,isexplanation=0,isdotcode=1, imgid=  imgid)    
#         # print("EncodedData : ",encodedData , "Dot Code : ",dot_code , "Explanation : ",explanation)
#         return {
#             "explanation": explanation,
#             "dot_code": dot_code,
#             "image_base64": encodedData
#         }
#     except Exception as e:
#         return HTTPException(status_code=500, detail=str(e))



# @app.post("/codeforsight/v1/setToken/")
# async def setToken(token: SetArgRequest):
#     try:
#         setArg.set_env_token(token.key, token.val)
#         return {"message": "Token updated successfully."}
#     except Exception as e:
#         return HTTPException(status_code=500, detail=str(e))
    
# @app.post("/codeforsight/v1/login/")
# async def login(request: LoginRequest):
#     user_data = db.check_login(request)
#     if user_data:
#         user_dict = {
#             "userid": user_data[0],
#             "first_name": user_data[2],
#             "last_name": user_data[3]
#         }
#         return {"message": "Login successful.", "user": user_dict}
#     else:
#         raise HTTPException(status_code=500, detail="Invalid username or password")
    

# @app.post("/codeforsight/v1/createAccount/")
# async def create_account(request: CreateAccountRequest):
#     try:
#         print(request)
#         db.insert_user(request)
#         return {"message": "Account created successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/codeforsight/v1/getAllConversations/")
# async def get_all_conversations(request: GetConversationsRequest):
#     try:
#         conversations = db.get_all_conversations(request)
#         return {"conversations": conversations}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/codeforsight/v1/getAllMessages/")
# async def get_all_messages(request: GetMessagesRequest):
#     try:
#         messages = db.get_messages(request)
#         return {"messages": messages}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# #create conv
# @app.post("/codeforsight/v1/createConversation/")
# async def create_conversation(request: CreateConversationRequest):
#     try:
#         conversation = db.insert_conversation(request.user_id , request.conversation_name)
#         print("Conversation : ",conversation)
#         return {"conversation_id": conversation[0], "conversation_name": conversation[1]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # @app.post("/codeforsight/v1/updateConversation/")
# # async def update_conversation(request: CreateConversationRequest):
# #     try:
# #         conversation_id = db.update_conversation(request.user_id , request.conversation_name)
# #         return {"conversation_id": conversation_id , }
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))
