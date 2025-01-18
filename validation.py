# validation.py
import json
import os

class Validation:
    def __init__(self, data, file_name):
        self.data = data
        self.file_name = file_name

    def validate_prices(self):
        for product in self.data:
            if product.get('price', 0) < 0:
                raise ValueError(f"Invalid price for product: {product['title']} in file {self.file_name}")

    def validate_mandatory_fields(self):
        for product in self.data:
            if not all(key in product for key in ['title', 'product_id', 'model_id', 'image']):
                raise ValueError(f"Mandatory fields missing in product: {product} in file {self.file_name}")

    def validate(self):
        self.validate_prices()
        self.validate_mandatory_fields()
        print(f"All validations passed for file: {self.file_name}")

if __name__ == "__main__":
    # Directory containing JSON files
    directory = "output"

    # List of JSON files to validate
    files = ['foreignfortune.json', 'lechocolat.json', 'traderjoes.json']

    for file_name in files:
        file_path = os.path.join(directory, file_name)
        try:
            # Load JSON data
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Validate data
            validator = Validation(data, file_name)
            validator.validate()
        
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {file_path}")
        except ValueError as e:
            print(e)
        except Exception as e:
            print(f"An unexpected error occurred for file {file_name}: {e}")
