import os
import socket
import sys
import time

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


def test_mysql_connection():
    """Test MySQL connection with detailed error reporting"""
    
    # Load environment variables
    load_dotenv()
    
    # Connection parameters from environment variables
    config = {
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD')
    }
    
    # Check if all required environment variables are set
    required_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("\nError: Missing required environment variables:")
        for var in missing_vars:
            print(f"❌ {var} is not set")
        return
    
    # First, test if the port is reachable
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        result = sock.connect_ex((config['host'], config['port']))
        if result != 0:
            print(f"\nPort connectivity test failed:")
            print(f"❌ Cannot reach port {config['port']} on host {config['host']}")
            print("This might indicate a firewall issue or the server is not accepting connections on this port")
            return
        print(f"\nPort connectivity test passed:")
        print(f"✅ Port {config['port']} is reachable on host {config['host']}")
    except socket.error as e:
        print(f"\nNetwork error during port test: {str(e)}")
        return
    finally:
        sock.close()

    # Now test MySQL connection
    print("\nAttempting MySQL connection...")
    start_time = time.time()
    
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            row = cursor.fetchone()
            connect_time = time.time() - start_time
            
            print("\nConnection successful!")
            print(f"✅ MySQL Server version: {db_info}")
            print(f"✅ Current database: {row[0]}")
            print(f"✅ Connection time: {connect_time:.2f} seconds")
            
            # Test a simple query
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            print("\nAccessible databases:")
            for db in databases:
                print(f"- {db[0]}")

    except Error as err:
        print("\nError: Connection failed!")
        print("\nError details:")
        print(f"❌ Error code: {err.errno if hasattr(err, 'errno') else 'N/A'}")
        print(f"❌ Error message: {str(err)}")
        
        # Provide more specific error guidance
        if hasattr(err, 'errno'):
            if err.errno == 2003:
                print("\nPossible causes:")
                print("- Server is down or unreachable")
                print("- Firewall is blocking the connection")
                print("- Wrong host or port")
            elif err.errno == 1045:
                print("\nPossible causes:")
                print("- Invalid username or password")
                print("- User doesn't have permission to connect from this host")
            elif err.errno == 1049:
                print("\nPossible causes:")
                print("- Database does not exist")
                print("- User doesn't have access to the database")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection is closed")

if __name__ == "__main__":
    print("MySQL Connection Test Script")
    print("=" * 50)
    test_mysql_connection()
