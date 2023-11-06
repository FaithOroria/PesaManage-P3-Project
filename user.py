from main import Session, User

# Function to register a new user
def register_user(session,username, password):
    new_user = User(username=username, password=password)
    Session.add(new_user)
    Session.commit()

# Function to log in a user
def login_user(session,username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and user.password == password:
        return user
    else:
        return None
