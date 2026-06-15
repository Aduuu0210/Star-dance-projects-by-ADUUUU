import mysql.connector
from mysql.connector import Error
from datetime import date

# --- Configuration ---
# IMPORTANT: Replace these with your actual MySQL credentials
DB_HOST = "localhost"
# The database name as specified by the company name
DB_NAME = "Car_Rental_Solutions_LLC"
DB_USER = "root"  # MySQL username
DB_PASSWORD = "0210"  # MySQL password
# ---------------------

def connect_to_db(db_name=DB_NAME):
    """
    Establishes a connection to the MySQL database.
    FIXED: Explicitly uses 'utf8' for compatibility with older MySQL servers.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            database=db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            # --- FIX APPLIED HERE ---
            # Ensure all connections use the compatible 'utf8' charset
            charset='utf8'
            # ------------------------
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"❌ Error connecting to MySQL (Check credentials and MySQL status): {e}")
        return None

def initialize_database():
    """
    Ensures the database exists and creates all three tables.
    Explicitly uses 'utf8' charset during the initial connection
    to prevent 'Unknown character set: 'utf8mb4'' error on older servers.
    """
    print(f"\n--- Initializing Database: {DB_NAME} ---")

    # 1. Connect without specifying a DB to create the DB first
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            # --- FIX APPLIED HERE (Kept from previous attempt) ---
            # Use 'utf8' for connection compatibility
            charset='utf8'
            # ----------------------------------------------------
        )
        cursor = conn.cursor()

        # We also explicitly define character set and collation for the database
        # to ensure it's compatible if the 'utf8mb4' error persists.
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci")
        conn.close()
    except Error as e:
        print(f"❌ Error during database creation: {e}")
        return None

    # 2. Connect to the new database
    # This now calls the fixed connect_to_db function above.
    conn = connect_to_db(DB_NAME)
    if conn is None:
        return None

    try:
        cursor = conn.cursor()

        # --- Table 1: Rented_people (Renter Details) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Rented_people (
                R_N_O INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                aadhar_number VARCHAR(12) UNIQUE NOT NULL,
                phone_number VARCHAR(15) UNIQUE NOT NULL,
                driver_licence_id VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        # --- Table 2: CARS (Vehicle Inventory) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CARS (
                CAR_N_O INT AUTO_INCREMENT PRIMARY KEY,
                car_brand VARCHAR(50) NOT NULL,
                model VARCHAR(50) NOT NULL,
                licence_plate_number VARCHAR(20) UNIQUE NOT NULL,
                VIN_number VARCHAR(50) UNIQUE NOT NULL,
                is_available BOOLEAN DEFAULT TRUE
            )
        """)
        # --- Table 3: Rent_Time (Transaction Log) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Rent_Time (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                R_N_O INT NOT NULL,
                CAR_N_O INT NOT NULL,
                Renting_Date DATE NOT NULL,
                Returning_Date DATE,
                FOREIGN KEY (R_N_O) REFERENCES Rented_people(R_N_O) ON DELETE RESTRICT,
                FOREIGN KEY (CAR_N_O) REFERENCES CARS(CAR_N_O) ON DELETE RESTRICT
            )
        """)

        conn.commit()
        print("✅ Database connection established and tables ensured.")
        return conn

    except Error as e:
        print(f"❌ Error initializing tables: {e}")
        if conn and conn.is_connected():
            conn.close()
        return None

# =================================================================
#               CRUD (Create, Read, Update, Delete) Functions
# =================================================================

# --- RENTED PEOPLE CRUD ---

def add_new_person(conn, name, aadhar, phone, license_id):
    """Inserts a new person into the Rented_people table."""
    sql = "INSERT INTO Rented_people (name, aadhar_number, phone_number, driver_licence_id) VALUES (%s, %s, %s, %s)"
    val = (name, aadhar, phone, license_id)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, val)
        conn.commit()
        print(f"✅ Person added: {name} (ID: {cursor.lastrowid})")
        return cursor.lastrowid
    except Error as e:
        print(f"❌ Error adding person (Check Aadhar/Phone/License ID uniqueness): {e}")
        return None

def view_people(conn):
    """Fetches and prints all people in the system."""
    sql = "SELECT R_N_O, name, aadhar_number, phone_number, driver_licence_id FROM Rented_people"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()

        if not records:
            print("\nDatabase is empty.")
            return

        print("\n--- 🧑 Rented People Inventory ---")
        print("{:<5} {:<25} {:<15} {:<15} {:<20}".format(
              "ID", "Name", "Aadhar No.", "Phone No.", "License ID"))
        print("-" * 80)

        for record in records:
            print("{:<5} {:<25} {:<15} {:<15} {:<20}".format(*record))

    except Error as e:
        print(f"❌ Error viewing people: {e}")

def edit_person(conn, r_n_o, name=None, phone=None):
    """Updates the name and/or phone number of a person."""
    updates = []
    values = []
    if name:
        updates.append("name = %s")
        values.append(name)
    if phone:
        updates.append("phone_number = %s")
        values.append(phone)

    if not updates:
        print("⚠️ No updates specified.")
        return False

    sql = "UPDATE Rented_people SET " + ", ".join(updates) + " WHERE R_N_O = %s"
    values.append(r_n_o)

    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"✅ Person ID {r_n_o} updated successfully.")
            return True
        else:
            print(f"⚠️ Person ID {r_n_o} not found or no changes made.")
            return False
    except Error as e:
        print(f"❌ Error editing person: {e}")
        return False

def remove_person(conn, r_n_o):
    """Deletes a person record if they have no active rentals."""
    try:
        cursor = conn.cursor()
        # The ON DELETE RESTRICT in the FK definition prevents deletion
        # if the person is referenced in Rent_Time.
        cursor.execute("DELETE FROM Rented_people WHERE R_N_O = %s", (r_n_o,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"✅ Person ID {r_n_o} removed successfully.")
            return True
        else:
            print(f"⚠️ Person ID {r_n_o} not found or has existing rental history.")
            return False
    except Error as e:
        if 'foreign key constraint' in str(e).lower():
            print(f"❌ Error: Person ID {r_n_o} cannot be deleted because they are linked to a rental transaction.")
        else:
            print(f"❌ Error removing person: {e}")
        return False

# --- CARS CRUD ---

def add_new_car(conn, brand, model, license_plate, vin):
    """Inserts a new car into the CARS inventory."""
    sql = "INSERT INTO CARS (car_brand, model, licence_plate_number, VIN_number) VALUES (%s, %s, %s, %s)"
    val = (brand, model, license_plate, vin)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, val)
        conn.commit()
        print(f"✅ Car added: {brand} {model} (ID: {cursor.lastrowid})")
        return cursor.lastrowid
    except Error as e:
        print(f"❌ Error adding car (Check License Plate/VIN uniqueness): {e}")
        return None

def view_cars(conn):
    """Fetches and prints all cars in the inventory."""
    sql = "SELECT CAR_N_O, car_brand, model, licence_plate_number, VIN_number, is_available FROM CARS"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()

        if not records:
            print("\nCar inventory is empty.")
            return

        print("\n--- 🚗 Current Car Inventory ---")
        print("{:<5} {:<15} {:<15} {:<15} {:<30} {:<10}".format(
              "ID", "Brand", "Model", "License Plate", "VIN", "Available"))
        print("-" * 100)

        for record in records:
            availability = "YES" if record[5] else "NO"
            print("{:<5} {:<15} {:<15} {:<15} {:<30} {:<10}".format(
                  record[0], record[1], record[2], record[3], record[4], availability))

    except Error as e:
        print(f"❌ Error viewing cars: {e}")

def edit_car(conn, car_n_o, brand=None, model=None, license_plate=None):
    """Updates the brand, model, and/or license plate of a car."""
    updates = []
    values = []
    if brand:
        updates.append("car_brand = %s")
        values.append(brand)
    if model:
        updates.append("model = %s")
        values.append(model)
    if license_plate:
        updates.append("licence_plate_number = %s")
        values.append(license_plate)

    if not updates:
        print("⚠️ No updates specified.")
        return False

    sql = "UPDATE CARS SET " + ", ".join(updates) + " WHERE CAR_N_O = %s"
    values.append(car_n_o)

    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"✅ Car ID {car_n_o} updated successfully.")
            return True
        else:
            print(f"⚠️ Car ID {car_n_o} not found or no changes made.")
            return False
    except Error as e:
        print(f"❌ Error editing car: {e}")
        return False

def remove_car(conn, car_n_o):
    """Deletes a car record if it has no active rentals."""
    try:
        cursor = conn.cursor()
        # The ON DELETE RESTRICT in the FK definition prevents deletion
        # if the car is referenced in Rent_Time.
        cursor.execute("DELETE FROM CARS WHERE CAR_N_O = %s", (car_n_o,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"✅ Car ID {car_n_o} removed successfully.")
            return True
        else:
            print(f"⚠️ Car ID {car_n_o} not found or has existing rental history.")
            return False
    except Error as e:
        if 'foreign key constraint' in str(e).lower():
            print(f"❌ Error: Car ID {car_n_o} cannot be deleted because it is currently linked to a rental transaction.")
        else:
            print(f"❌ Error removing car: {e}")
        return False

# --- RENTAL TRANSACTION FUNCTIONS ---

def rent_car(conn, r_n_o, car_n_o):
    """Records a car rental transaction and updates car availability."""

    cursor = conn.cursor(dictionary=True)

    # 1. Check if the car is available
    cursor.execute("SELECT is_available, licence_plate_number FROM CARS WHERE CAR_N_O = %s", (car_n_o,))
    car_status = cursor.fetchone()

    if not car_status:
        print(f"⚠️ Error: Car ID {car_n_o} not found.")
        return False

    if not car_status['is_available']:
        print(f"⚠️ Car {car_status['licence_plate_number']} (ID: {car_n_o}) is already rented.")
        return False

    # 2. Check if the Renter exists
    cursor.execute("SELECT name FROM Rented_people WHERE R_N_O = %s", (r_n_o,))
    renter = cursor.fetchone()

    if not renter:
        print(f"⚠️ Error: Renter ID {r_n_o} not found.")
        return False

    try:
        # 3. Record the rental time
        sql_rent = "INSERT INTO Rent_Time (R_N_O, CAR_N_O, Renting_Date) VALUES (%s, %s, %s)"
        val_rent = (r_n_o, car_n_o, date.today())
        cursor.execute(sql_rent, val_rent)

        # 4. Update car availability status
        sql_update = "UPDATE CARS SET is_available = FALSE WHERE CAR_N_O = %s"
        cursor.execute(sql_update, (car_n_o,))

        conn.commit()
        print(f"🎉 SUCCESS! {renter['name']} rented car {car_status['licence_plate_number']} today.")
        return True
    except Error as e:
        print(f"❌ Error processing rental: {e}")
        conn.rollback()
        return False

def return_car(conn, car_n_o):
    """Records the car return date and updates car availability."""

    cursor = conn.cursor(dictionary=True)

    # 1. Find the active rental transaction for this car
    sql_find_active = """
        SELECT transaction_id, R_N_O
        FROM Rent_Time
        WHERE CAR_N_O = %s AND Returning_Date IS NULL
    """
    cursor.execute(sql_find_active, (car_n_o,))
    active_rental = cursor.fetchone()

    if not active_rental:
        print(f"⚠️ Error: Car ID {car_n_o} is not currently checked out.")
        # Check car table just in case the transaction log is inconsistent
        cursor.execute("SELECT is_available FROM CARS WHERE CAR_N_O = %s", (car_n_o,))
        car_status = cursor.fetchone()
        if car_status and not car_status['is_available']:
             print("Please check the Rent_Time table manually for potential issues.")
        return False

    try:
        # 2. Update the Rent_Time table with the return date
        sql_update_rent = "UPDATE Rent_Time SET Returning_Date = %s WHERE transaction_id = %s"
        cursor.execute(sql_update_rent, (date.today(), active_rental['transaction_id']))

        # 3. Update car availability status
        sql_update_car = "UPDATE CARS SET is_available = TRUE WHERE CAR_N_O = %s"
        cursor.execute(sql_update_car, (car_n_o,))

        conn.commit()
        print(f"✅ Car ID {car_n_o} successfully returned and marked available.")
        return True
    except Error as e:
        print(f"❌ Error processing return: {e}")
        conn.rollback()
        return False


def view_current_rentals(conn):
    """Fetches and prints details of all currently rented cars."""
    query = """
    SELECT
        RT.transaction_id, RP.name, C.car_brand, C.model, C.licence_plate_number, RT.Renting_Date
    FROM Rent_Time RT
    JOIN Rented_people RP ON RT.R_N_O = RP.R_N_O
    JOIN CARS C ON RT.CAR_N_O = C.CAR_N_O
    WHERE RT.Returning_Date IS NULL
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()

        if not records:
            print("\nNo cars are currently rented out.")
            return

        print("\n--- 📝 Current Rentals (Cars NOT Returned) ---")
        print("{:<5} {:<20} {:<15} {:<15} {:<15} {:<12}".format(
              "TID", "Renter Name", "Brand", "Model", "License Plate", "Rented Date"))
        print("-" * 85)

        for record in records:
            # Format the date object for clean printing
            rent_date_str = record[5].strftime('%Y-%m-%d') if record[5] else 'N/A'
            print("{:<5} {:<20} {:<15} {:<15} {:<15} {:<12}".format(
                  record[0], record[1], record[2], record[3], record[4], rent_date_str))

    except Error as e:
        print(f"❌ Error viewing rentals: {e}")

