
from getpass import getpass

from werkzeug.security import generate_password_hash
from app.database import get_db


def create_admin():

   
    print("  PARKING MANAGEMENT SYSTEM")
    print("       CREATE ADMIN ACCOUNT")
  

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()

    password = getpass("Enter admin password: ")
    confirm_password = getpass("Confirm admin password: ")

    
    if not name or not email or not password:
        print("\nError: All fields are required.")
        return

    if len(password) < 8:
        print("\nError: Password must be at least 8 characters.")
        return

    if password != confirm_password:
        print("\nError: Passwords do not match.")
        return

    db = None

    try:
        db = get_db()

        with db.cursor() as cursor:

            
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                print("\nError: This email is already registered.")
                return

            
            password_hash = generate_password_hash(password)

            
            cursor.execute(
                """
                INSERT INTO users
                (name, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, 'admin', TRUE)
                """,
                (name, email, password_hash)
            )

        db.commit()

        print("\nAdmin account created successfully!")
        print("------------------------------------")
        print(f"Name:  {name}")
        print(f"Email: {email}")
        print("Role:  Admin")
        print("------------------------------------")
        print("You can now log in to ParkSmart.")

    except Exception as error:

        if db:
            db.rollback()

        print("\nDatabase error:", error)

    finally:
        if db:
            db.close()


if __name__ == "__main__":
    create_admin()
