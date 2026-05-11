from passlib.context import CryptContext

# 1. Initialize the CryptContext
# 'bcrypt' is the algorithm; 'deprecated="auto"' handles future migrations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Takes a plain-text password and returns a secure, salted hash.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a plain-text password against the stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


# --- EXECUTION ---
if __name__ == "__main__":
    new_password = "Retail@505"

    # Generate the hash
    hashed_val = hash_password(new_password)

    print(f"Original Password: {new_password}")
    print(f"Generated Hash:    {hashed_val}")

    # Example of how verification works during login
    is_match = verify_password("Retail@505", hashed_val)
    print(f"Match Check:       {'✅ Success' if is_match else '❌ Failed'}")