import secrets

# Generate a random secret key (32 bytes long)
SECRET_KEY = secrets.token_urlsafe(32)
print("SECRET_KEY:", SECRET_KEY)

# Generate a random salt (16 bytes long)
SECURITY_SALT = secrets.token_urlsafe(16)
print("SECURITY_SALT:", SECURITY_SALT)
