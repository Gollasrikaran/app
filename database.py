import sqlite3
import pandas as pd

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, timeout=30)
        return conn
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return conn

def create_tables():
    conn = create_connection("school.db")
    if conn is not None:
        try:
            conn.executescript('''
                -- Users Table
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('SuperAdmin', 'BranchAdmin', 'Teacher')),
                    branch_id INTEGER  -- For BranchAdmin and Teachers
                );

                -- Schools Table
                CREATE TABLE IF NOT EXISTS Schools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT,
                    branch_name TEXT UNIQUE NOT NULL
                );

                -- Classes Table
                CREATE TABLE IF NOT EXISTS Classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_id INTEGER,
                    class INTEGER,
                    section TEXT,
                    no_of_students INTEGER,
                    FOREIGN KEY (branch_id) REFERENCES Schools(id) ON DELETE CASCADE
                );
                -- Teachers Table
                CREATE TABLE IF NOT EXISTS Teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_name TEXT NOT NULL,
                    school_name TEXT NOT NULL,
                    branch_name TEXT NOT NULL,
                    subject TEXT NOT NULL
                );
                
                -- Drop Subjects Table if it exists
                DROP TABLE IF EXISTS Subjects;
                
                -- Subjects Table
                CREATE TABLE IF NOT EXISTS Subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    branch_id INTEGER,
                    UNIQUE(name, branch_id),
                    FOREIGN KEY (branch_id) REFERENCES Schools(id) ON DELETE CASCADE
                );

                 -- Drop Students Table if it exists
                DROP TABLE IF EXISTS Students;
                -- Students Table
                CREATE TABLE IF NOT EXISTS Students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    class_id INTEGER,
                    FOREIGN KEY (class_id) REFERENCES Classes(id) ON DELETE CASCADE
                );
                
                -- Chapters Table
                CREATE TABLE IF NOT EXISTS Chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    subject_id INTEGER,
                    FOREIGN KEY (subject_id) REFERENCES Subjects(id) ON DELETE CASCADE
                );

                -- Topics Table
               
                DROP TABLE IF EXISTS Topics;
                CREATE TABLE IF NOT EXISTS Topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    chapter_id INTEGER,
                    evaluation TEXT,
                    FOREIGN KEY (chapter_id) REFERENCES Chapters(id) ON DELETE CASCADE
                );
            ''')
            create_default_users(conn) # Function to create default users
            conn.close()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
    else:
        print("Error: Unable to connect to the database.")


def create_default_users(conn):
    """Creates default users in the Users table."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users")
        count = cursor.fetchone()[0]
        if count == 0:
            # Insert default SuperAdmin user
            cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
                            ("admin", "admin", "SuperAdmin"))
            # Get the branch_id for the "Malakpet"
            cursor.execute("SELECT id FROM Schools WHERE branch_name = ?", ("Malakpet",))
            malakpet_branch_id = cursor.fetchone()
            # Insert default BranchAdmin user with the corresponding branch_id
            if malakpet_branch_id:
                cursor.execute("INSERT INTO Users (username, password, role, branch_id) VALUES (?, ?, ?, ?)",
                            ("malakpet_admin", "admin", "BranchAdmin", malakpet_branch_id[0]))
            else:
                cursor.execute("INSERT INTO Users (username, password, role, branch_id) VALUES (?, ?, ?, NULL)",
                            ("malakpet_admin", "admin", "BranchAdmin", ))

            # Get the branch_id for the "Dilshuknagar"
            cursor.execute("SELECT id FROM Schools WHERE branch_name = ?", ("Dilshuknagar",))
            dilshuknagar_branch_id = cursor.fetchone()
            # Insert default Teacher user with the corresponding branch_id
            if dilshuknagar_branch_id:
               cursor.execute("INSERT INTO Users (username, password, role, branch_id) VALUES (?, ?, ?, ?)",
                           ("teacher1", "admin", "Teacher", dilshuknagar_branch_id[0]))
            else:
               cursor.execute("INSERT INTO Users (username, password, role, branch_id) VALUES (?, ?, ?, NULL)",
                           ("teacher1", "admin", "Teacher"))
            
             # Get the branch_id for the "Malakpet"
            cursor.execute("SELECT id FROM Schools WHERE branch_name = ?", ("Malakpet",))
            malakpet_branch_id = cursor.fetchone()
            # Insert default Teacher user for Malakpet with the corresponding branch_id
            if malakpet_branch_id:
               cursor.execute("INSERT INTO Users (username, password, role, branch_id) VALUES (?, ?, ?, ?)",
                           ("teacher2", "admin", "Teacher", malakpet_branch_id[0]))
            else:
                cursor.execute("INSERT INTO Users (username, password, role, branch_id) VALUES (?, ?, ?, NULL)",
                           ("teacher2", "admin", "Teacher"))
             
            
            # Get the branch_id for the "Dilshuknagar"
            cursor.execute("SELECT id FROM Schools WHERE branch_name = ?", ("Dilshuknagar",))
            dilshuknagar_branch_id = cursor.fetchone()
             # Insert default BranchAdmin user with the corresponding branch_id
            if dilshuknagar_branch_id:
                 cursor.execute("INSERT INTO Users (username, password, role, branch_id) VALUES (?, ?, ?, ?)",
                           ("dilshuknagar_admin", "admin", "BranchAdmin", dilshuknagar_branch_id[0]))
            else:
                 cursor.execute("INSERT INTO Users (username, password, role, branch_id) VALUES (?, ?, ?, NULL)",
                           ("dilshuknagar_admin", "admin", "BranchAdmin"))


            conn.commit()
            print("Default users added successfully.")
    except sqlite3.Error as e:
        print(f"Error creating default users: {e}")


def load_data(query):
    conn = create_connection("school.db")
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_classes(branch_id):
    conn = create_connection("school.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Classes WHERE branch_id = ?
        """, (branch_id,))
        classes = cursor.fetchall()
        return classes
    except sqlite3.Error as e:
        print(f"Error fetching classes: {e}")
    finally:
        conn.close()

def add_student(class_id, student_name):
    conn = create_connection("school.db")
    try:
        cursor = conn.cursor()
         # Check if class exists
        cursor.execute("SELECT * FROM Classes WHERE id = ?", (class_id,))
        existing_class = cursor.fetchone()
        if not existing_class:
          print(f"Error: Class with id '{class_id}' does not exist.")
          return False
        cursor.execute("""
            INSERT INTO Students (student_name, class_id) VALUES (?, ?)
        """, (student_name, class_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding student: {e}")
        return False
    finally:
        conn.close()

# Create tables once on the first run
create_tables()
