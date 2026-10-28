
from main import SessionLocal, UserDB, password_hash

db = SessionLocal()

try:
    user = db.query(UserDB).filter(
        UserDB.username == "anushka123"
    ).first()

    if user is None:
        print("User not found")
    else:
        user.hashed_password = password_hash.hash("password123")
        db.commit()
        print("Password reset successfully!")

finally:
    db.close()
