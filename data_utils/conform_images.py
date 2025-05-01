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
# This file is based from FastSurfer (https://github.com/Deep-MI/FastSurfer)
# under the terms of the Apache License, Version 2.0.
#---------------------------------------------------------------------------------#

import os
import argparse
import subprocess

def conform_images(input_dir, output_dir, order, dtype, seg_input):

    # Ensure output directory exists
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.join(os.path.dirname(input_dir), 'inputs-cfm')
        os.makedirs(output_dir, exist_ok=True)

    # Iterate over all files in the input directory
    for filename in sorted(os.listdir(input_dir)):

        if filename.endswith(".nii") or filename.endswith(".nii.gz"):
            
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            # Construct the command
            conform_module = "data_utils.fastsurfer.conform"
            command = [
                "python3", "-m", conform_module,
                "-i", input_path,
                "-o", output_path,
                "--conform_min",
                "--order", str(order),
                "--dtype", dtype
            ]

            # Add the --seg_input flag if specified
            if seg_input:
                command.append("--seg_input")

            # Run the command
            subprocess.run(command, check=True)
            print("--------------------------------------------------------------")


def main():

    parser = argparse.ArgumentParser(description="Conform NIfTI images in a directory.")
    parser.add_argument("-i", "--input_dir", required=True, help="Path to the input directory containing NIfTI images.")
    parser.add_argument("-o", "--output_dir",
                        help="Path to the output directory to save conformed images. If not provided, input files will be overwritten.")
    parser.add_argument("--order", type=int, default=3, help="Order of interpolation to use (default: 3).")
    parser.add_argument("--dtype", type=str, default="float32",
                        help="Data type to use for the conformed images (default: float32. Other options: uint8, int16, int32).")
    parser.add_argument("--seg_input", action='store_true',
                        help="Indicate that the image to be conformed is a label map and nearest neighbor interpolation will be used instead of linear interpolation or spline.")

    args = parser.parse_args()
    
    conform_images(args.input_dir, args.output_dir, args.order, args.dtype, args.seg_input)

if __name__ == "__main__":
    main()
