import os
import argparse
import nibabel as nib
import numpy as np

def load_mapping(old_labels_file, new_labels_file):
    try:
        # Function to extract label numbers from the text files
        def parse_label_file(file_path):
            labels = []
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:  # Ignore lines with less than 2 parts (header or empty lines)
                        label = int(parts[0])  # First column is the label number
                        labels.append(label)
            return labels

        # Read old and new labels
        old_labels = parse_label_file(old_labels_file)
        new_labels = parse_label_file(new_labels_file)

        # Ensure both files have the same number of labels
        if len(old_labels) != len(new_labels):
            print("Error: The number of old and new labels do not match.")
            raise ValueError("Mismatch in label count between old and new labels.")
        
        # Create the mapping dictionary from old label to new label
        mapping = {old: new for old, new in zip(old_labels, new_labels)}
        return mapping

    except FileNotFoundError as e:
        print(f"Error: File not found. {e}")
        raise
    except ValueError as e:
        print(f"Error: Invalid data. {e}")
        raise

def process_label_map(file_path, output_dir, mapping):
    print(f"Processing file: {file_path}")
    # Load the label map file
    img = nib.load(file_path)
    data = img.get_fdata()

    # Ensure the data is handled as integer
    unique_raw_labels = np.unique(data)
    rounded_int_label_map = np.round(data).astype(np.int32)  # Round first, and then convert to integer

    # Debug: print the shape and data type of the loaded image
    print(f"Loaded {file_path}, shape: {rounded_int_label_map.shape}, dtype: {rounded_int_label_map.dtype}")

    # Map the new labels back to the original labels
    new_data = np.copy(rounded_int_label_map)
    for old_label, new_label in mapping.items():
        print(f"Switching label {old_label} to {new_label}")
        new_data[rounded_int_label_map == old_label] = new_label
    new_data_rd = np.round(new_data).astype(np.int32)

    # Save the modified label map
    new_affine = img.affine
    new_header = img.header
    new_header.set_data_dtype(np.int32)

    # Save the new label map file
    new_img = nib.Nifti1Image(new_data_rd, new_affine, new_header)
    new_file_path = os.path.join(output_dir, os.path.basename(file_path))
    nib.save(new_img, new_file_path)
    print(f"Processed {file_path} -> {new_file_path}")

def process_directory(input_dir, output_dir, old_labels_file, new_labels_file):
    if not os.path.isdir(input_dir):
        print(f"Error: The input directory {input_dir} does not exist.")
        return

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the mapping from the old and new label files
    mapping = load_mapping(old_labels_file, new_labels_file)

    # Process each .nii.gz or .nii file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.nii.gz') or filename.endswith('.nii'):
            file_path = os.path.join(input_dir, filename)
            process_label_map(file_path, output_dir, mapping)
        else:
            print(f"Skipping non-NIfTI file: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Process and rename label maps in a directory.")
    parser.add_argument('--input_dir', type=str, required=True,
                        help="Path to the input directory containing label maps.")
    parser.add_argument('--output_dir', type=str, required=False,
                        help="Path to the output directory to save processed label maps.")
    parser.add_argument('--old_labels_file', type=str, required=True,
                        help="Path to the .txt file containing the old labels.")
    parser.add_argument('--new_labels_file', type=str, required=True,
                        help="Path to the .txt file containing the new labels.")
    args = parser.parse_args()

    # Derive output_dir from input_dir if it is not provided
    if not args.output_dir:
        args.output_dir = args.input_dir + "-fss-order"

    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Old labels file: {args.old_labels_file}")
    print(f"New labels file: {args.new_labels_file}")

    # Process and rename the label maps in the input directory
    process_directory(args.input_dir, args.output_dir, args.old_labels_file, args.new_labels_file)
    print("Done processing label values.")

if __name__ == "__main__":
    main()