# =================================================================
#                         CLI INTERFACE
# =================================================================

def handle_person_menu(conn):
    """Handles the Rented People management options."""
    while True:
        print("\n" + "="*40)
        print("  👤 RENTER MANAGEMENT (Rented_people)")
        print("="*40)
        print("  1. INPUT: Add New Renter")
        print("  2. DISPLAY: View All Renters")
        print("  3. EDIT: Update Renter Details (Name/Phone)")
        print("  4. REMOVE: Delete Renter")
        print("  5. Back to Main Menu")
        print("-" * 40)
        choice = input("Enter choice (1-5): ")

        if choice == '1':
            name = input("Name: ")
            aadhar = input("Aadhar Number (12 digits): ")
            phone = input("Phone Number: ")
            license_id = input("Driver License ID: ")
            add_new_person(conn, name, aadhar, phone, license_id)

        elif choice == '2':
            view_people(conn)

        elif choice == '3':
            try:
                view_people(conn)
                r_n_o = int(input("Enter Renter ID (R_N_O) to edit: "))
                name = input("Enter new Name (leave blank to skip): ")
                phone = input("Enter new Phone Number (leave blank to skip): ")
                edit_person(conn, r_n_o, name if name else None, phone if phone else None)
            except ValueError:
                print("⚠️ Invalid ID input. Must be a number.")

        elif choice == '4':
            try:
                view_people(conn)
                r_n_o = int(input("Enter Renter ID (R_N_O) to remove: "))
                remove_person(conn, r_n_o)
            except ValueError:
                print("⚠️ Invalid ID input. Must be a number.")

        elif choice == '5':
            break

        else:
            print("⚠️ Invalid choice. Please try again.")

