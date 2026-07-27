# filter users by status
from models import User, UserStatus, db
from app import app


with app.app_context():
    # Retrieve all matching records.
    users= User.query.all()

    # returns a list of all users in the database 
    for user in users:
        print(user.id, user.last_name, user.first_name, user.status)

    # first 5 users
    users = User.query.limit(5).all()
    print("The first 5 users:")
    for user in users:
        print(user.id, user.first_name, user.last_name)

    # order users by last name
    users = User.query.order_by(User.first_name).all()
    print(users)

    # Retrieve the first matching record.
    users = User.query.first()
    print("The first user is:", users.first_name, users.last_name, users.status)


    # Apply complex conditional filters.
    users = User.query.filter(User.status == UserStatus.ACTIVE).all()
    print("Active users:")
    for user in users:
        print(user.id, user.last_name, user.first_name, user.status)


    # Use filter_by for simpler equality checks.
    def get_active_users():
        users = User.query.filter_by(status=UserStatus.ACTIVE).all()
        print("Active users (using filter_by):")
        for user in users:
            print(user.id,user.first_name, user.last_name, user.status, user.phone_number)
        return users
    
    get_active_users()

    # Delete one user from the database
    user_to_delete = User.query.filter_by(email="john.jackson@example.com").first()
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
    
