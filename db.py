import sqlite3
import json

def create_connection():
    connection = sqlite3.connect('midterm.db')
    cursor = connection.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY,
        user_name TEXT NOT NULL UNIQUE,
        user_password TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Conversation (
        id INTEGER PRIMARY KEY,
        conversation TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES User(id)
    )
    ''')
    
    connection.commit()
    return connection

def check_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT user_password FROM User WHERE user_name = ?', (username,))
    result = cursor.fetchone()
    
    connection.close()
    
    if result:
        if result[0] == password:
            return "Login successful"
        else:
            return "Incorrect password"
    else:
        return "User not found"

def insert_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT id FROM User WHERE user_name = ?', (username,))
    result = cursor.fetchone()
    if result:
        connection.close()
        return "Username already exists"
    
    try:
        cursor.execute('INSERT INTO User (user_name, user_password) VALUES (?, ?)', (username, password))
        connection.commit()
        return "User created successfully"
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        connection.close()

def get_user_id(username):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT id FROM User WHERE user_name = ?', (username,))
    result = cursor.fetchone()
    
    connection.close()
    
    if result:
        return result[0]  
    else:
        return None  


def get_conversation(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT conversation FROM Conversation WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    connection.close()
    
    if result and result[0]:  
        return json.loads(result[0])  
    else:
        return None  
    
def update_conversation(user_id, messages):
    connection = create_connection()
    cursor = connection.cursor()
    
    conversation_json = json.dumps(messages)
    
    cursor.execute('SELECT id FROM Conversation WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if result:
        cursor.execute('''
            UPDATE Conversation
            SET conversation = ?
            WHERE user_id = ?
        ''', (conversation_json, user_id))
    else:
        cursor.execute('''
            INSERT INTO Conversation (conversation, user_id)
            VALUES (?, ?)
        ''', (conversation_json, user_id))
    
    connection.commit()
    connection.close()

def delete_conversation(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Conversation WHERE user_id = ?', (user_id,))
    
    connection.commit()
    connection.close()
