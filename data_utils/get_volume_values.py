#!/usr/bin/env python3

import os
import argparse
import nibabel as nib
import numpy as np
import pandas as pd
import glob

def load_label_mapping(label_file):
    label_map = {}
    with open(label_file, 'r') as f:
        for line in f:
            if line.strip() == "" or line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                label_id = int(parts[0])
                label_name = parts[1]
                label_map[label_id] = label_name
    return label_map

def compute_volumes(nifti_file, label_map, voxel_volume):
    img = nib.load(nifti_file)
    data = img.get_fdata()
    unique_labels = np.unique(data).astype(int)

    volumes = []
    TIV_vox = np.count_nonzero(data)
    CSF_vox = np.sum(data == 16)
    BV_vox = TIV_vox - CSF_vox

    for label in unique_labels:
        if label == 0:
            continue  # skip background
        label_vox = np.sum(data == label)
        abs_vol = label_vox * voxel_volume
        norm_tiv = abs_vol / (TIV_vox * voxel_volume) if TIV_vox > 0 else 0
        norm_bv = abs_vol / (BV_vox * voxel_volume) if BV_vox > 0 else 0
        volumes.append({
            "File": os.path.basename(nifti_file),
            "Label_ID": label,
            "Label_Name": label_map.get(label, f"Label_{label}"),
            "Absolute_Volume_mm3": abs_vol,
            "Normalized_Volume_TIV": norm_tiv,
            "Normalized_Volume_BV": norm_bv
        })

    # Add TIV and BV entries
    volumes.append({
        "File": os.path.basename(nifti_file),
        "Label_ID": -1,
        "Label_Name": "TIV",
        "Absolute_Volume_mm3": TIV_vox * voxel_volume,
        "Normalized_Volume_TIV": 1.0,
        "Normalized_Volume_BV": TIV_vox * voxel_volume / (BV_vox * voxel_volume) if BV_vox > 0 else 0
    })

    volumes.append({
        "File": os.path.basename(nifti_file),
        "Label_ID": -2,
        "Label_Name": "BrainVolume(BV)",
        "Absolute_Volume_mm3": BV_vox * voxel_volume,
        "Normalized_Volume_TIV": BV_vox * voxel_volume / (TIV_vox * voxel_volume) if TIV_vox > 0 else 0,
        "Normalized_Volume_BV": 1.0
    })

    return volumes

def main():
    parser = argparse.ArgumentParser(description="Volumetry extraction script for .nii.gz label maps")
    parser.add_argument("input_dir", help="Directory containing .nii or .nii.gz label maps")
    parser.add_argument("--output_dir", "-o", help="Directory to save the output CSV (default: same as input_dir)")
    parser.add_argument("--task", "-t", choices=["brain", "cortex"], required=True, help="Task type: 'brain' or 'cortex'")
    parser.add_argument("--label_file", "-l", help="Optional custom label map file (.txt format)")

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir if args.output_dir else input_dir

    default_label_files = {
        "brain": "brain_labels.txt",
        "cortex": "cortex_labels.txt"
    }

    label_file = args.label_file if args.label_file else default_label_files[args.task]

    if not os.path.isfile(label_file):
        print(f"Label file '{label_file}' not found.")
        return

    label_map = load_label_mapping(label_file)
    all_volumes = []

    nii_files = sorted(glob.glob(os.path.join(input_dir, "*.nii*")))
    if not nii_files:
        print("No .nii or .nii.gz files found in the input directory.")
        return

    for nifti_path in nii_files:
        img = nib.load(nifti_path)
        voxel_volume = np.prod(img.header.get_zooms())  # mm³ per voxel
        vols = compute_volumes(nifti_path, label_map, voxel_volume)
        all_volumes.extend(vols)

    df = pd.DataFrame(all_volumes)
    output_csv = os.path.join(output_dir, f"volumetry_{args.task}.csv")
    df.to_csv(output_csv, index=False)
    print(f"✅ Volumetry CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
