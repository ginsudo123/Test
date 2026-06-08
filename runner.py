import os
import sys
import zipfile
import io
import subprocess

# Ensure cryptography is installed
try:
    from cryptography.fernet import Fernet
except ImportError:
    print("cryptography module not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    from cryptography.fernet import Fernet

def main():
    key_str = os.environ.get("AES_SECRET_KEY")
    if not key_str:
        print("Error: AES_SECRET_KEY environment variable is not set!")
        sys.exit(1)

    encrypted_file = "test.enc"
    if not os.path.exists(encrypted_file):
        print(f"Error: Encrypted file '{encrypted_file}' not found!")
        sys.exit(1)

    print(f"Decrypting '{encrypted_file}'...")
    key = key_str.encode('utf-8')
    try:
        fernet = Fernet(key)
    except Exception as e:
        print(f"Invalid AES_SECRET_KEY format: {e}")
        sys.exit(1)

    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        print(f"Decryption failed: {e}. Check if AES_SECRET_KEY is correct.")
        sys.exit(1)

    print("Extracting files...")
    zip_buffer = io.BytesIO(decrypted_data)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        zip_file.extractall(".")

    print("Checking dependencies...")
    req_file = os.path.join("code", "requirements.txt")
    if os.path.exists(req_file):
        print(f"Installing requirements from {req_file}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        except Exception as e:
            print(f"Failed to install requirements: {e}")
            # Continue anyway, dependencies might already be installed
            
    print("Launching framework entry point (main.py)...")
    main_script = os.path.join("code", "main.py")
    if not os.path.exists(main_script):
        print(f"Error: Framework entry point '{main_script}' not found after extraction!")
        sys.exit(1)

    # Invoke main.py using same python interpreter and forward arguments
    cmd = [sys.executable, main_script] + sys.argv[1:]
    try:
        sys.exit(subprocess.run(cmd).returncode)
    except Exception as e:
        print(f"Execution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
