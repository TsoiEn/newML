import os
import sys
import pandas as pd
import joblib
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from encryption.homomorphic import load_keys, decrypt_value, encrypt_value
from data.data_config import db_cred


# Load the preprocessor and model
preprocessor_path = "/home/tsoien/github/newML/backend/ml_model/preprocessor.joblib"
model_path = "/home/tsoien/github/newML/backend/ml_model/model.joblib"

preprocessor = joblib.load(preprocessor_path)
model = joblib.load(model_path)

# Load keys
public_key_path = "/home/tsoien/github/newML/public_key.pkl"
private_key_path = "/home/tsoien/github/newML/private_key.pkl"
public_key, private_key = load_keys(public_key_path, private_key_path)

# Function to fetch encrypted data from the database
def fetch_encrypted_data(query):
    try:
        db = db_cred()
        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()
        db.close()
        return pd.DataFrame(rows, columns=column_names)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Function to decrypt encrypted data
def decrypt_dataframe_for_prediction(df):
    try:
        encrypted_columns = [
            "Gender", "Fever", "Cough", "Fatigue",
            "Difficulty_Breathing", "Age", "Blood_Pressure", "Cholesterol_Level"
        ]
        for col in encrypted_columns:
            df[col] = df[col].apply(lambda x: decrypt_value(private_key, pickle.loads(x)))
        return df
    except Exception as e:
        print(f"Error during decryption: {e}")
        return None

# Function to store predictions in the database
def store_predictions_in_db(ids, predictions):
    try:
        db = db_cred()
        cursor = db.cursor()
        for idx, pred in zip(ids, predictions):
            sql = """
                UPDATE disease_data 
                SET Prediction_Variable = %s
                WHERE id = %s
            """
            cursor.execute(sql, (pred, idx))  # Update the column with prediction value
        db.commit()
        cursor.close()
        db.close()
        print("Predictions stored successfully.")
    except Exception as e:
        print(f"Error storing predictions: {e}")


# Query to fetch data for prediction (ensure that the `Outcome_Variable` is NULL for prediction)
query = "SELECT * FROM disease_data WHERE Prediction_Variable IS NULL;"
encrypted_data = fetch_encrypted_data(query)

if encrypted_data is not None and not encrypted_data.empty:
    print("Encrypted data fetched successfully.")
    
    # Decrypt the data for preprocessing
    decrypted_data = decrypt_dataframe_for_prediction(encrypted_data)
    if decrypted_data is not None:
        print("Decryption completed successfully.")
        
        # Extract features for prediction
        X_to_predict = decrypted_data.drop(columns=["Outcome_Variable", "Prediction_Variable", "id"], errors="ignore")
        
        # Preprocess the data
        try:
            X_preprocessed = preprocessor.transform(X_to_predict)
            print("Data preprocessed successfully.")
            
            # Make predictions
            predictions = model.predict(X_preprocessed)
            print("Predictions:", predictions)
            
            # Optionally, you can compare with the actual values (if available for testing)
            # Assuming you have a dataset with known `Outcome_Variable` values
            y_actual = decrypted_data["Outcome_Variable"]  # Actual values if available for evaluation
            accuracy = accuracy_score(y_actual, predictions)
            print(f"Prediction Accuracy: {accuracy * 100:.2f}%")
            
            # Store the predictions directly in the database
            store_predictions_in_db(ids=encrypted_data["id"], predictions=predictions)
        except Exception as e:
            print(f"Error during prediction or preprocessing: {e}")
    else:
        print("Failed to decrypt data.")
else:
    print("No data available for prediction.")

