from dotenv import load_dotenv, set_key
import os

def set_env_token(key, value, env_path='.env'):
   
    # Load the .env file
    load_dotenv(dotenv_path=env_path)

    # Set the new value for the key
    set_key(env_path, key, value)

    # print(f"Updated {key} to {value} in {env_path}")

# if __name__ == "__main__":
#     set_env_token('GROQ_TOKEN', 'new_value2')