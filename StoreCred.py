from app import User, db
import getpass

def store_password():
    # Check if there's already a user
    if len(User.query.all()) == 0:
        email = input("Enter your email: ")
        password = getpass.getpass(prompt="Enter your password: ")
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

db.create_all()