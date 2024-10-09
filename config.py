# config.py
import os
import secrets

def get_secret_key():
    # Define the path for the secret key file
    secret_key_path = 'secret_key.txt'

    # Check if the secret key file exists
    if os.path.exists(secret_key_path):
        # Read the existing secret key
        with open(secret_key_path, 'r') as f:
            return f.read().strip()
    else:
        # Generate a new secret key
        new_key = secrets.token_hex(16)
        # Save the new secret key to the file
        with open(secret_key_path, 'w') as f:
            f.write(new_key)
        return new_key
