import sqlite3
from contextlib import contextmanager

class Pdb:
    def __init__(self, db_name: str):
        """Initialize the database connection."""
        self.db_name = db_name

    @contextmanager
    def connect(self):
        """Context manager for database connection."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def create_table(self, table_name: str, columns: dict):
        """Create a table with given columns."""
        columns_with_types = ", ".join([f"{col} {col_type}" for col, col_type in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"
        with self.connect() as cursor:
            cursor.execute(query)

    def insert(self, table_name: str, data: dict):
        """Insert data into a table."""
        if not data:
            raise ValueError("Data dictionary cannot be empty.")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        with self.connect() as cursor:
            cursor.execute(query, values)



    def select(self, table_name: str, columns: list = None, query: dict = None):
        """Retrieve data from a table and return it as a list of dictionaries."""
        try:
            columns_str = ', '.join(columns) if columns else '*'
            query_str = ""
            
            if query:
                # Construct the WHERE clause from the query dictionary
                conditions = []
                for key, value in query.items():
                    conditions.append(f"{key} = ?")
                query_str = " WHERE " + " AND ".join(conditions)
            
            # Construct the final SQL query
            sql_query = f"SELECT {columns_str} FROM {table_name}{query_str}"
            
            with self.connect() as cursor:
                cursor.execute(sql_query, tuple(query.values()) if query else ())
                rows = cursor.fetchall()
                
                # Convert rows to a list of dictionaries if columns are specified
                if columns:
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
            
            return result
        except Exception as e:
            print(f"An error occurred in select method: {e}")
            return []  # Return an empty list in case of any error



    def update(self, table_name: str, updates: dict, conditions: dict = None):
        """Update data in a table based on conditions.
        
        Args:
            table_name (str): The name of the table to update.
            updates (dict): A dictionary of columns and their new values.
            conditions (dict): A dictionary of conditions to filter which rows to update.
            
        Example:
            db.update('users', {'age': 35}, {'name': 'John Doe'})
        """
        # Prepare the SET part of the query
        set_clause = ', '.join([f"{col} = ?" for col in updates.keys()])
        values = list(updates.values())
        
        # Prepare the WHERE part of the query if conditions are provided
        where_clause = ""
        if conditions:
            condition_clauses = [f"{col} = ?" for col in conditions.keys()]
            where_clause = " WHERE " + " AND ".join(condition_clauses)
            values.extend(conditions.values())
        
        # Construct the final SQL query
        query = f"UPDATE {table_name} SET {set_clause}{where_clause}"
        
        # Execute the query
        with self.connect() as cursor:
            cursor.execute(query, tuple(values))


    def delete(self, table_name: str, conditions: str = ""):
        """Delete data from a table."""
        query = f"DELETE FROM {table_name} {conditions}"
        with self.connect() as cursor:
            cursor.execute(query)

    def drop_table(self, table_name: str):
        """Drop a table."""
        query = f"DROP TABLE IF EXISTS {table_name}"
        with self.connect() as cursor:
            cursor.execute(query)
