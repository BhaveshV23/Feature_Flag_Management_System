from app.database.session import SessionLocal
from app.models.user import User
from app.services.auth_service import hash_password

db = SessionLocal()

existing = db.query(User).filter(User.username == "admin").first()
if existing:
    print("User 'admin' already exists.")
else:
    user = User(username="admin", hashed_password=hash_password("admin123"))
    db.add(user)
    db.commit()
    print("Created user 'admin' with password 'admin123'")

db.close()