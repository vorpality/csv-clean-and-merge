import csv
import re
import os
import sys

def get_script_directory():
    # Determine the script's directory whether running as script or executable
    if getattr(sys, 'frozen', False):  # Running as executable
        return os.path.dirname(sys.executable)
    else:  # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def read_config_file():
    config = {}
    script_dir = get_script_directory()
    config_file_path = os.path.join(script_dir, 'config.txt')

    try:
        with open(config_file_path, 'r') as config_file:
            for line in config_file:
                key, value = line.strip().split('=')
                config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Config file not found at: {config_file_path}")
        sys.exit(1)

    return config

def custom_transliteration(part):
    # Custom mappings for Greek to Latin characters
    greek_to_latin = {'Α': 'A', 'Β': 'B'}

    return ''.join(greek_to_latin.get(char, char) for char in part)

def transform_csv(input_file_path, output_file_path):
    with open(input_file_path, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            # Remove empty cells
            row = [cell.replace(" ", "").replace(".", "") if cell else cell for cell in row]
            
            original_sample_id = row[0]
            modified_sample_id_base = transform_sample_id(original_sample_id)
            trials = row[1:5]

            for i, trial in enumerate(trials, 1):
                trial_number = f"0{trial}" if len(trial) == 5 else trial
                modified_sample_id = f"{modified_sample_id_base}_{i}"
                writer.writerow([modified_sample_id, trial_number])

def transform_sample_id(original_id):
    parts = original_id.split('/')
    if not parts[0].endswith('d'):
        parts[0] += 'd'
    transliterated_parts = [custom_transliteration(part) for part in parts]
    return '_'.join(transliterated_parts)




def create_mapping_from_transformed(transformed_file_path):
    mapping = {}
    with open(transformed_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the part of the filename is in the second column
            part_of_filename = row[1]
            sample_id = row[0]
            mapping[part_of_filename] = sample_id

    return mapping


def extract_part_of_filename(filename):
    match = re.search(r'(\d{6})_', filename)
    if match:
        return match.group(1)
    return None

def match_and_write_new_csv(transformed_mapping, reformed_file_path, output_file_path):
    with open(reformed_file_path, mode='r', newline='', encoding='utf-8') as reformed_file, \
         open(output_file_path, mode='w', newline='', encoding='utf-8') as output_file:

        reformed_reader = csv.reader(reformed_file)
        output_writer = csv.writer(output_file)

        for reformed_row in reformed_reader:
            filename = reformed_row[0]

            # Extract the part of the filename from reformed data
            part_of_filename = extract_part_of_filename(filename)

            matching_sample_id = None
            print(f"{part_of_filename} , from {filename}")
            if part_of_filename:
                # Check if any part of the transformed filename matches
                
                matching_sample_id = next((sample_id for transformed_filename, sample_id in transformed_mapping.items()
                                            if part_of_filename in transformed_filename), None)

            if matching_sample_id:
                # Write the sample ID from transformed data and the rest of the row from reformed data
                output_writer.writerow([matching_sample_id] + reformed_row[1:])



def main():
    config = read_config_file()

    input_file_path = config.get('sample_data', 'normal_data.csv')
    output_file_path = config.get('transformation_file', 'transformed_data.csv')
    reformed_file_path = config.get('file_with_wavelengths', 'reformed.csv')
    final_output_file_path = config.get('final_file', 'final.csv')


    transform_csv(input_file_path, output_file_path)
    print("Transformation complete.")

    transformed_mapping = create_mapping_from_transformed(output_file_path)

    match_and_write_new_csv(transformed_mapping, reformed_file_path, final_output_file_path)
    print("Matching and writing to final CSV complete.")

if __name__ == "__main__":
    main()
