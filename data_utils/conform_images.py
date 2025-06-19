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


import nibabel as nib
from nibabel.orientations import axcodes2ornt, io_orientation, ornt_transform, apply_orientation, inv_ornt_aff
import argparse
import os
import sys
import numpy as np
from glob import glob

def reorient_image(img, orientation='LIA'):
    data = img.get_fdata()
    affine = img.affine

    current_ornt = io_orientation(affine)
    target_ornt = axcodes2ornt(tuple(orientation))

    transform = ornt_transform(current_ornt, target_ornt)
    reoriented_data = apply_orientation(data, transform)
    new_affine = affine @ inv_ornt_aff(transform, data.shape)

    return nib.Nifti1Image(reoriented_data, new_affine)

def rescale_intensity(image_data, out_min=0, out_max=255):
    in_min = image_data.min()
    in_max = image_data.max()

    if in_max - in_min == 0:
        return np.full_like(image_data, out_min, dtype=np.float32)

    scaled = (image_data - in_min) / (in_max - in_min)
    scaled = scaled * (out_max - out_min) + out_min
    return scaled.astype(np.float32)

def main():
    parser = argparse.ArgumentParser(
        description="Reorient and rescale all NIfTI images in a directory (default orientation: LIA, intensity range: 0-255)"
    )
    parser.add_argument('-i', '--input-dir', required=True, help='Directory with input NIfTI images')
    parser.add_argument('-o', '--output-dir', required=True, help='Directory to save output images')
    parser.add_argument('-r', '--orientation', default='LIA', help='Target orientation (e.g., LIA, RAS)')
    parser.add_argument('--min', type=float, default=0, help='Rescale output minimum (default: 0)')
    parser.add_argument('--max', type=float, default=255, help='Rescale output maximum (default: 255)')

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    input_files = sorted(glob(os.path.join(args.input_dir, '*.nii')) + glob(os.path.join(args.input_dir, '*.nii.gz')))

    if not input_files:
        print("No NIfTI files found in the input directory.")
        sys.exit(0)

    print(f"Found {len(input_files)} NIfTI images to process in: {args.input_dir}")
    print(f"  Output directory   : {args.output_dir}")
    print(f"  Target orientation : {args.orientation.upper()}")
    print(f"  Output data type   : float32")
    print(f"  Intensity range    : {args.min} to {args.max}\n")

    for input_path in input_files:
        filename = os.path.basename(input_path)
        output_path = os.path.join(args.output_dir, filename)

        original_img = nib.load(input_path)
        reoriented_img = reorient_image(original_img, args.orientation.upper())
        rescaled_data = rescale_intensity(reoriented_img.get_fdata(), args.min, args.max)
        final_img = nib.Nifti1Image(rescaled_data, reoriented_img.affine)
        nib.save(final_img, output_path)

    print(f"Finished processing {len(input_files)} images.")

if __name__ == "__main__":
    main()

