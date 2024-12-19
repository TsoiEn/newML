from phe import paillier
import pickle

# Generate public and private keys
def generate_keys():
    public_key, private_key = paillier.generate_paillier_keypair()
    return public_key, private_key

# Save keys to disk
def save_keys(public_key, private_key, public_key_file="public_key.pkl", private_key_file="private_key.pkl"):
    with open(public_key_file, "wb") as pub_file:
        pickle.dump(public_key, pub_file)
    with open(private_key_file, "wb") as priv_file:
        pickle.dump(private_key, priv_file)
    print("Keys saved to disk.")

# Load keys from disk
def load_keys(public_key_file="public_key.pkl", private_key_file="private_key.pkl"):
    with open(public_key_file, "rb") as pub_file:
        public_key = pickle.load(pub_file)
    with open(private_key_file, "rb") as priv_file:
        private_key = pickle.load(priv_file)
    print("Keys loaded from disk.")
    return public_key, private_key

# Encrypt a value
def encrypt_value(public_key, value):
    encrypted_value = public_key.encrypt(value)
    return encrypted_value

# Decrypt a value
def decrypt_value(private_key, encrypted_value):
    decrypted_value = private_key.decrypt(encrypted_value)
    return decrypted_value

#test purposes
# Perform a homomorphic operation (e.g., addition) on encrypted data
def homomorphic_addition(encrypted_value1, encrypted_value2, public_key):
    # Add the encrypted values directly without decryption
    result = encrypted_value1 + encrypted_value2
    return result

# Example usage
def main():
    # Step 1: Check if keys exist, load or generate
    try:
        public_key, private_key = load_keys()
    except FileNotFoundError:
        print("Keys not found, generating new keys...")
        public_key, private_key = generate_keys()
        save_keys(public_key, private_key)

    # Step 2: Encrypt some values
    value1 = 25
    value2 = 50
    encrypted_value1 = encrypt_value(public_key, value1)
    encrypted_value2 = encrypt_value(public_key, value2)

    print(f"Encrypted Value 1: {encrypted_value1}")
    print(f"Encrypted Value 2: {encrypted_value2}")

    # Step 3: Perform homomorphic addition on the encrypted values
    encrypted_result = homomorphic_addition(encrypted_value1, encrypted_value2, public_key)
    print(f"Encrypted Result (sum): {encrypted_result}")

    # Step 4: Decrypt the result
    decrypted_result = decrypt_value(private_key, encrypted_result)
    print(f"Decrypted Result (sum): {decrypted_result}")

if __name__ == "__main__":
    main()