import sqlite3

from dto.CreateAccountRequest import CreateAccountRequest
from dto.GetConversationsRequest import GetConversationsRequest
from dto.GetMessagesRequest import GetMessagesRequest
from dto.LoginRequest import LoginRequest 
import Dev_CodeForsight as model


def initialize_database():
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('codeForsightDB.db')
    
    cursor = conn.cursor()

    # Create the users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL , 
        first_name TEXT ,
        last_name TEXT ,
        acc_creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Check if the users table is empty
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        # Insert the admin user
        cursor.execute('''
            INSERT INTO users (username, password, first_name, last_name)
            VALUES ('admin', 'admin', 'admin', 'admin')
        ''')

    # Create the conversations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_name TEXT ,
        user_id INTEGER NOT NULL,
        conversation_creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # Create the messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        img_id INTEGER DEFAULT NULL,
        isexplanation INTEGER DEFAULT 0,
        isdotcode INTEGER DEFAULT 0,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id),
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (img_id) REFERENCES images(id)
    )
    ''')

    # Create the images table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        conversation_id INTEGER NOT NULL,
        image_base64 TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Database initialized")

def get_all_conversations(request: GetConversationsRequest):
    conn = sqlite3.connect('codeForsightDB.db')
    print("Request : ",request)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM conversations
    WHERE user_id = ?
    ORDER BY conversation_creation_timestamp
    ''',(str(request.user_id),))
    conversations = cursor.fetchall()
    conn.close()
    mapList = []
    for conv in conversations:
        mapList.append({
            "id": conv[0],
            "conversation_name": conv[1],
            "user_id": conv[2],
            "conversation_creation_timestamp": conv[3]
        })
    return mapList

def get_messages(request: GetMessagesRequest):
    conn = sqlite3.connect('codeForsightDB.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT *
    FROM messages
    WHERE conversation_id = ? 
    AND sender_id = ?
    ORDER BY timestamp
    ''', (request.conversation_id,request.user_id))
    messages = cursor.fetchall()
    conn.close()
    # print("Messages : ",messages)
    mapList = []
    for msg in messages:
        mapList.append({
            "id": msg[0],
            "conversation_id": msg[1],
            "sender_id": msg[2],
            "message": msg[3],
            "timestamp": msg[4],
            "img_id": msg[5],
            "isexplanation": msg[6],
            "isdotcode": msg[7]
        })
    return mapList

def insert_message(conversation_id, sender_id, message, isexplanation, isdotcode , imgid):
    try:
        conn = sqlite3.connect('codeForsightDB.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO messages (conversation_id, sender_id, message, isexplanation, isdotcode , img_id)
        VALUES (?, ?, ?, ?, ?,?)
        ''', (conversation_id, sender_id, message, isexplanation, isdotcode , imgid))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        print("Message inserted with ID:", inserted_id)
        return inserted_id
    except Exception as e:
        print("Error inserting message:", e)
        return None

def insert_conversation(user_id , conversation_name):
    conn = sqlite3.connect('codeForsightDB.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO conversations (user_id, conversation_name)
    VALUES (? , ? )
    ''', (user_id,conversation_name))
    conversation_id = cursor.lastrowid
    # Retrieve the full row of the newly inserted conversation
    cursor.execute('''
    SELECT * FROM conversations WHERE id = ?
    ''', (conversation_id,))
    conversation = cursor.fetchone()
    conn.commit()
    conn.close()
    print("Conversation inserted : ",conversation)
    return conversation

def update_conversation(user_id ,conversation_id, conversation_name):
    conn = sqlite3.connect('codeForsightDB.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE conversations
    SET conversation_name = ?
    WHERE user_id = ? AND id = ?
    ''', (conversation_name, user_id, conversation_id))
    conn.commit()
    conn.close()
    return cursor.lastrowid 

def insert_user( user : CreateAccountRequest ):
    conn = sqlite3.connect('codeForsightDB.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (username, password, first_name, last_name )
    VALUES (?, ?, ? ,?)
    ''', (user.username, user.password , user.first_name , user.last_name))
    conn.commit()
    conn.close()
    print("User inserted")

def check_login(user: LoginRequest):
    conn = sqlite3.connect('codeForsightDB.db')
    cursor = conn.cursor()
    print("User : ",user)
    cursor.execute('''
    SELECT * FROM users WHERE username = ? AND password = ?
    ''', (user.username, user.password))

    user_data = cursor.fetchone()
    print("User Data" + str(user_data))
    conn.close()

    return user_data

# def setImgID(user_id , conversation_id, img_id):
#     try : 
#         conn = sqlite3.connect('codeForsightDB.db')
#         cursor = conn.cursor()
#         print("Setting image ID")
#         print("Model Image ID : ",model.imgMessageId)
#         print("User ID : ",user_id)
#         print("Conversation ID : ",conversation_id)
#         print("Image ID : ",img_id)
#         cursor.execute('''
#         UPDATE messages
#         SET img_id = ?
#         WHERE id = ? 
#         ''', (img_id , model.imgMessageId))
#         conn.commit()
#         conn.close()
#     except Exception as e:
#         print("Error setting image ID:", e)
#         return None

def insert_img(user_id, conversation_id, img_base64):
    try:
        conn = sqlite3.connect('codeForsightDB.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO images (user_id, conversation_id, image_base64)
        VALUES (?, ?, ?)
        ''', (user_id, conversation_id, img_base64))
        # setImgID(user_id, conversation_id, cursor.lastrowid)
        conn.commit()
        conn.close()
        return cursor.lastrowid
    except Exception as e :
        print("Error inserting image:", e)
        return None