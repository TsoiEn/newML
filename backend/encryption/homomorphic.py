from phe import paillier
import random

# Generate public and private keys
def generate_keys():
    public_key, private_key = paillier.generate_paillier_keypair()
    return public_key, private_key

# Encrypt a value
def encrypt_value(public_key, value):
    encrypted_value = public_key.encrypt(value)
    return encrypted_value

# Decrypt a value
def decrypt_value(private_key, encrypted_value):
    decrypted_value = private_key.decrypt(encrypted_value)
    return decrypted_value



# testing purposes
# Perform a homomorphic operation (e.g., addition) on encrypted data
def homomorphic_addition(encrypted_value1, encrypted_value2, public_key):
    # Add the encrypted values directly without decryption
    result = encrypted_value1 + encrypted_value2
    return result

# Example usage
def main():
    # Step 1: Generate Paillier keys
    public_key, private_key = generate_keys()

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
