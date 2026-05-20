from database import SessionLocal
from models import User
from auth import get_password_hash

db = SessionLocal()

email = "test@example.com"
password = "password123"

hashed_password = get_password_hash(password)

user = User(
    email=email,
    hashed_password=hashed_password
)

db.add(user)
db.commit()
db.close()

print("User created successfully")
print("Email:", email)
print("Password:", password)
