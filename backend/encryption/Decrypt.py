import sys
import os
import pickle  # Add pickle import to deserialize the encrypted values
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mysql.connector
from data.data_config import db_cred
from encryption.homomorphic import generate_keys, decrypt_value, save_keys, load_keys  # Assuming these exist
from phe import paillier

# Check if keys exist, load or generate
def load_or_generate_keys():
    try:
        public_key, private_key = load_keys()  # Attempt to load keys from disk
    except FileNotFoundError:
        print("Keys not found, generating new keys...")
        public_key, private_key = generate_keys()  # Generate new keys if not found
        save_keys(public_key, private_key)  # Save the generated keys
    return public_key, private_key

# Database connection
db = db_cred()
cursor = db.cursor()

# Decrypt the data retrieved from MySQL
def decrypt_data_from_db(public_key, private_key):
    print("Fetching and decrypting data from the database...")

    # Query to fetch the encrypted data from the database
    query = """
    SELECT Disease, Gender, Fever, Cough, Fatigue, Difficulty_Breathing, Age, Blood_Pressure, Cholesterol_Level, Outcome_Variable
    FROM disease_data LIMIT 5;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    decrypted_rows = []

    # Decrypt each row
    for row in rows:
        decrypted_row = [
            row[0],  # Disease (no decryption)
            decrypt_value(private_key, pickle.loads(row[1])),  # Deserialize and Decrypt Gender
            decrypt_value(private_key, pickle.loads(row[2])),  # Deserialize and Decrypt Fever
            decrypt_value(private_key, pickle.loads(row[3])),  # Deserialize and Decrypt Cough
            decrypt_value(private_key, pickle.loads(row[4])),  # Deserialize and Decrypt Fatigue
            decrypt_value(private_key, pickle.loads(row[5])),  # Deserialize and Decrypt Difficulty Breathing
            int(decrypt_value(private_key, pickle.loads(row[6]))),  # Deserialize and Decrypt Age
            decrypt_value(private_key, pickle.loads(row[7])),  # Deserialize and Decrypt Blood Pressure
            decrypt_value(private_key, pickle.loads(row[8])),  # Deserialize and Decrypt Cholesterol Level
            row[9]  # Outcome Variable (no decryption)
        ]
        decrypted_rows.append(decrypted_row)

    # Print the decrypted rows
    for decrypted_row in decrypted_rows:
        print(decrypted_row)

# Call the decryption function
def main():
    # Step 1: Load or generate keys
    public_key, private_key = load_or_generate_keys()

    # Step 2: Decrypt data from the database
    decrypt_data_from_db(public_key, private_key)

# Run the script
if __name__ == '__main__':
    main()

# Close the cursor and the database connection
cursor.close()
db.close()
