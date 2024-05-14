from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return context.verify(plain_password, hashed_password)
    
def get_password_hash(password):
    return context.hash(password)