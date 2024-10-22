import sqlite3

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
