#!/usr/bin/env python3
#----------------------------------------------------------------------------------# 
# Copyright 2025 [Marc-Antoine Fortin, MR Physics, NTNU]
# Licensed under the Apache License, Version 2.0
#----------------------------------------------------------------------------------#

import argparse
import os
from data_utils import conform_images
from data_utils import brain_extraction_antspynet

def run_preprocessing(args):
    input_dir = args.input_dir
    conform_output_dir = os.path.join(os.path.dirname(input_dir), os.path.basename(input_dir) + "_cfm")
    brain_output_dir = args.output_dir or os.path.join(os.path.dirname(input_dir), os.path.basename(input_dir) + "_preproc")

    print("\n=== Step 1: Conforming images ===")
    conform_args = argparse.Namespace(
        input_dir=input_dir,
        output_dir=conform_output_dir,
        orientation=args.orientation,
        min=args.min,
        max=args.max,
        pmin=args.pmin,
        pmax=args.pmax
    )
    conform_images.main(conform_args)

    # Always keep conforming results, no deletion here

    print("\n=== Step 2: Brain Extraction ===")
    brain_args = argparse.Namespace(
        input_dir=conform_output_dir,
        output_dir=brain_output_dir,
        modality=args.modality,
        skip_morpho=args.skip_morpho,
        mask_folder=args.mask_folder,
        dilation_voxels=args.dilation_voxels,
        rename=args.rename
    )
    brain_extraction_antspynet.main(brain_args)

def main():
    parser = argparse.ArgumentParser(description="Run full preprocessing: conforming + brain extraction")

    parser.add_argument("-i", "--input_dir", type=str, required=True, help="Path to raw input images")
    parser.add_argument("-o", "--output_dir", type=str, help="Optional: path to save brain-extracted images (default: input_dir + _preproc)")
    parser.add_argument("--mask_folder", type=str, help="Optional: path to mask folder for brain extraction")

    # Brain extraction options
    parser.add_argument("--modality", type=str, default="t1", help="Modality for brain extraction (default: t1)")
    parser.add_argument("--skip_morpho", action="store_true", default=True, help="Skip morphological operations (default: True)")
    parser.add_argument("--dilation_voxels", type=int, default=0, help="Dilation radius in voxels (default: 0)")
    parser.add_argument("--rename", action="store_true", help="Rename brain-extracted files with '_masked' suffix")

    # Conforming options
    parser.add_argument("--orientation", type=str, default="LIA", help="Orientation (default: LIA)")
    parser.add_argument("--min", type=float, default=0, help="Rescale output minimum (default: 0)")
    parser.add_argument("--max", type=float, default=255, help="Rescale output maximum (default: 255)")
    parser.add_argument("--pmin", type=float, default=0.5, help="Lower percentile (default: 0.5)")
    parser.add_argument("--pmax", type=float, default=99.5, help="Upper percentile (default: 99.5)")

    args = parser.parse_args()
    run_preprocessing(args)

if __name__ == "__main__":
    main()
