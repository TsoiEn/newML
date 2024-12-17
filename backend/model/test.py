import os
import sys
import pandas as pd
from phe import paillier
import pickle  # For serializing and deserializing objects

# Add data directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import database credentials
from data.data_config import db_cred
from encryption.homomorphic import generate_keys, decrypt_value

# Deserialize an encrypted number
def deserialize_encrypted_number(encrypted_str, public_key):
    try:
        # Attempt deserialization from a hex string
        encrypted_bytes = bytes.fromhex(encrypted_str)
        encrypted_number = pickle.loads(encrypted_bytes)
        if not isinstance(encrypted_number, paillier.EncryptedNumber):
            raise ValueError("Deserialized object is not an EncryptedNumber.")
        return encrypted_number
    except Exception as e:
        print(f"Deserialization failed for input: {encrypted_str}. Error: {e}")
        return None

# Fetch encrypted data from a database
def fetch_encrypted_data(query):
    db = db_cred()  # Establish connection using db_cred
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    cursor.close()
    db.close()
    return pd.DataFrame(rows, columns=column_names)

# Decrypt specific columns in the DataFrame
def decrypt_data(df, private_key, public_key, encrypted_columns):
    decrypted_df = df.copy()
    for col in encrypted_columns:
        decrypted_df[col] = decrypted_df[col].apply(
            lambda x: decrypt_value(private_key, deserialize_encrypted_number(x, public_key)) if x else None
        )
    return decrypted_df

# Main function
def main():
    # Generate or load keys
    public_key, private_key = generate_keys()

    # Fetch encrypted data
    query = "SELECT * FROM disease_data;"
    encrypted_data = fetch_encrypted_data(query)

    # Specify encrypted columns
    encrypted_columns = ['Gender', 'Fever', 'Cough', 'Fatigue', 'Difficulty_Breathing', 'Age', 'Blood_Pressure', 'Cholesterol_Level']

    # Decrypt data
    decrypted_data = decrypt_data(encrypted_data, private_key, public_key, encrypted_columns)

    print("Decrypted Data:")
    print(decrypted_data.head())

if __name__ == "__main__":
    main()
