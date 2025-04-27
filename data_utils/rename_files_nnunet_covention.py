import os
import csv
import argparse

def extract_sub_id(filename, start_substring='sub', end_substring='_'):
    start = filename.find(start_substring)
    if start == -1:
        return None
    start += len(start_substring)  # Move start to the end of the start_substring
    end = filename.find(end_substring, start)
    if end == -1:
        return None
    return filename[start:end]

def rename_files_in_subfolder(subfolder, output_folder=None, start_substring='sub', end_substring='_', segs=False):
    # If output folder is not provided, use the same as the input folder
    if output_folder is None:
        output_folder = subfolder

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Determine the path for the CSV file in the parent directory of the input folder
    parent_dir = os.path.abspath(os.path.join(subfolder, os.pardir))
    csv_file_path = os.path.join(parent_dir, 'file_correspondence.csv')

    # Check if the CSV file already exists
    if os.path.exists(csv_file_path):
        # Read the existing CSV file
        with open(csv_file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Skip the header
            rename_mapping = {rows[0]: rows[1] for rows in csvreader}
    else:
        rename_mapping = {}
        # Initialize the CSV file to save the correspondence
        with open(csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Old ID', 'New ID'])

    # Iterate over each file in the subfolder
    for i, file_name in enumerate(os.listdir(subfolder)):
        old_file_path = os.path.join(subfolder, file_name)
        old_id = extract_sub_id(file_name, start_substring, end_substring)
        if old_id is None:
            continue
        if old_id in rename_mapping:
            new_id = rename_mapping[old_id]
        else:
            new_id = f"image_{i:04d}" if segs else f"image_{i:04d}_0000"
            rename_mapping[old_id] = new_id
            with open(csv_file_path, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([old_id, new_id])
        new_file_name = f"{new_id}.nii.gz"
        new_file_path = os.path.join(output_folder, new_file_name)

        # Rename the file by moving it to the output folder with the new name
        os.rename(old_file_path, new_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rename files in a subfolder and save the correspondence to a CSV file.')
    parser.add_argument('--input_folder', type=str, help='Path to the subfolder containing files to rename', required=True)
    parser.add_argument('--output_folder', type=str, help='Path to the output folder to save the renamed files and CSV file')
    parser.add_argument('--start_substring', type=str, default='sub', help='Substring to start extracting the sub_id')
    parser.add_argument('--end_substring', type=str, default='_', help='Substring to end extracting the sub_id')
    parser.add_argument('--segs', action='store_true', help='Flag indicating that the files to rename are label maps and should not have the _0000 suffix')
    args = parser.parse_args()

    rename_files_in_subfolder(args.input_folder, args.output_folder, args.start_substring, args.end_substring, args.segs)