#!/usr/bin/env python3
#----------------------------------------------------------------------------------# 
# Copyright 2025 [Marc-Antoine Fortin, MR Physics, NTNU]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#---------------------------------------------------------------------------------#


import os
import argparse
import nibabel as nib
import numpy as np

def load_labels(label_file):
    """Reads a label text file and returns a dictionary mapping label IDs to label names."""
    labels = {}
    with open(label_file, 'r') as f:
        for line in f:
            # Skip lines that are comments or empty
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            label_id = int(parts[0])
            label_name = " ".join(parts[1:-3])  # Everything except the first part (ID) and RGB values
            labels[label_id] = label_name
    return labels

def create_mapping(old_labels, new_labels):
    """Create a dictionary mapping old label IDs to new label IDs based on label names."""
    mapping = {}
    for old_id, old_name in old_labels.items():
        # Find the corresponding new label ID based on name matching
        for new_id, new_name in new_labels.items():
            if old_name == new_name:
                mapping[old_id] = new_id
                break
    return mapping

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
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the old and new labels from the respective files
    old_labels = load_labels(old_labels_file)
    new_labels = load_labels(new_labels_file)

    # Create the mapping based on the label names
    mapping = create_mapping(old_labels, new_labels)

    # Process each .nii.gz file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.nii.gz'):
            file_path = os.path.join(input_dir, filename)
            process_label_map(file_path, output_dir, mapping)

def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Process and rename label maps in a directory.")
    parser.add_argument('-i','--input_dir', type=str, required=True,
                        help="Path to the input directory containing label maps.")
    parser.add_argument('-o','--output_dir', type=str, required=False,
                        help="Path to the output directory to save processed label maps.")
    parser.add_argument('--old_labels_file', type=str, required=True, default=None,
                        help="Path to the text file containing GOUHFI's label definitions (label IDs and names).")
    parser.add_argument('--new_labels_file', type=str, required=True, default=None,
                        help="Path to the text file containing FreeSurfer/new label definitions (label IDs and names).")
    args = parser.parse_args()

    # Derive output_dir from input_dir if it is not provided
    if not args.output_dir:
        args.output_dir = args.input_dir + "-freesurfer-labels"

    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Old labels file: {args.old_labels_file}")
    print(f"New labels file: {args.new_labels_file}")

    process_directory(args.input_dir, args.output_dir, args.old_labels_file, args.new_labels_file)
    print("Done reordering label values.")

if __name__ == "__main__":
    main()
