from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

pw = "test123"
hashed = pwd_context.hash(pw)
print("HASH:", hashed)
print("VERIFY:", pwd_context.verify(pw, hashed))
