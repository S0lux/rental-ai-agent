import psycopg
import os

class PostgresqlConnector:
    def __init__(self, db_host=None, db_name=None, db_user=None, db_password=None, db_port=None):
        """
        Initializes the connector with database connection parameters.
        Parameters can be passed directly or will be fetched from environment variables if None.
        """
        self.db_host = db_host or os.getenv("POSTGRES_HOST") or "localhost"
        self.db_name = db_name or os.getenv("POSTGRES_DB") or "rental_db"
        self.db_user = db_user or os.getenv("POSTGRES_USER") or "rental_db_user"
        self.db_password = db_password or os.getenv("POSTGRES_PASSWORD") or "rental_db_password"
        self.db_port = db_port or os.getenv("POSTGRES_PORT") or "5432"
        self.connection = None
        self.cursor = None

        if not self.db_name or not self.db_user or not self.db_password:
            raise ValueError("Database name, user, and password must be provided or set as environment variables (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)")

    def connect(self):
        """
        Establishes a connection to the PostgreSQL database.
        """
        if self.connection and not self.connection.closed:
            print("Already connected.")
            return
        try:
            conn_string = f"host='{self.db_host}' dbname='{self.db_name}' user='{self.db_user}' password='{self.db_password}' port='{self.db_port}'"
            self.connection = psycopg.connect(conn_string)
            self.cursor = self.connection.cursor()
            print("Successfully connected to the PostgreSQL database.")
        except psycopg.Error as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            self.connection = None
            self.cursor = None
            raise

    def disconnect(self):
        """
        Closes the database connection.
        """
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
            print("Disconnected from the PostgreSQL database.")
        else:
            print("No active connection to disconnect.")

    def execute_query(self, query, params=None):
        """
        Executes a given SQL query.
        :param query: SQL query string.
        :param params: Optional tuple or dictionary of parameters for the query.
        :return: The cursor object after execution.
        """
        if not self.connection or self.connection.closed:
            print("Not connected to the database. Call connect() first.")
            self.connect() # Attempt to reconnect

        if not self.connection or self.connection.closed: # Check again after trying to connect
             raise ConnectionError("Failed to establish a database connection.")


        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor
        except psycopg.Error as e:
            print(f"Error executing query: {e}")
            if self.connection: # Attempt to rollback on error
                self.connection.rollback()
            raise

    def fetch_one(self):
        """
        Fetches the next row of a query result set.
        :return: A single row from the query result, or None if no more rows are available.
        """
        if self.cursor:
            return self.cursor.fetchone()
        print("No active cursor to fetch from.")
        return None

    def fetch_all(self):
        """
        Fetches all (remaining) rows of a query result set.
        :return: A list of rows from the query result.
        """
        if self.cursor:
            return self.cursor.fetchall()
        print("No active cursor to fetch from.")
        return []

    def __enter__(self):
        """
        Context management protocol. Connects to the database.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context management protocol. Disconnects from the database.
        """
        self.disconnect()
