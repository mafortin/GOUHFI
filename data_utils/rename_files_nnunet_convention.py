import os
import json
import argparse

def extract_sub_id(filename, start_substring=None, end_substring=None):
    base = os.path.splitext(os.path.splitext(filename)[0])[0]  # Remove .nii.gz or .nii
    if not start_substring and not end_substring:
        return base
    start = base.find(start_substring) if start_substring else 0
    if start == -1:
        return None
    start += len(start_substring)
    end = base.find(end_substring, start) if end_substring else len(base)
    if end == -1:
        return None
    return base[start:end]

def rename_files_in_subfolder(input_dir, output_folder=None, start_substring=None, end_substring=None, segms=False):
    if output_folder is None:
        output_folder = input_dir
    os.makedirs(output_folder, exist_ok=True)

    json_file_path = os.path.join(input_dir, 'file_correspondence.json')
    rename_mapping = {}

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as jsonfile:
            rename_mapping = json.load(jsonfile)

    for file_name in os.listdir(input_dir):
        if not file_name.endswith(('.nii.gz', '.nii')):
            continue
        old_file_path = os.path.join(input_dir, file_name)
        old_id = extract_sub_id(file_name, start_substring, end_substring)
        if old_id is None:
            continue
        if old_id in rename_mapping:
            new_id = rename_mapping[old_id]
        else:
            new_id = f"{old_id}" if segms else f"{old_id}_0000"
            rename_mapping[old_id] = new_id

        new_file_name = f"{new_id}.nii.gz"
        new_file_path = os.path.join(output_folder, new_file_name)
        os.rename(old_file_path, new_file_path)

    with open(json_file_path, 'w') as jsonfile:
        json.dump(rename_mapping, jsonfile, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Rename files and store correspondence in a JSON file.')
    parser.add_argument('-i', '--input_dir', required=True, help='Input folder containing files to rename')
    parser.add_argument('-o', '--output_dir', help='Optional output folder to save renamed files')
    parser.add_argument('--start_substring', type=str, help='Start substring to extract sub_id')
    parser.add_argument('--end_substring', type=str, help='End substring to extract sub_id')
    parser.add_argument('--segms', action='store_true', help='Flag for label maps (omit _0000 in filename)')
    args = parser.parse_args()

    rename_files_in_subfolder(
        input_dir=args.input_dir,
        output_folder=args.output_dir,
        start_substring=args.start_substring,
        end_substring=args.end_substring,
        segms=args.segms
    )

if __name__ == "__main__":
    main()
