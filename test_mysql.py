import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        # Try to connect without specifying a database first
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345"  # Change this to your MySQL root password
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL server!")
            
            # Check if the database exists
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES LIKE 'english_training'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Database 'english_training' exists")
            else:
                print("ℹ️ Database 'english_training' does not exist")
                create_db = input("Would you like to create it? (y/n): ")
                if create_db.lower() == 'y':
                    cursor.execute("CREATE DATABASE english_training")
                    print("✅ Database 'english_training' created successfully")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure MySQL server is running")
        print("2. Verify your MySQL username and password")
        print("3. Check if your MySQL user has the necessary permissions")
        print("4. Try connecting with MySQL Workbench or MySQL CLI to verify credentials")

if __name__ == "__main__":
    print("🔍 Testing MySQL connection...")
    test_connection()
