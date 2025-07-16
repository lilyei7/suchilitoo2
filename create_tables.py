import os
import sqlite3

# Set the path to your SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
SQL_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'create_incident_tables.sql')

def execute_sql_script():
    # Read SQL script
    with open(SQL_SCRIPT_PATH, 'r') as f:
        sql_script = f.read()
    
    # Connect to the SQLite database
    try:
        print("Executing SQL script to create tables...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute the SQL script
        cursor.executescript(sql_script)
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'dashboard_incident%'")
        tables = cursor.fetchall()
        
        print("Created tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        print("\nTables created successfully!")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    execute_sql_script()
