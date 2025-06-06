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
# This file is based on the ANTsPyNet (https://github.com/ANTsX/ANTsPyNet)
# under the terms of the Apache License, Version 2.0.
#---------------------------------------------------------------------------------#

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress INFO, WARNING, and ERROR logs from TensorFlow
import ants
import antspynet
import argparse
import numpy as np
from scipy.ndimage import label
from skimage.morphology import binary_closing, ball, binary_dilation


def brain_extraction(input_folder, output_folder=None, modality="t1", skip_morpho=False, mask_folder=None, dilation_voxels=0, rename=False):
    if output_folder is None:
        output_folder = input_folder

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    if mask_folder:
        # Use existing masks and perform brain extraction
        for mask_filename in os.listdir(mask_folder):
            if mask_filename.endswith(".nii") or mask_filename.endswith(".nii.gz"):
                # Remove 'mask' from the mask filename to find the corresponding image filename
                subject_id = mask_filename.replace('mask', '')
                input_filename = next((f for f in os.listdir(input_folder) if subject_id in f), None)

                if input_filename:
                    input_path = os.path.join(input_folder, input_filename)
                    mask_path = os.path.join(mask_folder, mask_filename)

                    if ".nii.gz" in input_filename:
                        new_output_name = os.path.splitext(os.path.splitext(input_filename)[0])[0] + "_masked.nii.gz"
                        new_mask_name = os.path.splitext(os.path.splitext(mask_filename)[0])[0] + "_mod.nii.gz"
                    else:
                        new_output_name = os.path.splitext(input_filename)[0] + "_masked.nii"
                        new_mask_name = os.path.splitext(mask_filename)[0] + "_mod.nii"

                    output_path = os.path.join(output_folder, new_output_name)
                    mask_output_path = os.path.join(output_folder, new_mask_name)

                    # Load the image
                    image = ants.image_read(input_path)

                    # Load the mask
                    mask = ants.image_read(mask_path)

                    # Threshold the mask to keep values greater than 0.01
                    binary_mask = mask.numpy() > 0.01

                    # Keep only the largest connected component in the mask
                    labeled_mask, num_features = label(binary_mask)
                    sizes = np.bincount(labeled_mask.ravel())
                    sizes[0] = 0  # Ignore background
                    largest_label = sizes.argmax()
                    largest_component_mask = labeled_mask == largest_label

                    # Apply morphological operations on the mask
                    selem = ball(5)  # Use a 3D structuring element
                    closed_mask = binary_closing(largest_component_mask, selem)
                    if dilation_voxels > 0:
                        dilated_mask = binary_dilation(closed_mask, ball(dilation_voxels))
                    else:
                        dilated_mask = closed_mask

                    # Apply the mask to the original image
                    masked_image = image * dilated_mask

                    # Save the modified mask and the brain-extracted and masked image
                    modified_mask = ants.from_numpy(dilated_mask, origin=image.origin, spacing=image.spacing,
                                                    direction=image.direction)
                    ants.image_write(modified_mask, mask_output_path)
                    ants.image_write(masked_image, output_path)
                    print(f"Brain extraction and masking completed for {input_filename}, saved to {output_path}")
                    print(f"Modified mask saved to {mask_output_path}")
                else:
                    print(f"No matching image found for mask {mask_filename}")
    else:
        # Iterate over all files in the input folder
        for filename in os.listdir(input_folder):
            if filename.endswith(".nii") or filename.endswith(".nii.gz"):
                input_path = os.path.join(input_folder, filename)
                input_basename = os.path.basename(input_path)

                if rename:
                    if ".nii.gz" in input_basename:
                        new_output_name = os.path.splitext(os.path.splitext(input_basename)[0])[0] + "_masked.nii.gz"
                    else:
                        new_output_name = os.path.splitext(os.path.splitext(input_basename)[0])[0] + "_masked.nii"
                else:
                    new_output_name = input_basename


                output_path = os.path.join(output_folder, new_output_name)
                new_mask_name = 'mask_' + input_basename
                mask_output_path = os.path.join(output_folder, new_mask_name)

                # Load the image
                image = ants.image_read(input_path)

                # Perform brain extraction to create the initial mask
                initial_mask = antspynet.brain_extraction(image, modality=modality)

                if skip_morpho:
                
                    # Convert the brain-extracted image to a binary mask
                    binary_mask = initial_mask.numpy() > 0.01
                    # Apply the mask to the original image
                    masked_image = image * binary_mask

                    ants.image_write(masked_image, output_path)
                    print(f"Brain extraction completed for {filename}, saved to {output_path}")

                else:
                    # Convert the brain-extracted image to a binary mask
                    binary_mask = initial_mask.numpy() > 0.01

                    # Keep only the largest connected component in the mask
                    labeled_mask, num_features = label(binary_mask)
                    sizes = np.bincount(labeled_mask.ravel())
                    sizes[0] = 0  # Ignore background
                    largest_label = sizes.argmax()
                    largest_component_mask = labeled_mask == largest_label

                    # Apply morphological operations on the mask
                    selem = ball(5)  # Use a 3D structuring element
                    closed_mask = binary_closing(largest_component_mask, selem)
                    if dilation_voxels > 0:
                        dilated_mask = binary_dilation(closed_mask, ball(dilation_voxels))
                    else:
                        dilated_mask = closed_mask

                    # Apply the mask to the original image
                    masked_image = image * dilated_mask

                    # Save the modified mask and the brain-extracted and masked image
                    modified_mask = ants.from_numpy(dilated_mask, origin=image.origin, spacing=image.spacing,
                                                    direction=image.direction)
                    ants.image_write(modified_mask, mask_output_path)
                    ants.image_write(masked_image, output_path)
                    print(f"Brain extraction and masking completed for {filename}, saved to {output_path}")
                    print(f"Mask saved to {mask_output_path}")


    
def main():
    parser = argparse.ArgumentParser(description="Brain Extraction using ANTsPyNet")
    parser.add_argument("-i", "--input_dir", type=str, help="Path to the input folder containing images")
    parser.add_argument("-o", "--output_dir", type=str, default=None,
                        help="Path to the output folder (default: input folder)")
    parser.add_argument("--modality", type=str, default="t1", help="Modality for brain extraction (default: t1)")
    parser.add_argument("--skip_morpho", action="store_true",
                        help="Skip morphological operations and only save the newly brain extracted image(s).")
    parser.add_argument("--mask_folder", type=str,
                        help="Path to the folder containing masks for morphological operations")
    parser.add_argument("--dilation_voxels", type=int, default=0, help="Number of voxels for dilation (default: 0)")
    parser.add_argument("--rename", action="store_true", help="Flag to rename the brain extracted image(s) by adding the '_masked' suffix. Otherwise, brain extracted images will keep the same name.")

    args = parser.parse_args()

    brain_extraction(args.input_dir, args.output_dir, args.modality, args.skip_morpho, args.mask_folder,
                     args.dilation_voxels, args.rename)

if __name__ == "__main__":
    main()