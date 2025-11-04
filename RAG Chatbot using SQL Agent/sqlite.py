import sqlite3

# 1. Connect to the database
# This will create the file 'my_database.db' if it doesn't exist
try:
    conn = sqlite3.connect('employee.db')
    
    # 2. Create a cursor object
    # The cursor is used to execute SQL commands
    cursor = conn.cursor()
    
    # 3. Define the SQL query to create a new table
    # Using "IF NOT EXISTS" prevents an error if the table already exists
    create_employees_table_query = """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT,
        job_role TEXT,
        join_date TEXT,
        ctc INTEGER
    );
    """

    
    # 4. Execute the SQL query
    cursor.execute(create_employees_table_query)

    # 5.Insert data into the table
    data_to_insert = [
    (190241, 'John', 'Snow', 'Data Scientist', '02-10-2022', 2444555),
    (130242, 'Steven', 'Smith', 'AI Engineer', '04-10-2021', 4235566),
    (150243, 'Stefan', 'Salvatore', 'Data Analyst', '07-10-2023', 1300555),
    (160244, 'Elizabeth', 'Olsen', 'Data Engineer', '02-10-2024', 224677),
    (170245, 'Micheal', 'Kors', 'DevOps Engineer', '02-10-2023', 24566)
]
    insert_query = """
    INSERT INTO employees (id, first_name, last_name, job_role, join_date, ctc) VALUES (?, ?, ?, ?, ?,?);
    """
    cursor.executemany(insert_query, data_to_insert)
    
    # 6. Commit the changes
    # This saves the changes to the database file
    conn.commit()
    
    print("Table 'Employees' created successfully.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # 6. Close the connection
    # It's important to close the connection when you're done
    if conn:
        conn.close()
