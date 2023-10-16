import json

file_path = "..\\..\\_data\\AusUrbHI HVI data unprocessed\\OSM and HealthDirect\\HealthcareService_combined.txt"

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

        # Try to parse the content as JSON
        parsed_json = json.loads(content)

        print("The file is in JSON format.")


        # Function to print the structure with field names
        def print_structure(data, indent=0):
            if isinstance(data, dict):
                for key, value in data.items():
                    print(' ' * indent + str(key))
                    print_structure(value, indent + 4)
            elif isinstance(data, list) and data:
                print_structure(data[0], indent + 4)


        print_structure(parsed_json)

except json.JSONDecodeError:
    print("The file is not in JSON format.")
except FileNotFoundError:
    print(f"The file {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
