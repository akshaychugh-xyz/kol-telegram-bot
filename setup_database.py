import sqlite3

def setup_database():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        referral_code TEXT,
        deposited INTEGER DEFAULT 0
    )
    ''')

    # Insert dummy data
    dummy_data = [
        ('user1@example.com', 'REF001', 1),
        ('user2@example.com', 'REF002', 0),
        ('user3@example.com', 'REF003', 1),
    ]

    cursor.executemany('''
    INSERT OR REPLACE INTO users (email, referral_code, deposited)
    VALUES (?, ?, ?)
    ''', dummy_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    print("Database setup complete with dummy data.")