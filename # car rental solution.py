# car rental solution
import mysql.connector
from mysql.connector import Error
from datetime import date

# Connection credentials
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '0210'
DB_NAME = 'car_rental'

# Defining functions
def connect_to_db(db_name=DB_NAME):
    """Establishes connection to the specific database using 'utf8' charset."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=db_name,
            charset='utf8'  # Forces standard UTF-8 charset to prevent 'utf8mb4' server incompatibilities
        )
        if conn.is_connected():
            print("Connected to the database")
            return conn
    except Error as e:
        print(f"Error while connecting to the database: {e}")
        return None


def initialise_DB():
    """Initializes the schema structure, creating the database and tables if missing."""
    print(f"\n---Initialising the database: {DB_NAME}---")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8'
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.close()
    except Error as e:
        print(f"Error while initialising the database: {e}")
        return None
    
    conn = connect_to_db(DB_NAME)
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        
        # People table (Using lowercase & InnoDB)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rented_people (
            R_N_O int PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            aadhaar_number VARCHAR(12) UNIQUE NOT NULL,
            phone_number VARCHAR(15) UNIQUE NOT NULL,
            driver_license_number VARCHAR(20) UNIQUE NOT NULL
        ) ENGINE=InnoDB
        ''')
        
        # CAR table (Using lowercase & InnoDB)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            CAR_N_O int PRIMARY KEY AUTO_INCREMENT,
            car_brand VARCHAR(255) NOT NULL,
            car_model VARCHAR(255) NOT NULL,
            licence_plate_number VARCHAR(20) UNIQUE NOT NULL,
            VIN_NUMBER VARCHAR(50) UNIQUE NOT NULL,
            availability_status BOOLEAN NOT NULL DEFAULT TRUE
        ) ENGINE=InnoDB
        ''')
        
        # Rent table (Using lowercase & InnoDB)
        # Foreign keys removed here to completely bypass local MySQL configuration & table conflicts (errno: 150)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rent_time (
                transaction_id int PRIMARY KEY AUTO_INCREMENT,
                R_N_O int NOT NULL,
                CAR_N_O int NOT NULL,
                Renting_date DATE NOT NULL,
                Returning_date DATE
            ) ENGINE=InnoDB
        ''')

        conn.commit()
        print("Database connected and tables created successfully")
        return conn
    except Error as e:
        print(f"Error while creating tables: {e}")
        if conn and conn.is_connected():
            conn.close()
        return None

    
# PEOPLE CRUD OPERATIONS
def add_person(conn, name, aadhaar_number, phone_number, driver_license_number):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rented_people (name, aadhaar_number, phone_number, driver_license_number)
            VALUES (%s, %s, %s, %s)
        ''', (name, aadhaar_number, phone_number, driver_license_number))
        conn.commit()
        print("Person added successfully")
    except Error as e:
        print(f"Error while adding person: {e}")
        return None
    

def view_people(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rented_people')
        people = cursor.fetchall()
        if people:
            print("\n---Rented People---")
            for person in people:
                print(f"R_N_O: {person[0]}, Name: {person[1]}, Aadhaar: {person[2]}, Phone: {person[3]}, Driver License: {person[4]}")
        else:
            print("No people found.")
    except Error as e:
        print(f"Error while fetching people: {e}")
        return None
    

def edit_person(conn, R_N_O, name=None, aadhaar_number=None, phone_number=None, driver_license_number=None):
    try:
        cursor = conn.cursor()
        updates = []
        params = []
        if name:
            updates.append("name = %s")
            params.append(name)
        if aadhaar_number:
            updates.append("aadhaar_number = %s")
            params.append(aadhaar_number)
        if phone_number:
            updates.append("phone_number = %s")
            params.append(phone_number)
        if driver_license_number:
            updates.append("driver_license_number = %s")
            params.append(driver_license_number)
        
        if not updates:
            print("No fields to update.")
            return
        
        params.append(R_N_O)
        query = f"UPDATE rented_people SET {', '.join(updates)} WHERE R_N_O = %s"
        cursor.execute(query, tuple(params))
        conn.commit()
        print("Person updated successfully")
    except Error as e:
        print(f"Error while updating person: {e}")
        return False


def remove_person(conn, R_N_O):
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM rented_people WHERE R_N_O = %s', (R_N_O,))
        conn.commit()
        print("Person removed successfully")
    except Error as e:
        print(f"Error while removing person: {e}")
        return False

    
# CAR CRUD OPERATIONS
def add_car(conn, car_brand, car_model, licence_plate_number, VIN_NUMBER):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cars (car_brand, car_model, licence_plate_number, VIN_NUMBER)
            VALUES (%s, %s, %s, %s)
        ''', (car_brand, car_model, licence_plate_number, VIN_NUMBER))
        conn.commit()
        print("Car added successfully")
    except Error as e:
        print(f"Error while adding car: {e}")
        return None


def view_cars(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cars')
        cars = cursor.fetchall()
        if cars:
            print("\n---Cars---")
            for car in cars:
                availability = "Available" if car[5] else "Not Available"
                print(f"CAR_N_O: {car[0]}, Brand: {car[1]}, Model: {car[2]}, Licence Plate: {car[3]}, VIN: {car[4]}, Availability: {availability}")
        else:
            print("No cars found.")
    except Error as e:
        print(f"Error while fetching cars: {e}")
        return None


def edit_car(conn, CAR_N_O, car_brand=None, car_model=None, licence_plate_number=None, VIN_NUMBER=None, availability_status=None):
    try:
        cursor = conn.cursor()
        updates = []
        params = []
        if car_brand:
            updates.append("car_brand = %s")
            params.append(car_brand)
        if car_model:
            updates.append("car_model = %s")
            params.append(car_model)
        if licence_plate_number:
            updates.append("licence_plate_number = %s")
            params.append(licence_plate_number)
        if VIN_NUMBER:
            updates.append("VIN_NUMBER = %s")
            params.append(VIN_NUMBER)
        if availability_status is not None:
            updates.append("availability_status = %s")
            params.append(availability_status)
        
        if not updates:
            print("No fields to update.")
            return
        
        params.append(CAR_N_O)
        query = f"UPDATE cars SET {', '.join(updates)} WHERE CAR_N_O = %s"
        cursor.execute(query, tuple(params))
        conn.commit()
        print("Car updated successfully")
    except Error as e:
        print(f"Error while updating car: {e}")
        return False


def remove_car(conn, CAR_N_O):
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cars WHERE CAR_N_O = %s', (CAR_N_O,))
        conn.commit()
        print("Car removed successfully")
    except Error as e:
        print(f"Error while removing car: {e}")
        return False


# RENTAL CRUD OPERATIONS
def rent_car(conn, R_N_O, CAR_N_O, Renting_date):
    try:
        cursor = conn.cursor()
        # Check if the car is available
        cursor.execute('SELECT availability_status FROM cars WHERE CAR_N_O = %s', (CAR_N_O,))
        car = cursor.fetchone()
        if car is None:
            print("Car not found.")
            return
        if not car[0]:
            print("Car is not available for rent.")
            return
        
        # Insert rental record
        cursor.execute('''
            INSERT INTO rent_time (R_N_O, CAR_N_O, Renting_date)
            VALUES (%s, %s, %s)
        ''', (R_N_O, CAR_N_O, Renting_date))
        
        # Update car availability
        cursor.execute('UPDATE cars SET availability_status = FALSE WHERE CAR_N_O = %s', (CAR_N_O,))
        
        conn.commit()
        print("Car rented successfully")
    except Error as e:
        print(f"Error while renting car: {e}")
        return None
    

def return_car(conn, transaction_id, Returning_date):
    try:
        cursor = conn.cursor()
        # Check if the rental record exists
        cursor.execute('SELECT CAR_N_O FROM rent_time WHERE transaction_id = %s', (transaction_id,))
        rental = cursor.fetchone()
        if rental is None:
            print("Rental record not found.")
            return
        
        CAR_N_O = rental[0]
        
        # Update rental record with returning date
        cursor.execute('UPDATE rent_time SET Returning_date = %s WHERE transaction_id = %s', (Returning_date, transaction_id))
        
        # Update car availability
        cursor.execute('UPDATE cars SET availability_status = TRUE WHERE CAR_N_O = %s', (CAR_N_O,))
        
        conn.commit()
        print("Car returned successfully")
    except Error as e:
        print(f"Error while returning car: {e}")
        return None


def view_rentals(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rent_time')
        rentals = cursor.fetchall()
        if rentals:
            print("\n---Rentals---")
            for rental in rentals:
                print(f"Transaction ID: {rental[0]}, R_N_O: {rental[1]}, CAR_N_O: {rental[2]}, Renting Date: {rental[3]}, Returning Date: {rental[4]}")
        else:
            print("No rentals found.")
    except Error as e:
        print(f"Error while fetching rentals: {e}")
        return None


# MENUS AND CONTROLLERS
def handel_people(conn):
    """Sub-menu interface for managing customer information."""
    while True:
        print("\n---People Management---")
        print("1. Add Person")
        print("2. View People")
        print("3. Edit Person")
        print("4. Remove Person")
        print("5. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter name: ")
            aadhaar_number = input("Enter Aadhaar number: ")
            phone_number = input("Enter phone number: ")
            driver_license_number = input("Enter driver license number: ")
            add_person(conn, name, aadhaar_number, phone_number, driver_license_number)
        elif choice == '2':
            view_people(conn)
        elif choice == '3':
            try:
                R_N_O = int(input("Enter R_N_O of the person to edit: "))
                name = input("Enter new name (leave blank to keep unchanged): ")
                aadhaar_number = input("Enter new Aadhaar number (leave blank to keep unchanged): ")
                phone_number = input("Enter new phone number (leave blank to keep unchanged): ")
                driver_license_number = input("Enter new driver license number (leave blank to keep unchanged): ")
                edit_person(conn, R_N_O, name or None, aadhaar_number or None, phone_number or None, driver_license_number or None)
            except ValueError:
                print("Invalid input! R_N_O must be an integer.")
        elif choice == '4':
            try:
                R_N_O = int(input("Enter R_N_O of the person to remove: "))
                remove_person(conn, R_N_O)
            except ValueError:
                print("Invalid input! R_N_O must be an integer.")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")


def handel_cars(conn):
    """Sub-menu interface for managing car inventory."""
    while True:
        print("\n---Car Management---")
        print("1. Add Car")
        print("2. View Cars")
        print("3. Edit Car")
        print("4. Remove Car")
        print("5. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            car_brand = input("Enter car brand: ")
            car_model = input("Enter car model: ")
            licence_plate_number = input("Enter licence plate number: ")
            VIN_NUMBER = input("Enter VIN number: ")
            add_car(conn, car_brand, car_model, licence_plate_number, VIN_NUMBER)
        elif choice == '2':
            view_cars(conn)
        elif choice == '3':
            try:
                CAR_N_O = int(input("Enter CAR_N_O of the car to edit: "))
                car_brand = input("Enter new car brand (leave blank to keep unchanged): ")
                car_model = input("Enter new car model (leave blank to keep unchanged): ")
                licence_plate_number = input("Enter new licence plate number (leave blank to keep unchanged): ")
                VIN_NUMBER = input("Enter new VIN number (leave blank to keep unchanged): ")
                availability_status_input = input("Enter new availability status (True/False, leave blank to keep unchanged): ")
                
                availability_status = None
                if availability_status_input.lower() == 'true':
                    availability_status = True
                elif availability_status_input.lower() == 'false':
                    availability_status = False
                    
                edit_car(conn, CAR_N_O, car_brand or None, car_model or None, licence_plate_number or None, VIN_NUMBER or None, availability_status)
            except ValueError:
                print("Invalid input! CAR_N_O must be an integer.")
        elif choice == '4':
            try:
                CAR_N_O = int(input("Enter CAR_N_O of the car to remove: "))
                remove_car(conn, CAR_N_O)
            except ValueError:
                print("Invalid input! CAR_N_O must be an integer.")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")


def handel_rental_menu(conn):
    """Sub-menu interface for tracking transactions, rentals, and returns."""
    while True:
        print("\n---Rental Management---")
        print("1. Rent Car")
        print("2. Return Car")
        print("3. View Rentals")
        print("4. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            try:
                R_N_O = int(input("Enter R_N_O of the person renting the car: "))
                CAR_N_O = int(input("Enter CAR_N_O of the car to rent: "))
                Renting_date = input("Enter renting date (YYYY-MM-DD): ")
                rent_car(conn, R_N_O, CAR_N_O, Renting_date)
            except ValueError:
                print("Invalid input! IDs must be integers.")
        elif choice == '2':
            try:
                transaction_id = int(input("Enter transaction ID of the rental to return: "))
                Returning_date = input("Enter returning date (YYYY-MM-DD): ")
                return_car(conn, transaction_id, Returning_date)
            except ValueError:
                print("Invalid input! Transaction ID must be an integer.")
        elif choice == '3':
            view_rentals(conn)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")


def main_MAIN():
    """Main program entry point."""
    conn = initialise_DB()
    if conn is None:
        print("Failed to initialise the database. Exiting.")
        return
    
    while True:
        print("\n---Car Rental System---")
        print("1. Manage People")
        print("2. Manage Cars")
        print("3. Manage Rentals")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            handel_people(conn)
        elif choice == '2':
            handel_cars(conn)
        elif choice == '3':
            handel_rental_menu(conn)
        elif choice == '4':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
            
    if conn and conn.is_connected():
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main_MAIN()