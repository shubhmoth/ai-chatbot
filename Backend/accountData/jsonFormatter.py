# account_converter.py
import json
import re
from datetime import datetime
import os

def convert_account_info_to_json(input_file, output_file):
    # Read the text file
    file_path = os.path.join('accountData', input_file)
    with open(file_path, 'r') as file:
        data = file.read()

    # Extract account information
    account_info_match = re.search(r'Account Information:\nID: (\d+)\nName: (.+?)\nEmail: (.+?)\n', data)
    account_info = {
        "id": int(account_info_match.group(1)),
        "name": account_info_match.group(2).strip(),
        "email": account_info_match.group(3).strip()
    }

    # Extract access mapping data
    access_mapping_matches = re.findall(r'\{.*?\}', data, re.DOTALL)
    account_access_mapping = []
    for match in access_mapping_matches:
        access_data = eval(match)  # Convert the string representation to a dictionary
        access_data['created_date'] = access_data['created_date'].isoformat()
        access_data['last_modified_date'] = access_data['last_modified_date'].isoformat()
        account_access_mapping.append(access_data)

    # Combine everything into a single dictionary
    structured_data = {
        "account_information": account_info,
        "account_access_mapping": account_access_mapping
    }

    # Convert to JSON format
    json_output = json.dumps(structured_data, indent=2)

    # Write to a JSON file
    with open(output_file, 'w') as json_file:
        json_file.write(json_output)

    print(f"Data has been converted to JSON format and saved to {output_file}.")
