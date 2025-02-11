
import os
# import streamlit as st
from groq import Groq
import graphviz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Groq API configuration
apiKey = os.getenv("GROQ_TOKEN")
client = Groq(api_key=apiKey)

# if not apiKey:
#     st.error("Error: GROQ_TOKEN is not set. Please check your environment variables.")
#     st.stop()


# Function to query Groq API
def query_groq(prompt: str) -> str:
    try:

        print("Prompt : ",prompt)
        chat_completion =   client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant expert in the cybersecurity domain."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
        )
        print("Chat Completion : ",chat_completion.choices[0].message.content.strip())
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

async def getDotCode(input_question : str):
    try:    
        formatted_prompt_diagram_type =  PROMPT_TEMPLATE_DIAGRAM_TYPE.format(input=input_question)
        response = query_groq(formatted_prompt_diagram_type)
        response_index = int(response)
        if response_index is None:
            return {"error": "Got a null response for diagram classification."}
        if response_index not in range(len(diagram_types)):
            return {"error": "Received an invalid response for diagram classification."}

        diagram_type = diagram_types[response_index]

        # Get the Graphviz code
        formatted_prompt =   PROMPT_TEMPLATE_GRAPHVIZ.format(type=diagram_type, input=input_question)
        response2 = query_groq(formatted_prompt)
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
    

async def getExplaination(input_question : str):
    try:
        formatted_prompt_explaination =  PROMPT_TEMPLATE_PROMPT_EXPLAINATION.format(input=input_question)
        response_explaination =  query_groq(formatted_prompt_explaination)
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
