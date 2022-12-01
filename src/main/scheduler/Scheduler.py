from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime



'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    if len(tokens) != 3:
        print("Failed to create patient")
        return

    patientname = tokens[1]
    patientpassword = tokens[2]
    if username_exists_patient(patientname):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(patientpassword, salt)

    patient = Patient(patientname, salt=salt, hash=hash)
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", patientname)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_patient(patientname):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, patientname)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def login_patient(tokens):
    """
    TODO: Part 1
    """
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    if len(tokens) != 3:
        print("Login failed.")
        return

    patientname = tokens[1]
    patientpassword = tokens[2]

    patient = None
    try:
        patient = Patient(patientname, password=patientpassword).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + patientname)
        current_patient = patient
    pass


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    login = False
    valid = False

    if len(tokens) != 2:
        print("Please try again!")
    else:
        valid = True

    if valid:
        if current_caregiver is None and current_patient is None:
            print("Please login first!")
        else:
            login = True
    if login:
        date = tokens[1]
        cm = ConnectionManager()
        conn = cm.create_connection()
        search_command = f"SELECT Ca.Username\
            FROM Caregivers as Ca, Availabilities as Av\
            WHERE Ca.Username = Av.Username AND Av.Time = '{date}'"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(search_command)
            total_available = cursor.fetchall()
            if len(total_available) == 0:
                print("There are no available caregivers for this date!")
            else:
                check_vac_command ="SELECT *\
                FROM Vaccines;"
                print(f"{'-'*25}\nAvailable caregivers\n{'-'*25}" )
                for item in total_available:
                    print(item['Username'])
                cursor.execute(check_vac_command)
                print(f"{'-'*35}\n{'Available Vaccines':25s}Doses\n{'-'*35}")
                for row in cursor:
                    print(f"{row['Name']:25s}{row['Doses']}")
        except pymssql.Error as e:
            print("Error occurred when checking the date")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error:", e)
        finally:
            cm.close_connection()
    pass


