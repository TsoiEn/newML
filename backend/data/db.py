import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import csv
from data.data_config import db_cred
from encryption.homomorphic import generate_keys, encrypt_value
from mappings import (
    GENDER_MAP, FEVER_MAP, COUGH_MAP, FATIGUE_MAP, 
    DIFFICULTY_BREATHING_MAP, BLOOD_PRESSURE_MAP, CHOLESTEROL_LEVEL_MAP
)

# Generate Paillier keys (public and private)
public_key, private_key = generate_keys()

# Database connection
db = db_cred()
cursor = db.cursor()

# Transform and encrypt data
def transform_and_encrypt(row):
    """
    Transforms the row based on the mapping rules and encrypts certain values.
    Args:
        row (list): A row of data read from the CSV file.
    Returns:
        list: A transformed and encrypted row ready for insertion.
    """
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
    
    # Encrypt specific values (Gender, Fever, Cough, Fatigue, Difficulty_Breathing, Age, Blood_Pressure, Cholesterol_Level)
    encrypted_row = [
        transformed_row[0],  # Disease (no encryption)
        str(encrypt_value(public_key, transformed_row[1])),  # Encrypt Gender
        str(encrypt_value(public_key, transformed_row[2])),  # Encrypt Fever
        str(encrypt_value(public_key, transformed_row[3])),  # Encrypt Cough
        str(encrypt_value(public_key, transformed_row[4])),  # Encrypt Fatigue
        str(encrypt_value(public_key, transformed_row[5])),  # Encrypt Difficulty Breathing
        str(encrypt_value(public_key, transformed_row[6])),  # Encrypt Age
        str(encrypt_value(public_key, transformed_row[7])),  # Encrypt Blood Pressure
        str(encrypt_value(public_key, transformed_row[8])),  # Encrypt Cholesterol Level
        transformed_row[9]  # Outcome Variable (no encryption)
    ]
    
    return encrypted_row

# Insert CSV into MySQL
def insert_csv_to_db(file_path):
    with open(file_path, 'r') as file:
        csv_data = csv.reader(file)
        next(csv_data)  # Skip the header row
        rows_inserted = 0

        for row in csv_data:
            transformed_row = transform_and_encrypt(row)
            if not transformed_row:  # Skip rows with missing mappings
                print(f"Skipping row due to missing mappings: {row}")
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

# Call the function
file_path = '/home/tsoien/github/newML/backend/data/Disease_symptom_and_patient_profile_dataset.csv' 
insert_csv_to_db(file_path)

cursor.close()
db.close()