def handle_car_menu(conn):
    """Handles the CARS inventory management options."""
    while True:
        print("\n" + "="*40)
        print("  🚗 CAR INVENTORY (CARS)")
        print("="*40)
        print("  1. INPUT: Add New Car")
        print("  2. DISPLAY: View All Cars")
        print("  3. EDIT: Update Car Details (Brand/Model/Plate)")
        print("  4. REMOVE: Delete Car")
        print("  5. Back to Main Menu")
        print("-" * 40)
        choice = input("Enter choice (1-5): ")

        if choice == '1':
            brand = input("Brand: ")
            model = input("Model: ")
            license_plate = input("License Plate Number: ")
            vin = input("VIN Number: ")
            add_new_car(conn, brand, model, license_plate, vin)

        elif choice == '2':
            view_cars(conn)

        elif choice == '3':
            try:
                view_cars(conn)
                car_n_o = int(input("Enter Car ID (CAR_N_O) to edit: "))
                brand = input("Enter new Brand (leave blank to skip): ")
                model = input("Enter new Model (leave blank to skip): ")
                license_plate = input("Enter new License Plate (leave blank to skip): ")
                edit_car(conn, car_n_o, brand if brand else None, model if model else None, license_plate if license_plate else None)
            except ValueError:
                print("⚠️ Invalid ID input. Must be a number.")

        elif choice == '4':
            try:
                view_cars(conn)
                car_n_o = int(input("Enter Car ID (CAR_N_O) to remove: "))
                remove_car(conn, car_n_o)
            except ValueError:
                print("⚠️ Invalid ID input. Must be a number.")

        elif choice == '5':
            break

        else:
            print("⚠️ Invalid choice. Please try again.")

