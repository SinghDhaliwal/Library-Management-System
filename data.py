import sqlite3
import pickle
from models import DataAccessAbstract, Student, Faculty, Book, Magazine, DVD 

class SQLiteManager(DataAccessAbstract):
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self.setup_database()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Successfully connected to the database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def setup_database(self):
        if not self.conn:
            print("Database connection failed. Cannot setup tables.")
            return

        queries = [
            """
            CREATE TABLE IF NOT EXISTS Users (
                id TEXT PRIMARY KEY,
                data BLOB
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Items (
                id TEXT PRIMARY KEY,
                data BLOB
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Transactions (
                id TEXT PRIMARY KEY,
                data BLOB
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Fines (
                id TEXT PRIMARY KEY,
                data BLOB
            )
            """
        ]
        
        try:
            for query in queries:
                self.cursor.execute(query)
            self.conn.commit()
            print("Database tables ensured to be present.")
        except sqlite3.Error as e:
            print(f"Error setting up tables: {e}")
            
    
    def save_data(self, data_list, data_type):
        table_name = data_type + 's'
        if not self.conn:
            print("Cannot save: No database connection.")
            return False

        try:
            for obj in data_list:
                obj_id = getattr(obj, 'user_id', None) or \
                         getattr(obj, 'item_id', None) or \
                         getattr(obj, 'transaction_id', None) or \
                         getattr(obj, 'fine_id', None)
                
                if not obj_id:
                    print(f"Object {obj.__class__.__name__} is missing a required ID.")
                    continue
                    
                serialized_data = pickle.dumps(obj)
                
                self.cursor.execute(
                    f"INSERT OR REPLACE INTO {table_name} (id, data) VALUES (?, ?)", 
                    (obj_id, serialized_data)
                )
            
            self.conn.commit()
            print(f"Saved {len(data_list)} {data_type}(s) successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error while saving data: {e}")
            return False

    def load_data(self, data_type):
        table_name = data_type + 's'
        loaded_objects = []
        if not self.conn:
            print("Cannot load: No database connection.")
            return loaded_objects

        try:
            self.cursor.execute(f"SELECT data FROM {table_name}")
            rows = self.cursor.fetchall()
            
            for row in rows:
                obj = pickle.loads(row[0])
                loaded_objects.append(obj)
            
            print(f"Loaded {len(loaded_objects)} {data_type}(s) from database.")
            return loaded_objects
        except sqlite3.Error as e:
            print(f"Error while loading data from {table_name}: {e}")
            return []
        except pickle.UnpicklingError:
            print("Error during data retrieval, invalid object data.")
            return []
            
    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")