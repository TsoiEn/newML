import sys
import os
import pickle  # Add pickle import to serialize the encrypted values

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import csv
from data.data_config import db_cred
from encryption.homomorphic import generate_keys, encrypt_value, save_keys, load_keys
from mappings import (
    GENDER_MAP, FEVER_MAP, COUGH_MAP, FATIGUE_MAP, 
    DIFFICULTY_BREATHING_MAP, BLOOD_PRESSURE_MAP, CHOLESTEROL_LEVEL_MAP
)

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

# Transform and encrypt data
def transform_and_encrypt(row, transform_count, encrypt_count, public_key):
    """
    Transforms the row based on the mapping rules and encrypts certain values.
    Args:
        row (list): A row of data read from the CSV file.
        transform_count (int): Counter for how many rows have been transformed.
        encrypt_count (int): Counter for how many rows have been encrypted.
        public_key: The Paillier public key used for encryption.
    Returns:
        tuple: Transformed and encrypted row, updated counters.
    """
    print(f"Processing row: {transform_count + 1}...")

    # Map the values using the mappings
    transformed_row = [
        row[0],  # Disease (no transformation or encryption)
        GENDER_MAP.get(row[1], None),
        FEVER_MAP.get(row[2], None),
        COUGH_MAP.get(row[3], None),
        FATIGUE_MAP.get(row[4], None),
        DIFFICULTY_BREATHING_MAP.get(row[5], None),
        int(row[6]),  # Age
        BLOOD_PRESSURE_MAP.get(row[7], None),
        CHOLESTEROL_LEVEL_MAP.get(row[8], None),
        row[9]  # Outcome Variable
    ]

    # Check for missing mappings
    if None in transformed_row:
        return None  # Indicates an issue in the mapping

    # Encrypt specific values and serialize them
    encrypted_row = [
        transformed_row[0],  # Disease (no encryption)
        pickle.dumps(encrypt_value(public_key, transformed_row[1])),  # Serialize Encrypted Gender
        pickle.dumps(encrypt_value(public_key, transformed_row[2])),  # Serialize Encrypted Fever
        pickle.dumps(encrypt_value(public_key, transformed_row[3])),  # Serialize Encrypted Cough
        pickle.dumps(encrypt_value(public_key, transformed_row[4])),  # Serialize Encrypted Fatigue
        pickle.dumps(encrypt_value(public_key, transformed_row[5])),  # Serialize Encrypted Difficulty Breathing
        pickle.dumps(encrypt_value(public_key, transformed_row[6])),  # Serialize Encrypted Age
        pickle.dumps(encrypt_value(public_key, transformed_row[7])),  # Serialize Encrypted Blood Pressure
        pickle.dumps(encrypt_value(public_key, transformed_row[8])),  # Serialize Encrypted Cholesterol Level
        transformed_row[9]  # Outcome Variable (no encryption)
    ]

    transform_count += 1
    encrypt_count += 1
    print(f"Row {encrypt_count} encrypted.")
    
    return encrypted_row, transform_count, encrypt_count

# Insert CSV into MySQL
def insert_csv_to_db(file_path):
    print(f"Starting to insert data from {file_path}...")
    
    # Load or generate keys
    public_key, private_key = load_or_generate_keys()

    transform_count = 0  # Counter for rows transformed
    encrypt_count = 0  # Counter for rows encrypted
    rows_inserted = 0  # Counter for rows inserted into the database

    with open(file_path, 'r') as file:
        csv_data = csv.reader(file)
        next(csv_data)  # Skip the header row

        for row in csv_data:
            transformed_row, transform_count, encrypt_count = transform_and_encrypt(row, transform_count, encrypt_count, public_key)
            if not transformed_row:  # Skip rows with missing mappings
                continue
            
            sql = """
            INSERT INTO disease_data (
                Disease, Gender, Fever, Cough, Fatigue, Difficulty_Breathing, Age, Blood_Pressure, Cholesterol_Level, Outcome_Variable
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(sql, tuple(transformed_row))
            rows_inserted += 1
        
        db.commit()
        print(f"Inserted {rows_inserted} rows.")
        print(f"Total transformed rows: {transform_count}")
        print(f"Total encrypted rows: {encrypt_count}")

# Call the function
file_path = '/home/tsoien/github/newML/backend/data/Disease_symptom_and_patient_profile_dataset.csv' 
insert_csv_to_db(file_path)

cursor.close()
db.close()
