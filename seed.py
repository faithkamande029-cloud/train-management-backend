"""Seed the database with test data for all models."""

import random
from datetime import datetime, timedelta
from app import app
from models import (
    db,
    User,
    UserRole,
    UserStatus,
    Train,
    TrainType,
    TrainStatus,
    Station,
    Schedule,
    ScheduleStatus,
    Booking,
    BookingStatus,
    Payment,
    PaymentMethod,
    UserFavourite,
)


def create_users():
    """Create sample users if they don't exist."""
    users_data = [
        {
            "first_name": "Joe",
            "last_name": "Jackson",
            "email": "joe.jackson@example.com",
            "password": "password123",
            "phone_number": "0712345678",
            "date_of_birth": datetime(1990, 1, 1),
            "role": UserRole.PASSENGER,
            "status": UserStatus.SUSPENDED,
        },
        {
            "first_name": "Lulu",
            "last_name": "Hassan",
            "email": "lulu.hassan@example.com",
            "password": "password456",
            "phone_number": "0723456789",
            "date_of_birth": datetime(1985, 5, 15),
            "role": UserRole.PASSENGER,
            "status": UserStatus.ACTIVE,
        },
        {
            "first_name": "Peter",
            "last_name": "Kimotho",
            "email": "peter.kimotho@example.com",
            "password": "password789",
            "phone_number": "0734567890",
            "date_of_birth": datetime(1980, 10, 10),
            "role": UserRole.PASSENGER,
            "status": UserStatus.ACTIVE,
        },
        {
            "first_name": "Mary",
            "last_name": "Wanjiku",
            "email": "mary.wanjiku@example.com",
            "password": "password012",
            "phone_number": "0745678901",
            "date_of_birth": datetime(1988, 3, 20),
            "role": UserRole.PASSENGER,
            "status": UserStatus.SUSPENDED,
        },
        {
            "first_name": "Malcom",
            "last_name": "Karanja",
            "email": "malcom.karanja@example.com",
            "password": "password345",
            "phone_number": "0756789012",
            "date_of_birth": datetime(1992, 7, 25),
            "role": UserRole.PASSENGER,
            "status": UserStatus.INACTIVE,
        },
        {
            "first_name": "Jane",
            "last_name": "Muthoni",
            "email": "jane.muthoni@example.com",
            "password": "password678",
            "phone_number": "0767890123",
            "date_of_birth": datetime(1995, 12, 12),
            "role": UserRole.PASSENGER,
            "status": UserStatus.ACTIVE,
        },
        {
            "first_name": "Thaya",
            "last_name": "Muthaka",
            "email": "thaya.muthaka@example.com",
            "password": "password901",
            "phone_number": "0778901234",
            "date_of_birth": datetime(1985, 8, 8),
            "role": UserRole.PASSENGER,
            "status": UserStatus.ACTIVE,
        },
        {
            "first_name": "Muthoni",
            "last_name": "Wanjiru",
            "email": "muthoni.wanjiru@example.com",
            "password": "password234",
            "phone_number": "0789012345",
            "date_of_birth": datetime(1988, 6, 15),
            "role": UserRole.PASSENGER,
            "status": UserStatus.INACTIVE,
        },
        {
            "first_name": "Jackson",
            "last_name": "Karanja",
            "email": "jackson.karanja@example.com",
            "password": "password567",
            "phone_number": "0790123456",
            "date_of_birth": datetime(1990, 11, 11),
            "role": UserRole.PASSENGER,
            "status": UserStatus.SUSPENDED,
        },
    ]

    created = 0
    for data in users_data:
        # Check if user already exists by email
        existing = User.query.filter_by(email=data["email"]).first()
        if existing is None:
            user = User(**data)
            db.session.add(user)
            created += 1
    if created:
        db.session.commit()
        print(f"Created {created} new users.")
    else:
        print("Users already exist. Skipping.")


