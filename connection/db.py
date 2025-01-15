import psycopg2


dbname = 'payroll_db'
user = 'postgres'
password = 'postgres'
host = 'localhost' 
port = '5432'

def get_all_active_employees():
    # Establish a connection to the database
    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Example query to fetch data from a table within a specific schema
        cursor.execute(f"SELECT * FROM payroll_db.employees where is_deleted=False;")
        rows = cursor.fetchall()
        print(type(rows))

        # for row in rows:
        #     print(row)
        return list(rows)

    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def get_employee_by_id(id):
    # Establish a connection to the database
    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Example query to fetch data from a table within a specific schema
        cursor.execute(f"SELECT * FROM payroll_db.employees where is_deleted=False and id={id};")
        rows = cursor.fetchall()
        return rows

    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def get_timecard_by_emp(id, start_date=None, end_date=None):
    # Establish a connection to the database
    try:
        if start_date is None and end_date is None:
            connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM payroll_db.time_card 
                        where is_deleted=False 
                        and employee_id={id} 
                        order by login_date asc;
            """)
            rows = cursor.fetchall()
            return rows
        else:
            connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM payroll_db.time_card 
                        where is_deleted=False 
                        and employee_id={id} 
                        and date_added between date '{start_date}' and date '{end_date}'
                        order by date_added asc;
            """)
            rows = cursor.fetchall()
            return rows
        
    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def add_employee(employee_name, employee_type, status, daily_rate):
    # Establish a connection to the database
    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        cursor.execute("INSERT INTO payroll_db.employees (employee_name, employee_type, status, daily_rate) VALUES (%s, %s, %s, %s)", (employee_name, employee_type, status, daily_rate))
        connection.commit()  # Don't forget to commit the transaction
        return True

    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def add_time_card(employee_id, login, logout, remarks, note):
    from datetime import datetime

    # Convert string to datetime object
    # login = datetime.strptime(login, "%Y-%m-%d %H:%M:%S")
    # logout = datetime.strptime(logout, "%Y-%m-%d %H:%M:%S")
    if login != '' and logout !='':
        login = datetime.strptime(login, "%Y-%m-%dT%H:%M")
        logout = datetime.strptime(logout, "%Y-%m-%dT%H:%M")
    else:
        login = None
        logout = None


    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        cursor.execute("INSERT INTO payroll_db.time_card (employee_id, login_date, logout_date, remarks, note) VALUES (%s, %s, %s, %s, %s)", (employee_id, login, logout, remarks, note))
        connection.commit()  # Don't forget to commit the transaction
        return True

    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def update_employee(id):
    # Establish a connection to the database
    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        update_query = f"""
            UPDATE payroll_db.employees
            SET is_deleted = True
            WHERE id = {id};
        """
        # New name for the employee with employee_id = 3

        # Execute the UPDATE query with parameters
        cursor.execute(update_query)

        # Commit the transaction to make changes permanent
        connection.commit()

    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def update_time_card(id):
    # Establish a connection to the database
    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        update_query = f"""
            UPDATE payroll_db.time_card
            SET is_deleted = True
            WHERE id = {id};
        """
        # New name for the employee with employee_id = 3

        # Execute the UPDATE query with parameters
        cursor.execute(update_query)

        # Commit the transaction to make changes permanent
        connection.commit()


    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def get_employee_count(is_not_active=False):

    # Establish a connection to the database
    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        
        # Example query to fetch data from a table within a specific schema
        cursor.execute(f"SELECT count(1) FROM payroll_db.employees where is_deleted={is_not_active};")
        result = cursor.fetchone()
        count = result[0]
        
        return count

    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def get_total_emp_salary():

    # Establish a connection to the database
    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        
        # Example query to fetch data from a table within a specific schema
        cursor.execute(f"SELECT sum(daily_rate) FROM payroll_db.employees where is_deleted=False;")
        result = cursor.fetchone()
        count = result[0]
        
        return count

    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def get_all_employees():
    # Establish a connection to the database
    try:
        connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
        
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Example query to fetch data from a table within a specific schema
        cursor.execute(f"SELECT * FROM payroll_db.employees;")
        rows = cursor.fetchall()
        return list(rows)

    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

def get_timecard_min_max(id, dated_added=None):
    # Establish a connection to the database
    try:
        if dated_added is not None:
            connection = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT min(login_date), max(login_date) 
                FROM payroll_db.time_card
                where date_added = date '{dated_added}'
                and employee_id={id};
            """)
            result = cursor.fetchone()
            return result
            
        
    except Exception as error:
        print(f"Error connecting to the database: {error}")

    finally:
        # Close the cursor and connection if they were successfully created
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")