import secrets

def generate_jwt_secret():
    return secrets.token_hex(32)

if __name__ == "__main__":
    print(generate_jwt_secret())