def create_trains():
    """Create sample trains if none exist."""
    if Train.query.count() > 0:
        print("Trains already exist. Skipping.")
        return

    trains = [
        Train(
            name="Express 1",
            type=TrainType.EXPRESS,
            total_seat=100,
            available_seat=80,
            status=TrainStatus.ACTIVE,
            description="High-speed intercity express.",
        ),
        Train(
            name="Passenger 2",
            type=TrainType.PASSENGER,
            total_seat=150,
            available_seat=120,
            status=TrainStatus.ACTIVE,
            description="Regular passenger train.",
        ),
        Train(
            name="Freight 3",
            type=TrainType.FREIGHT,
            total_seat=50,
            available_seat=50,
            status=TrainStatus.INACTIVE,
            description="Freight transport.",
        ),
        Train(
            name="HighSpeed 4",
            type=TrainType.HIGH_SPEED,
            total_seat=200,
            available_seat=180,
            status=TrainStatus.ACTIVE,
            description="High-speed rail service.",
        ),
        Train(
            name="Coastal Express",
            type=TrainType.EXPRESS,
            total_seat=120,
            available_seat=90,
            status=TrainStatus.MAINTENANCE,
            description="Coastal route express.",
        ),
    ]
    db.session.add_all(trains)
    db.session.commit()
    print(f"Created {len(trains)} trains.")


def create_stations():
    """Create sample stations if none exist."""
    if Station.query.count() > 0:
        print("Stations already exist. Skipping.")
        return

    stations = [
        Station(
            name="Nairobi Central",
            train_number="NBO-01",
            city="Nairobi",
            platform=1,
            description="Main station in Nairobi.",
        ),
        Station(
            name="Mombasa Terminal",
            train_number="MBA-02",
            city="Mombasa",
            platform=2,
            description="Coastal terminal.",
        ),
        Station(
            name="Kisumu Port",
            train_number="KSM-03",
            city="Kisumu",
            platform=1,
            description="Lake Victoria port station.",
        ),
        Station(
            name="Nakuru Junction",
            train_number="NKR-04",
            city="Nakuru",
            platform=3,
            description="Central Rift station.",
        ),
        Station(
            name="Eldoret Station",
            train_number="ELD-05",
            city="Eldoret",
            platform=1,
            description="Highlands station.",
        ),
    ]
    db.session.add_all(stations)
    db.session.commit()
    print(f"Created {len(stations)} stations.")


def create_schedules():
    """Create sample schedules if none exist."""
    if Schedule.query.count() > 0:
        print("Schedules already exist. Skipping.")
        return

    trains = Train.query.all()
    stations = Station.query.all()
    if len(trains) < 2 or len(stations) < 2:
        print("Not enough trains or stations to create schedules. Skipping.")
        return

    # Create a few schedules using existing trains and stations
    schedules = [
        Schedule(
            name="Morning Express",
            train_id=trains[0].id,
            from_station_id=stations[0].id,
            to_station_id=stations[1].id,
            departure_time=datetime.strptime("08:00", "%H:%M").time(),
            arrival_time=datetime.strptime("12:30", "%H:%M").time(),
            status=ScheduleStatus.SCHEDULED,
            platform=1,
        ),
        Schedule(
            name="Afternoon Local",
            train_id=trains[1].id,
            from_station_id=stations[1].id,
            to_station_id=stations[2].id,
            departure_time=datetime.strptime("14:30", "%H:%M").time(),
            arrival_time=datetime.strptime("18:45", "%H:%M").time(),
            status=ScheduleStatus.SCHEDULED,
            platform=2,
        ),
        Schedule(
            name="Evening High-Speed",
            train_id=trains[3].id,
            from_station_id=stations[0].id,
            to_station_id=stations[3].id,
            departure_time=datetime.strptime("18:00", "%H:%M").time(),
            arrival_time=datetime.strptime("20:30", "%H:%M").time(),
            status=ScheduleStatus.SCHEDULED,
            platform=3,
        ),
        Schedule(
            name="Night Freight",
            train_id=trains[2].id,
            from_station_id=stations[2].id,
            to_station_id=stations[4].id,
            departure_time=datetime.strptime("22:00", "%H:%M").time(),
            arrival_time=datetime.strptime("01:30", "%H:%M").time(),
            status=ScheduleStatus.CANCELLED,
            platform=1,
        ),
        Schedule(
            name="Coastal Shuttle",
            train_id=trains[0].id,
            from_station_id=stations[1].id,
            to_station_id=stations[0].id,
            departure_time=datetime.strptime("06:30", "%H:%M").time(),
            arrival_time=datetime.strptime("10:00", "%H:%M").time(),
            status=ScheduleStatus.DELAYED,
            platform=2,
        ),
    ]
    db.session.add_all(schedules)
    db.session.commit()
    print(f"Created {len(schedules)} schedules.")


