from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import base64
import tempfile
import Dev_CodeForsight as dc

app = FastAPI()

# Define request body model
class GraphRequest(BaseModel):
    dot_code: str
class ChatRequest(BaseModel):
    input_question: str

# async def convertImgToBase64(request: GraphRequest):
#     # Create a temporary file for the PNG output
#     with tempfile.NamedTemporaryFile(suffix=".png") as temp_png:
#         # Run Graphviz without saving to disk
#         process = subprocess.run(
#             ["dot", "-Tpng"],
#             input=request.dot_code.encode(),
#             stdout=temp_png,
#             stderr=subprocess.PIPE
#         )

#         # Check for Graphviz errors
#         if process.returncode != 0:
#             return {"error": process.stderr.decode()}

#         # Read the image from the temporary file
#         temp_png.seek(0)
#         encoded_image = base64.b64encode(temp_png.read()).decode("utf-8")

#     return {"image_base64": encoded_image}

async def convertImgToBase64(dot_code: str) -> dict:
    """
    Converts a Graphviz DOT code string into a base64-encoded PNG image.

    Args:
        dot_code (str): The Graphviz DOT code.

    Returns:
        dict: A dictionary containing either the base64 image string or an error message.
    """
    try:
        # Create a temporary file for the PNG output
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_png:
            # Run Graphviz without saving to disk
            process = subprocess.run(
                ["dot", "-Tpng"],
                input=dot_code.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Check for Graphviz errors
            if process.returncode != 0:
                return {"error": process.stderr.decode()}

            # Encode the image in base64
            encoded_image = base64.b64encode(process.stdout).decode("utf-8")

        return encoded_image

    except Exception as e:
        return {"error": str(e)}


@app.post("/codeforsight/v1/chat/")
async def chat(input_question: ChatRequest):
    try:
        explanation = await dc.getExplaination(input_question.input_question)
        print("5")
        print("Explanation output : ",explanation)
        print("6")
        dot_code = await dc.getDotCode(input_question.input_question)
        print("Dot Code output : ",dot_code    )
        encodedData = await convertImgToBase64(dot_code)
        print("EncodedData : ",encodedData , "Dot Code : ",dot_code , "Explanation : ",explanation)
        return {
            "explanation": explanation,
            "dot_code": dot_code,
            "image_base64": encodedData
        }
    except Exception as e:
        return {"error": str(e)}