def handle_rental_menu(conn):
    """Handles the Rental Transaction options."""
    while True:
        print("\n" + "="*40)
        print("  📝 RENTAL TRANSACTIONS (Rent_Time)")
        print("="*40)
        print("  1. Rent a Car (New Rental)")
        print("  2. Return a Car (Complete Rental)")
        print("  3. DISPLAY: View Current Active Rentals")
        print("  4. Back to Main Menu")
        print("-" * 40)
        choice = input("Enter choice (1-4): ")

        if choice == '1':
            try:
                view_people(conn)
                r_n_o = int(input("Enter Renter ID (R_N_O): "))
                view_cars(conn)
                car_n_o = int(input("Enter Car ID (CAR_N_O) to rent: "))
                rent_car(conn, r_n_o, car_n_o)
            except ValueError:
                print("⚠️ Invalid ID input. Must be a number.")

        elif choice == '2':
            try:
                view_current_rentals(conn)
                car_n_o = int(input("Enter Car ID (CAR_N_O) being returned: "))
                return_car(conn, car_n_o)
            except ValueError:
                print("⚠️ Invalid ID input. Must be a number.")

        elif choice == '3':
            view_current_rentals(conn)

        elif choice == '4':
            break

        else:
            print("⚠️ Invalid choice. Please try again.")


def main():
    """Main function to run the CLI system."""
    conn = initialize_database()

    if conn is None:
        print("\nExiting program due to connection error.")
        return

    while True:
        print("\n\n" + "#"*60)
        print("############## CAR RENTAL SOLUTIONS LLC - MAIN MENU ##############")
        print("#"*60)
        print("1. Renter Management (People Data)")
        print("2. Car Inventory Management (Vehicle Data)")
        print("3. Rental Transactions (Rent/Return/Active)")
        print("4. Exit Program")
        print("#"*60)

        main_choice = input("Enter your choice (1-4): ")

        if main_choice == '1':
            handle_person_menu(conn)
        elif main_choice == '2':
            handle_car_menu(conn)
        elif main_choice == '3':
            handle_rental_menu(conn)
        elif main_choice == '4':
            break
        else:
            print("⚠️ Invalid choice. Please enter a number between 1 and 4.")

    # Close the connection upon exit
    if conn and conn.is_connected():
        conn.close()
        print("\nGoodbye! MySQL connection closed.")


if __name__ == "__main__":
    main()
