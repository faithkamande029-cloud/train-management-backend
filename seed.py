from app import app
from models import UserStatus, db, User
from datetime import datetime
from models import UserRole

with app.app_context():
    # Create the database tables
    db.session.query(User).delete()
    db.session.commit()

    # Create a new user
    new_users = [
        User(
            first_name="Joe",
            last_name="Jackson",
            email="joe.jackson@example.com",
            password="password123",
            phone_number="0712345678",
            date_of_birth=datetime(1990, 1, 1),
            role=UserRole.PASSENGER,
            status=UserStatus.SUSPENDED,
        ),
        User(
            first_name="Lulu",
            last_name="Hassan",
            email="lulu.hassan@example.com",
            password="password456",
            phone_number="0723456789",
            date_of_birth=datetime(1985, 5, 15),
            role=UserRole.PASSENGER,
            status=UserStatus.ACTIVE,
        ),
        User(
            first_name="Peter",
            last_name="Kimotho",
            email="peter.kimotho@example.com",
            password="password789",
            phone_number="0734567890",
            date_of_birth=datetime(1980, 10, 10),
            role=UserRole.PASSENGER,
            status=UserStatus.ACTIVE,
        ),
        User(
            first_name="Mary",
            last_name="Wanjiku",
            email="mary.wanjiku@example.com",
            password="password012",
            phone_number="0745678901",
            date_of_birth=datetime(1988, 3, 20),
            role=UserRole.PASSENGER,
            status=UserStatus.SUSPENDED,
        ),
        User(
            first_name="Malcom",
            last_name="Karanja",
            email="malcom.karanja@example.com",
            password="password345",
            phone_number="0756789012",
            date_of_birth=datetime(1992, 7, 25),
            role=UserRole.PASSENGER,
            status=UserStatus.INACTIVE,
        ),
        User(
            first_name="Jane",
            last_name="Muthoni",
            email="jane.muthoni@example.com",
            password="password678",
            phone_number="0767890123",
            date_of_birth=datetime(1995, 12, 12),
            role=UserRole.PASSENGER,
            status=UserStatus.ACTIVE,
        ),
        User(
            first_name="Thaya",
            last_name="Muthaka",
            email="thaya.muthaka@example.com",
            password="password901",
            phone_number="0778901234",
            date_of_birth=datetime(1985, 8, 8),
            role=UserRole.PASSENGER,
            status=UserStatus.ACTIVE,
        ),
        User(
            first_name="Muthoni",
            last_name="Wanjiru",
            email="muthoni.wanjiru@example.com",
            password="password234",
            phone_number="0789012345",
            date_of_birth=datetime(1988, 6, 15),
            role=UserRole.PASSENGER,
            status=UserStatus.INACTIVE,
        ),
        User(
            first_name="Jackson",
            last_name="Karanja",
            email="jackson.karanja@example.com",
            password="password567",
            phone_number="0790123456",
            date_of_birth=datetime(1990, 11, 11),
            role=UserRole.PASSENGER,
            status=UserStatus.SUSPENDED,
        )
    ]

    # Add the users to the database
    db.session.add_all(new_users)
    db.session.commit()
    print("Database seeded with initial users.")
