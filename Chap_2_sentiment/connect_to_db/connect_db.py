import pyodbc as odbc

def connect_to_db():
    DRIVER_NAME = "SQL SERVER"
    SERVER_NAME = "DESKTOP-A4J24U3\DUNG"     #DESKTOP-A4J24U3\DUNG
    DATABASE_NAME = "banking_solution_version_1"

    connection_string = f"""
        DRIVER={DRIVER_NAME};
        SERVER={SERVER_NAME};
        DATABASE={DATABASE_NAME};
        Trusted_Connection=Yes;
        charset=UTF8
    """

    conn = odbc.connect(connection_string)
    return conn