import sqlite3
import json

# Database connection and initialization function
def create_connection():
    connection = sqlite3.connect('midterm.db')
    cursor = connection.cursor()
    
    # Create User table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY,
        user_name TEXT NOT NULL UNIQUE,
        user_password TEXT NOT NULL
    )
    ''')
    
    # Create Conversation table if not exists
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

# Check if a user exists with the provided username and password
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

# Insert a new user into the User table
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
        return result[0]  # 返回用戶的 ID
    else:
        return None  # 如果用戶不存在，返回 None


def get_conversation(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT conversation FROM Conversation WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    connection.close()
    
    if result and result[0]:  # 檢查是否有對話紀錄
        return json.loads(result[0])  # 將 JSON 字符串轉換為 Python 列表
    else:
        return None  # 如果沒有對話紀錄，返回 None
    
def update_conversation(user_id, messages):
    connection = create_connection()
    cursor = connection.cursor()
    
    # 將 messages 列表轉換為 JSON 字符串
    conversation_json = json.dumps(messages)
    
    cursor.execute('SELECT id FROM Conversation WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if result:
        # 如果已有對話紀錄，進行更新
        cursor.execute('''
            UPDATE Conversation
            SET conversation = ?
            WHERE user_id = ?
        ''', (conversation_json, user_id))
    else:
        # 如果沒有對話紀錄，進行插入
        cursor.execute('''
            INSERT INTO Conversation (conversation, user_id)
            VALUES (?, ?)
        ''', (conversation_json, user_id))
    
    connection.commit()
    connection.close()