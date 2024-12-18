import hashlib
import json
import time
import pymysql
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.data_config import db_cred

class Blockchain:
    def __init__(self):
        self.chain = self.load_chain_from_db()

        # If no blocks are loaded, create the genesis block
        if len(self.chain) == 0:
            self.create_and_add_genesis_block()

    def create_and_add_genesis_block(self):
        """Create and add the genesis block."""
        sample_data = "Genesis Block"  # You can modify this data as needed
        validator_name = "MD001"  # Use a default validator name for the genesis block
        signature = "4fa8c1cdf83eb36e391f810620bfe090be6d41177e9d5dafcdde9de957fd3460"  # Use a placeholder or empty signature for the genesis block
        
        # Add the genesis block to the blockchain without validation
        self.add_block(sample_data, validator_name, signature, is_genesis=True)

    def create_hash(self, data):
        """Generate a SHA-256 hash of the provided data."""
        return hashlib.sha256(data.encode()).hexdigest()

    def get_validator(self, validator_name):
        """Fetch the validator details from the database."""
        try:
            db = db_cred()
            cursor = db.cursor(pymysql.cursors.DictCursor)  # Ensuring DictCursor is used
            sql = "SELECT * FROM users WHERE user_id = %s;"
            cursor.execute(sql, (validator_name,))
            validator = cursor.fetchone()  # This should be a dictionary
            print(f"Validator raw result: {validator}")  # Debugging line
            cursor.close()
            db.close()

            # Check if validator is a dictionary or tuple
            print(f"Validator type: {type(validator)}")  # Debugging line

            return validator
        except Exception as e:
            print(f"Error fetching validator: {e}")
            return None

    def validate_signature(self, validator, provided_signature):
        """Validate the provided signature against the validator's stored signature."""
        if not validator:
            print("Validator not found.")
            return False

        # Access the signature directly using the tuple index (4th element in the result)
        if validator[4] != provided_signature:  # Index 4 is the 'signature' field in your query result tuple
            print("Invalid signature for the validator.")
            return False
        return True

    def create_block(self, data, validator_name, signature, is_genesis=False):
        """Create a new block."""
        validator = self.get_validator(validator_name)
        if not self.validate_signature(validator, signature):
            print("Block creation failed: invalid validator or signature.")
            return None

        if len(self.chain) == 0 or is_genesis:
            # Genesis block creation
            previous_hash = "0"  # Genesis block doesn't have a previous block, so set it to "0"
            index_num = 1  # Genesis block is the first block, so its index is 1
        else:
            previous_block = self.chain[-1]
            # Handle tuple-based result: access by index if it's a tuple
            if isinstance(previous_block, tuple):
                previous_hash = previous_block[3]  # Assuming 'hash' is at index 3 in the tuple
                index_num = previous_block[0] + 1  # Assuming 'index_num' is at index 0
            else:
                previous_hash = previous_block["hash"]
                index_num = previous_block["index_num"] + 1

        # Block data
        block_data = {
            "index_num": index_num,
            "data": data,
            "previous_hash": previous_hash,
            "timestamp": int(time.time()),
            "validator_name": validator_name,
            "signature": signature,
        }

        # Create hash for this block
        block_string = json.dumps(block_data, sort_keys=True)
        current_hash = self.create_hash(block_string)

        block_data["hash"] = current_hash

        return block_data


    def validate_block(self, block):
        """Validate a block by checking its hash and previous hash."""
        if len(self.chain) > 0:
            last_block = self.chain[-1]
            # Check if last_block is a tuple or a dictionary
            if isinstance(last_block, tuple):
                previous_hash = last_block[3]  # Index 3 corresponds to 'hash'
            else:
                previous_hash = last_block["hash"]

            if block["previous_hash"] != previous_hash:
                print("Block validation failed: previous hash does not match.")
                return False

        block_string = json.dumps(
            {k: block[k] for k in block if k != "hash"}, sort_keys=True
        )
        recalculated_hash = self.create_hash(block_string)
        if recalculated_hash != block["hash"]:
            print("Block validation failed: hash does not match.")
            return False

        return True


    def add_block(self, data, validator_name, signature, is_genesis=False):
        """Add a validated block to the blockchain."""
        new_block = self.create_block(data, validator_name, signature, is_genesis)
        if new_block and (is_genesis or self.validate_block(new_block)):
            self.chain.append(new_block)
            self.save_block_to_db(new_block)
            print("Block added successfully!")
            return new_block
        else:
            print("Block not added. Validation failed.")
            return None

    def load_chain_from_db(self):
        """Load the blockchain from the MySQL database."""
        try:
            db = db_cred()
            cursor = db.cursor(pymysql.cursors.DictCursor)  # Ensures we get a dictionary instead of a tuple
            cursor.execute("SELECT * FROM blockchain ORDER BY index_num ASC;")
            rows = cursor.fetchall()
            cursor.close()
            db.close()
            return rows if rows else []
        except Exception as e:
            print(f"Error loading blockchain from database: {e}")
            return []


    def save_block_to_db(self, block):
        """Save a block to the blockchain table in the database."""
        try:
            db = db_cred()
            cursor = db.cursor()
            sql = """
                INSERT INTO blockchain 
                (index_num, data, previous_hash, hash, validator_name, signature, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW());
            """
            cursor.execute(
                sql,
                (
                    block["index_num"],
                    block["data"],
                    block["previous_hash"],
                    block["hash"],
                    block["validator_name"],
                    block["signature"],
                ),
            )
            db.commit()
            cursor.close()
            db.close()
            print("Block saved to database successfully.")
        except Exception as e:
            print(f"Error saving block to database: {e}")

# Example usage:
if __name__ == "__main__":
    blockchain = Blockchain()

    # Example data
    sample_data = "Encrypted patient data: {symptoms: [fever, cough]}"
    validator_name = "MD001"
    signature = "4fa8c1cdf83eb36e391f810620bfe090be6d41177e9d5dafcdde9de957fd3460"  # Replace with the actual signature for MD001
    # Add a block to the blockchain
    blockchain.add_block(sample_data, validator_name, signature)
    
    # Example data
    sample_data = "Encrypted patient data: {symptoms: [fever, cough]}"
    validator_name = "MD002"
    signature = "7e3d89811312ed290e4d1e50b7edbeea816a31d0b586c5e85c16c9c4c6d22ebe"  # Replace with the actual signature for MD001
    # Add a block to the blockchain
    blockchain.add_block(sample_data, validator_name, signature)
    
    # Example data
    sample_data = "Encrypted patient data: {symptoms: [fever, cough]}"
    validator_name = "MD004"
    signature = "023cf87ea9818c905eb9d15f2981cd6ad8a34c84a3a71754a450ad5bdb4fa043"  # Replace with the actual signature for MD001
    # Add a block to the blockchain
    blockchain.add_block(sample_data, validator_name, signature)

    # Print the blockchain
    for block in blockchain.chain:
        print(block)
