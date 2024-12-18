import hashlib
from getpass import getpass
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.data_config import db_cred
from encryption.homomorphic import encrypt_value, generate_keys, decrypt_value, save_keys, load_keys
import pickle
import joblib
from mappings import GENDER_MAP, FEVER_MAP, COUGH_MAP, FATIGUE_MAP, DIFFICULTY_BREATHING_MAP, BLOOD_PRESSURE_MAP, CHOLESTEROL_LEVEL_MAP
import pandas as pd

# User login function
def user_login(cursor):
    while True:
        email = input("Enter your email: ")
        password = getpass("Enter your password: ")

        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password_hash))
        user = cursor.fetchone()

        if user:
            print("Login successful!")
            return user
        else:
            print("Invalid credentials. Please try again.")

# Reverse mapping for decryption
def reverse_mapping(row):
    GENDER_MAP = {1: "Male", 2: "Female"}
    FEVER_MAP = {1: "Yes", 0: "No"}
    COUGH_MAP = {1: "Yes", 0: "No"}
    FATIGUE_MAP = {1: "Yes", 0: "No"}
    DIFFICULTY_BREATHING_MAP = {1: "Yes", 0: "No"}
    BLOOD_PRESSURE_MAP = {1: "Low", 2: "Normal", 3: "High"}
    CHOLESTEROL_LEVEL_MAP = {1: "Low", 2: "Normal", 3: "High"}

    decrypted_row = [
        row[0],  # Disease
        GENDER_MAP.get(row[1], row[1]),
        FEVER_MAP.get(row[2], row[2]),
        COUGH_MAP.get(row[3], row[3]),
        FATIGUE_MAP.get(row[4], row[4]),
        DIFFICULTY_BREATHING_MAP.get(row[5], row[5]),
        row[6],  # Age
        BLOOD_PRESSURE_MAP.get(row[7], row[7]),
        CHOLESTEROL_LEVEL_MAP.get(row[8], row[8])
    ]

    return decrypted_row

# Decrypt data from the database
def decrypt_data_from_db(public_key, private_key, cursor):
    print("\nFetching and decrypting data from the database...")

    query = """
    SELECT Disease, Gender, Fever, Cough, Fatigue, Difficulty_Breathing, Age, Blood_Pressure, Cholesterol_Level, Prediction_Variable
    FROM disease_data LIMIT 5;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    decrypted_rows = []

    for row in rows:
        decrypted_row = [
            row[0],
            decrypt_value(private_key, pickle.loads(row[1])),
            decrypt_value(private_key, pickle.loads(row[2])),
            decrypt_value(private_key, pickle.loads(row[3])),
            decrypt_value(private_key, pickle.loads(row[4])),
            decrypt_value(private_key, pickle.loads(row[5])),
            int(decrypt_value(private_key, pickle.loads(row[6]))),
            decrypt_value(private_key, pickle.loads(row[7])),
            decrypt_value(private_key, pickle.loads(row[8]))
        ]

        mapped_row = reverse_mapping(decrypted_row)
        decrypted_rows.append(mapped_row)

    print(pd.DataFrame(decrypted_rows, columns=[
        "Disease", "Gender", "Fever", "Cough", "Fatigue", "Difficulty Breathing", "Age", "Blood Pressure", "Cholesterol Level"
    ]))

# Load or generate encryption keys
def load_or_generate_keys():
    try:
        public_key, private_key = load_keys()
    except FileNotFoundError:
        print("Keys not found, generating new keys...")
        public_key, private_key = generate_keys()
        save_keys(public_key, private_key)
    return public_key, private_key

# Add patient function
def add_patient(cursor,connection, public_key):
    print("\nAdding a new patient...")
    
    # Get user inputs
    disease = input("Enter Disease: ")
    gender = input("Enter Gender (Male/Female): ").capitalize()
    fever = input("Fever (Yes/No): ").capitalize()
    cough = input("Cough (Yes/No): ").capitalize()
    fatigue = input("Fatigue (Yes/No): ").capitalize()
    difficulty_breathing = input("Difficulty Breathing (Yes/No): ").capitalize()
    age = int(input("Enter Age (integer): "))
    blood_pressure = input("Blood Pressure (Low/Normal/High): ").capitalize()
    cholesterol_level = input("Cholesterol Level (Low/Normal/High): ").capitalize()
    outcome_Variable = input("Outcome Variable (Positive/Negative): ").capitalize()

    # Map inputs to numerical values
    gender = GENDER_MAP.get(gender)
    fever = FEVER_MAP.get(fever)
    cough = COUGH_MAP.get(cough)
    fatigue = FATIGUE_MAP.get(fatigue)
    difficulty_breathing = DIFFICULTY_BREATHING_MAP.get(difficulty_breathing)
    blood_pressure = BLOOD_PRESSURE_MAP.get(blood_pressure)
    cholesterol_level = CHOLESTEROL_LEVEL_MAP.get(cholesterol_level)

    # Encrypt the mapped inputs
    encrypted_gender = pickle.dumps(encrypt_value(public_key, gender))
    encrypted_fever = pickle.dumps(encrypt_value(public_key, fever))
    encrypted_cough = pickle.dumps(encrypt_value(public_key, cough))
    encrypted_fatigue = pickle.dumps(encrypt_value(public_key, fatigue))
    encrypted_difficulty_breathing = pickle.dumps(encrypt_value(public_key, difficulty_breathing))
    encrypted_age = pickle.dumps(encrypt_value(public_key, age))
    encrypted_blood_pressure = pickle.dumps(encrypt_value(public_key, blood_pressure))
    encrypted_cholesterol_level = pickle.dumps(encrypt_value(public_key, cholesterol_level))

    # Insert the encrypted data into the database
    cursor.execute(
        """
        INSERT INTO disease_data (Disease, Gender, Fever, Cough, Fatigue, Difficulty_Breathing, Age, Blood_Pressure, Cholesterol_Level, Outcome_Variable)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            disease,
            encrypted_gender,
            encrypted_fever,
            encrypted_cough,
            encrypted_fatigue,
            encrypted_difficulty_breathing,
            encrypted_age,
            encrypted_blood_pressure,
            encrypted_cholesterol_level,
            outcome_Variable,
        ),
    )
    connection.commit()
    print("Patient data added successfully!")

# Main CLI Menu
def main():
    connection = db_cred()
    cursor = connection.cursor()

    user = user_login(cursor)

    public_key, private_key = load_or_generate_keys()

    while True:
        print("\n[Decrypted Disease Data]")
        decrypt_data_from_db(public_key, private_key, cursor)

        print("\nOptions:")
        print("[1] Add patient")
        print("[0] Log out")
        choice = input("Select an option: ")

        if choice == '1':
            add_patient(cursor, connection, public_key)
        elif choice == '0':
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
