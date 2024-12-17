from data_config import db_cred

def test_connection():
    try:
        db = db_cred()  # Attempt to connect
        if db.is_connected():
            print("Successfully connected to the database!")
        else:
            print("Failed to connect to the database.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'db' in locals() and db.is_connected():
            db.close()  # Close the connection
            print("Connection closed.")

# Run the test
if __name__ == "__main__":
    test_connection()