def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    login_as_patient = False
    valid = False

    if len(tokens) != 3:
        print("Please try again!")
    else:
        valid = True

    if valid:
        if current_caregiver is None and current_patient is None:
            print("Please login first!")
        elif current_caregiver is not None and current_patient is None:
            print("Please login as a patient!")
        else:
            login_as_patient = True
    if login_as_patient:
        date = tokens[1]
        vaccine = tokens[2]
        logged_name = current_patient.get_username()
        cm = ConnectionManager()
        conn = cm.create_connection()

        count_vaccine_cmd = f"SELECT V.Doses\
        FROM Vaccines as V\
        WHERE V.Name = '{vaccine}'"

        check_vaccine_exists_cmd = f"SELECT COUNT(Name) as count\
        FROM Vaccines AS VA\
        WHERE VA.Name = '{vaccine}'"

        check_caregiver_cmd = f"SELECT COUNT(C.Username) as num_caregivers\
        FROM Caregivers AS C, Availabilities AS AV\
        WHERE C.Username = AV.Username\
        AND AV.Time = '{date}';"

        choose_caregiver_cmd = f"SELECT TOP 1 Ca.Username as Caregiver, Av.Time, V.Name, V.Doses\
        FROM Caregivers as Ca, Availabilities as Av, Vaccines as V\
        WHERE Ca.Username = Av.Username\
        AND Av.Time = '{date}'\
        AND V.Name = '{vaccine}'\
        ORDER BY Ca.Username ASC"
        try:
            reserve_valid = False
            cursor = conn.cursor(as_dict=True)
            cursor.execute(check_vaccine_exists_cmd)
            count_vaccine = cursor.fetchall()
            cursor.execute(check_caregiver_cmd)
            count_caregivers = cursor.fetchall()

            if count_vaccine[0].get('count') == 0:
                print("Invalid vaccine type, please try again!")
            elif count_caregivers[0].get('num_caregivers') == 0:
                print("No Caregiver is available!")
            else:
                check_exist_reser = f"SELECT COUNT(Patient) as count\
                FROM Reserved AS R\
                WHERE R.patient = '{logged_name}'\
                AND R.Time = '{date}'"
                cursor.execute(count_vaccine_cmd)
                num_doses = cursor.fetchall()[0].get('Doses')
                cursor.execute(check_exist_reser)
                num_of_appointment = cursor.fetchall()[0].get('count')
                if num_of_appointment != 0:
                    print("You already reserved for this date!")
                else:
                    if num_doses == 0:
                        print("Not enough available doses!")
                    else:
                        cursor.execute(choose_caregiver_cmd)
                        reserved_caregiver = cursor.fetchall()
                        l=[]
                        for i in reserved_caregiver[0].values():
                            l.append(''.join(str(i).split('-')))
                        name = l[0]
                        appointment_id = ''.join(l[:2])
                        print(f"{'-'*25}\nReservation Detail\n{'-'*25}" )
                        print(f"Appointment ID: {appointment_id}, Caregiver username: {name}")
                        reserve_valid = True
            if reserve_valid == True:
                try:
                    update_reserved = f"INSERT INTO Reserved\
                    VALUES('{appointment_id}', '{date}', '{name}', '{logged_name}','{vaccine}')"
                    update_available = f"DELETE AV\
                    FROM Reserved AS R, Availabilities as AV\
                    WHERE R.Time = AV.Time\
                    AND AV.Username = R.Caregiver;"
                    update_vaccine = f"UPDATE Vaccines\
                    SET Doses = Doses - 1\
                    WHERE Name = '{vaccine}'"
                    cursor.execute(update_reserved)
                    conn.commit()
                    cursor.execute(update_available)
                    cursor.execute(update_vaccine)
                    conn.commit()
                    print("Reserved Successfully!")
                except pymssql.Error as e:
                    print("Error occurred when reserving")
                    print("Db-Error:", e)
            else:
                pass
        except pymssql.Error as e:
            print("Error occurred when reserving")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when reserving")
            print("Error:", e)
        finally:
            cm.close_connection()
    pass


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_caregiver
    global current_patient
    login = False
    valid = False

    if len(tokens) != 1:
        print("Please try again!")
    else:
        valid = True

    if valid:
        if current_caregiver is None and current_patient is None:
            print("Please login first!")
        else:
            login = True
    if login:
        cm = ConnectionManager()
        conn = cm.create_connection()
        if current_caregiver is not None:
            caregiver_name = current_caregiver.get_username()
            show_ca = f"SELECT Appointment_Id, Vaccine, TIME, Patient\
            FROM Reserved\
            WHERE Caregiver = '{caregiver_name}'\
            ORDER BY Appointment_Id ASC"
            cursor = conn.cursor(as_dict=True)
            cursor.execute(show_ca)
            print(f"{'-'*75}\n{'Appointment ID':20s}{'Vaccine name':20s}{'Date':20s}{'Patient Name':20}\n{'-'*75}")
            for row in cursor:
                print(f"{row['Appointment_Id']:20s}{row['Vaccine']:20s}{str(row['TIME']):20s}{row['Patient']:20s}")

        elif current_patient is not None:
            patient_name = current_patient.get_username()
            show_pa = f"SELECT Appointment_Id, Vaccine, TIME, Patient\
            FROM Reserved\
            WHERE Patient = '{patient_name}'\
            ORDER BY Appointment_Id ASC"
            cursor = conn.cursor(as_dict=True)
            cursor.execute(show_pa)
            print(f"{'-'*75}\n{'Appointment ID':20s}{'Vaccine name':20s}{'Date':20s}{'Patient Name':20}\n{'-'*75}")
            for row in cursor:
                print(f"{row['Appointment_Id']:20s}{row['Vaccine']:20s}{str(row['TIME']):20s}{row['Patient']:20s}")
        else:
            print("This statement wont be execute forever lol!")

    else:
        pass



def logout(tokens):
    """
    TODO: Part 2
    """
    pass


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
