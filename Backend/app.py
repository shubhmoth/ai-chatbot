# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
import pymysql
import os
from flask_cors import CORS
import json
from datetime import datetime,date

# Add this new class for JSON encoding
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()  # Convert date to a string in ISO format
        return super().default(obj)
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Helper function to get related tables and fetch data
def get_related_tables_data(account_id):
    print(f"Entering get_related_tables_data for account_id: {account_id}")
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            db='hk_asset_staging'
        )
        print("Database connection established")
        
        cursor = connection.cursor()
        
        # Query to get tables that have a foreign key to the 'account' table
        foreign_key_query = """
        SELECT table_name, column_name
        FROM information_schema.key_column_usage
        WHERE referenced_table_name = 'account'
        AND referenced_column_name = 'id'
        """
        
        print(f"Executing foreign key query")
        cursor.execute(foreign_key_query)
        related_tables = cursor.fetchall()
        print(f"Found {len(related_tables)} related tables")

        data = {}
        
        # Loop over each related table and fetch the associated data for the account_id
        for table, column in related_tables:
            try:
                print(f"Fetching data from table: {table}")
                
                # Prepare the SQL query
                query = f"SELECT * FROM {table} WHERE {column} = %s"
                
                # Execute the query
                cursor.execute(query, (account_id,))
                
                # Fetch all rows
                rows = cursor.fetchall()
            
                # Log the number of rows found
                print(f"Found {len(rows)} rows in {table}")
                
                # Store the data in a dictionary
                data[table] = [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
            
            except Exception as e:
                print(f"An error occurred while fetching data from {table}: {e}")
        
        print("Finished fetching related data")
        return data
    except Exception as e:
        print(f"Error in get_related_tables_data: {str(e)}")
        raise
    finally:
        cursor.close()
        connection.close()
        print("Database connection closed")

# Helper function to generate a summary and save to a file
def save_summary_to_file(account_id, account_info, related_data):
    print(f"Entering save_summary_to_file for account_id: {account_id}")
    try:
        # Create the accountData folder if it doesn't exist
        folder_path = os.path.join(os.getcwd(), 'accountData')
        os.makedirs(folder_path, exist_ok=True)
        
        file_name = f"{account_id}_data.json"
        file_path = os.path.join(folder_path, file_name)
        
        # Prepare the summary dictionary
        summary = {}

        # Only include non-empty account information
        if account_info:
            non_empty_account_info = {k: v for k, v in account_info.items() if v}
            if non_empty_account_info:
                summary["Account Information"] = non_empty_account_info

        # Only include non-empty related data
        non_empty_related_data = {table: rows for table, rows in related_data.items() if rows}
        if non_empty_related_data:
            summary["Related Data"] = non_empty_related_data

        # If both account info and related data are empty, don't create the file
        if not summary:
            print(f"No data to save for account_id: {account_id}. Skipping file creation.")
            return None
        
        print(f"Writing summary to JSON file: {file_path}")
        # Save the summary as a JSON file using the custom encoder
        with open(file_path, 'w') as f:
            json.dump(summary, f, indent=4, cls=CustomJSONEncoder)
        
        print(f"Summary JSON file created successfully in accountData folder")
        return file_name
    except Exception as e:
        print(f"Error in save_summary_to_file: {str(e)}")
        raise
# API route to fetch account data and related data
@app.route('/fetch-account-data', methods=['POST'])
def fetch_account_data():
    print("Entering fetch_account_data")
    try:
        print("Request Headers:", request.headers)
        print("Request Data:", request.data)  # Print the raw request data
        print("Is JSON?", request.is_json)
        account_id = request.json.get('account_id')
        
        if not account_id:
            print("No account_id provided in request")
            return jsonify({"error": "No account_id provided"}), 400
        
        # Convert account_id to integer
        try:
            account_id = int(account_id)
        except ValueError:
            print(f"Invalid account_id format: {account_id}")
            return jsonify({"error": "Invalid account_id format. Must be a number."}), 400
        
        print(f"Fetching data for account_id: {account_id}")
        
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            db='hk_asset_staging'
        )
        print("Database connection established")
        
        cursor = connection.cursor()
        
        # Check if the account exists
        account_query = "SELECT * FROM account WHERE id = %s"
        print(f"Executing account query: {account_query}")
        cursor.execute(account_query, (account_id,))
        account = cursor.fetchone()

        if not account:
            print(f"Account not found for account_id: {account_id}")
            return jsonify({"error": "Account not found"}), 404

        print("Account found, creating account_info dictionary")
        account_info = {
            "id": account[0],  # Assuming `id` is the first column in the account table
            "name": account[1],  # Assuming `name` is the second column in the account table
            "email": account[2]  # Assuming `email` is the third column in the account table
        }

        print("Fetching data from related tables")
        related_data = get_related_tables_data(account_id)
        
        print("Saving summary to file")
        file_name = save_summary_to_file(account_id, account_info, related_data)
        print("Committing database changes")
        connection.commit()

        print(f"Processing completed for account_id: {account_id}")
        return jsonify({"message": "Account information stored successfully", "file_name": file_name}), 200

    except Exception as e:
        print(f"Error in fetch_account_data: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
    finally:
        cursor.close()
        connection.close()
        print("Database connection closed")

if __name__ == '__main__':
    app.run(debug=True)