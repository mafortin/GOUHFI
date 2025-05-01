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
# This file is based from the nnUNet v2 framework (https://github.com/MIC-DKFZ/nnUNet)
# under the terms of the Apache License, Version 2.0.
#---------------------------------------------------------------------------------#
import argparse
import subprocess
import os
import time


def run_inference(dataset_id, input_dir, output_dir, config, trainer, plan, folds, num_pr):
    start_time = time.time()
    # Command for inference
    inference_command = [
                            "nnUNetv2_predict",
                            "-d", dataset_id,
                            "-i", input_dir,
                            "-o", output_dir,
                            "-tr", trainer,
                            "-c", config,
                            "-p", plan,
                            "-f"
                        ] + folds + [
                            "-chk", "checkpoint_best.pth",
                            "-npp", str(num_pr),
                            "-nps", str(num_pr)
                        ]
    print(f"Running inference with the following command: {' '.join(inference_command)}")
    subprocess.run(inference_command)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Inference completed in {duration:.2f} seconds.")
    return duration


def apply_post_processing(input_dir, output_dir, pp_pkl_file, np, plans_json):
    start_time = time.time()
    # Command for applying post processing
    post_processing_command = [
        "nnUNetv2_apply_postprocessing",
        "-i", input_dir,
        "-o", output_dir,
        "-pp_pkl_file", pp_pkl_file,
        "-np", str(np),
        "-plans_json", plans_json
    ]
    print(f"Applying post-processing with the following command: {' '.join(post_processing_command)}")
    subprocess.run(post_processing_command)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Post-processing completed in {duration:.2f} seconds.")
    return duration


def apply_reordering(input_dir, output_dir, in_lut, out_lut):
    start_time = time.time()
    # Command for reordering labels
    reorder_command = [
        "run_labels_reordering",
        "--input_dir", input_dir,
        "--output_dir", output_dir,
        "--old_labels_file", in_lut,
        "--new_labels_file", out_lut
    ]
    print(f"Reordering labels with the following command: {' '.join(reorder_command)}")
    subprocess.run(reorder_command)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Label reordering completed in {duration:.2f} seconds.")
    return duration

def run_all(dataset_id='014', 
            input_dir=os.getcwd(), 
            output_dir=os.getcwd(), 
            config="3d_fullres", 
            trainer="nnUNetTrainer_NoDA_500epochs_AdamW", 
            plan="nnUNetResEncL", 
            np=8, 
            folds="0 1 2 3 4", 
            reorder_labels=False,
            in_lut="/home/marcantf/Code/GOUHFI/misc/gouhfi-label-list-lut.txt",
            out_lut="/home/marcantf/Code/GOUHFI/misc/freesurfer-label-list-lut.txt"):

    # Fetch the GOUHFI_HOME environment variable
    gouhfi_home = os.getenv('GOUHFI_HOME')
    if gouhfi_home is None:
        print("Error: GOUHFI_HOME is not set. Please set the GOUHFI_HOME environment variable as explained in the installation steps.")
        exit(1)

    # Convert folds argument to a list of strings 
    folds_list = folds.split()
    # Construct paths
    input_dir = input_dir.rstrip('/')
    base_dir = os.path.dirname(input_dir)
    output_dir = os.path.join(base_dir, "outputs")
    output_pp_dir = os.path.join(base_dir, "outputs_postprocessed")
    pp_dir = os.path.join(gouhfi_home, "trained_model/Dataset014_gouhfi/nnUNetTrainer_NoDA_500epochs_AdamW__nnUNetResEncL__3d_fullres/crossval_results_folds_0_1_2_3_4")
    pp_pkl_file = os.path.join(pp_dir, "postprocessing.pkl")
    plans_dir = os.path.join(gouhfi_home, "trained_model/Dataset014_gouhfi/nnUNetTrainer_NoDA_500epochs_AdamW__nnUNetResEncL__3d_fullres")
    plans_json_file = os.path.join(plans_dir, "plans.json")
    output_pp_reo_dir = os.path.join(base_dir, "outputs_postprocessed_reordered")


    # Run inference
    inference_duration = run_inference(dataset_id, input_dir, output_dir, config, trainer, plan, folds_list, np)

    # Apply post-processing
    post_processing_duration = apply_post_processing(output_dir, output_pp_dir, pp_pkl_file, np, plans_json_file)

    # Reorder label maps to Freesurfer's lookuptable
    if reorder_labels:
        print("Reordering label maps to Freesurfer's lookuptable...")
        reordering_duration = apply_reordering(input_dir=output_pp_dir, output_dir=output_pp_reo_dir, in_lut=in_lut, out_lut=out_lut)



def main():

    parser = argparse.ArgumentParser(description="Run nnUNet_v2 inference and post-processing.")
    parser.add_argument("-i", "--input_dir", required=True, help="Directory containing input data.")
    parser.add_argument("-o", "--output_dir", help="Directory to save output data.")
    parser.add_argument("--np", type=int, default=8, help="Number of CPU processes to run post-processing in parallel. Depends on your CPU.")
    parser.add_argument("--folds", default="0 1 2 3 4", help="Folds to use for inference. By default all folds are used and combined together.")
    parser.add_argument("--reorder_labels", action="store_true", help="Set flag if you want to reorder the label values from GOUHFI's values to the FreeSurfer lookuptable after post-processing.")

    # Parse arguments
    args = parser.parse_args()

    run_all(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        np=args.np,
        folds=args.folds,
        reorder_labels=args.reorder_labels
    )


if __name__ == "__main__":
    main()