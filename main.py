from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    accounts = relationship('Account', back_populates='user')
    categories = relationship('Category', back_populates='user')
    transactions = relationship('Transaction', back_populates='user')


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='accounts')
    transactions = relationship('Transaction', back_populates='account')


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='categories')
    transactions = relationship('Transaction', back_populates='category')


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    account = relationship('Account', back_populates='transactions')
    category = relationship('Category', back_populates='transactions')
    user = relationship('User', back_populates='transactions')


def create_user(session, username, password):
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    print("User created successfully!")


def login(session, username, password):
    user = session.query(User).filter_by(username=username, password=password).first()
    if user:
        print("Login successful!")
        return user
    else:
        print("Invalid username or password.")
        return None


def print_expenses(session, user_id):
    expenses = session.query(Transaction).join(Category).filter(
        Transaction.user_id == user_id,
        Category.type == 'expense'
    ).all()

    if expenses:
        print("Expenses:")
        for expense in expenses:
            print(f"Date: {expense.date}, Description: {expense.description}, Amount: {expense.amount}")
    else:
        print("No expenses found.")


def print_incomes(session, user_id):
    incomes = session.query(Transaction).join(Category).filter(
        Transaction.user_id == user_id,
        Category.type == 'income'
    ).all()

    if incomes:
        print("Incomes:")
        for income in incomes:
            print(f"Date: {income.date}, Description: {income.description}, Amount: {income.amount}")
    else:
        print("No incomes found.")


def user_specific_functionality(session, user):
    options = [
        {"option": "Create an account"},
        {"option": "Add Category"},
        {"option": "Add a transaction"},
        {"option": "View Expenses"},
        {"option": "View Incomes"},
        {"option": "Logout"}
    ]

    while True:
        print("\nUser-specific Options:")
        for i, option in enumerate(options):
            print(f"{i + 1}. {option['option']}")

        choice = input("Enter your choice: ")

        if choice == '1':
            account_name = input("Enter account name: ")
            try:
                new_account = Account(name=account_name, user=user)
                session.add(new_account)
                session.commit()
                print("Account created successfully!")
            except Exception as e:
                print(f"Account creation failed: {str(e)}")

        elif choice == '2':
            category_name = input("Enter category name: ")
            category_type = input("Enter category type (income or expense): ")
            try:
                new_category = Category(name=category_name, type=category_type, user=user)
                session.add(new_category)
                session.commit()
                print("Category added successfully")
            except Exception as e:
                print(f"Category addition failed: {str(e)}")

        elif choice == '3':
            account_id = int(input("Enter account ID: "))
            category_id = int(input("Enter category ID: "))
            transaction_date = input("Enter transaction date (YYYY-MM-DD): ")
            description = input("Enter transaction description: ")
            amount = float(input("Enter transaction amount: "))
            try:
                formatted_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
                new_transaction = Transaction(
                    date=formatted_date,
                    description=description,
                    amount=amount,
                    account_id=account_id,
                    category_id=category_id,
                    user_id=user.id
                )
                session.add(new_transaction)
                session.commit()
                print("Transaction added successfully!")
            except Exception as e:
                print(f"Transaction addition failed: {str(e)}")

        elif choice == '4':
            print_expenses(session, user.id)

        elif choice == '5':
            print_incomes(session, user.id)

        elif choice == '6':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

def main():
    engine = create_engine('sqlite:///finance_tracker.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    options = [
        {"option": "Create an account"},
        {"option": "Login"},
        {"option": "Quit"}
    ]

    while True:
        print("\nOptions:")
        for i, option in enumerate(options):
            print(f"{i + 1}. {option['option']}")

        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            create_user(session, username, password)

        elif choice == '2':
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            user = login(session, username, password)
            if user:
                user_specific_functionality(session, user)

        elif choice == '3':
            print("Quitting...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == '__main__':
    main()