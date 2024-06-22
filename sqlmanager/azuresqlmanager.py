import pyodbc

class AzureSQLManager:

    def __init__(self,server,database,username,password):

        self.server = server
        self.database = database
        self.username = username    
        self.password = password
        self.connection = None
        
    def connect(self):
        try:            
            self.connection = pyodbc.connect(
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                f'Encrypt=yes; \
                TrustServerCertificate=no; \
                Connection Timeout=50;') 
                
            print("Connected to Azure SQL Server successfully!")
        except pyodbc.Error as e:
            print("Error connecting to Azure SQL Server:", e)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from Azure SQL Server")

    def execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except pyodbc.Error as e:
            print("Error executing query:", e)
        finally:
            cursor.close()

    def create(self, table_name, data):
        columns = ', '.join(data.keys())
        values = ', '.join([f"'{value}'" for value in data.values()])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        self.execute_query(query)
        

    def read(self, table_name, condition=None):
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except pyodbc.Error as e:
            print("Error executing query:", e)
        finally:
            cursor.close()

    def update(self, table_name, data, condition):
        set_values = ', '.join([f"{key} = '{value}'" for key, value in data.items()])
        query = f"UPDATE {table_name} SET {set_values} WHERE {condition}"
        self.execute_query(query)

    def delete(self, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.execute_query(query)
    
    def count(self, table_name,condition = ""):
        query = f"SELECT COUNT(*) FROM {table_name}"
        if condition.strip() != "": 
            query += f" WHERE {condition}"  
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"Total rows in {table_name}: {count}")
        except pyodbc.Error as e:
            print("Error executing query:", e)
        finally:
            cursor.close()
        return count
    
    def execute_query_return(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except pyodbc.Error as e:
            print("Error executing query:", e)
        finally:
            cursor.close()

