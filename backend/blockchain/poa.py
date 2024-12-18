import hashlib

class ProofOfAuthority:
    def __init__(self, authorized_validators):
        """
        Initialize PoA with a list of authorized validators.
        """
        self.authorized_validators = authorized_validators

    def is_validator_authorized(self, validator_name):
        """
        Check if a validator is authorized.
        """
        return validator_name in self.authorized_validators

    def sign_block(self, validator_name, private_key, block_data):
        """
        Simulate signing a block using the validator's private key.
        This can be expanded with real cryptographic signing.
        """
        if not self.is_validator_authorized(validator_name):
            raise Exception(f"Validator {validator_name} is not authorized.")

        # Simplified example of a signature (use proper signing in production)
        data_to_sign = f"{validator_name}:{block_data}"
        signature = hashlib.sha256(data_to_sign.encode()).hexdigest()
        return signature

    def validate_signature(self, validator_name, block_data, signature):
        """
        Validate the signature of a block.
        """
        if not self.is_validator_authorized(validator_name):
            print(f"Validator {validator_name} is not authorized.")
            return False

        # Recreate the signature and compare
        data_to_sign = f"{validator_name}:{block_data}"
        expected_signature = hashlib.sha256(data_to_sign.encode()).hexdigest()
        return expected_signature == signature