def create_bookings():
    """Create sample bookings if none exist."""
    if Booking.query.count() > 0:
        print("Bookings already exist. Skipping.")
        return

    users = User.query.all()
    trains = Train.query.all()
    schedules = Schedule.query.all()
    if not users or not trains or not schedules:
        print("Missing required data to create bookings. Skipping.")
        return

    # Use first few users and schedules
    bookings = []
    statuses = [BookingStatus.CONFIRMED, BookingStatus.PENDING, BookingStatus.COMPLETED, BookingStatus.CANCELLED]
    for i in range(5):
        user = users[i % len(users)]
        schedule = schedules[i % len(schedules)]
        train = trains[i % len(trains)]
        booking = Booking(
            booking_ref=f"BK-{random.randint(10000, 99999)}",
            passenger_name=f"{user.first_name} {user.last_name}",
            email=user.email,
            phone=user.phone_number,
            train_id=train.id,
            schedule_id=schedule.id,
            seat_number=f"{random.randint(1, 50)}A",
            fare=random.randint(500, 5000) / 10,
            status=random.choice(statuses),
            from_station=f"Station {random.randint(1, 5)}",
            to_station=f"Station {random.randint(6, 10)}",
            departure_time=schedule.departure_time,
        )
        bookings.append(booking)
    db.session.add_all(bookings)
    db.session.commit()
    print(f"Created {len(bookings)} bookings.")


def create_payments():
    """Create sample payments if none exist."""
    if Payment.query.count() > 0:
        print("Payments already exist. Skipping.")
        return

    bookings = Booking.query.all()
    users = User.query.all()
    if not bookings or not users:
        print("Missing bookings or users to create payments. Skipping.")
        return

    payments = []
    methods = [PaymentMethod.CARD, PaymentMethod.MPESA, PaymentMethod.CASH, PaymentMethod.BANK_TRANSFER]
    for i in range(3):
        booking = bookings[i % len(bookings)]
        user = users[i % len(users)]
        payment = Payment(
            booking_id=booking.id,
            user_id=user.id,
            amount=booking.fare,
            method=random.choice(methods),
            card_last4=str(random.randint(1000, 9999)) if random.choice([True, False]) else None,
            status="completed",
            transaction_id=f"TXN-{random.randint(100000, 999999)}",
        )
        payments.append(payment)
    db.session.add_all(payments)
    db.session.commit()
    print(f"Created {len(payments)} payments.")


def create_favourites():
    """Create sample favourites if none exist."""
    if UserFavourite.query.count() > 0:
        print("Favourites already exist. Skipping.")
        return

    users = User.query.all()
    trains = Train.query.all()
    stations = Station.query.all()
    if not users or not trains or not stations:
        print("Missing required data to create favourites. Skipping.")
        return

    favourites = []
    for i in range(3):
        user = users[i % len(users)]
        train = trains[i % len(trains)]
        station = stations[i % len(stations)]
        # Avoid duplicates
        existing = UserFavourite.query.filter_by(user_id=user.id, train_id=train.id, station_id=station.id).first()
        if not existing:
            fav = UserFavourite(user_id=user.id, train_id=train.id, station_id=station.id)
            favourites.append(fav)
    if favourites:
        db.session.add_all(favourites)
        db.session.commit()
        print(f"Created {len(favourites)} favourites.")
    else:
        print("No new favourites created.")


def seed_all():
    """Run all seeding functions."""
    with app.app_context():
        db.create_all()  # Ensure tables exist
        print("Starting database seeding...")
        create_users()
        create_trains()
        create_stations()
        create_schedules()
        create_bookings()
        create_payments()
        create_favourites()
        print("Seeding complete.")


if __name__ == "__main__":
    seed_all()