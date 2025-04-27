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
import glob
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


def run_inference_postproc(dataset_id, input_dir, config="3d_fullres", trainer="nnUNetTrainer_NoDA_500epochs_AdamW", plan="nnUNetResEncL", np=8, folds="0 1 2 3 4"):
    
    # Convert folds argument to a list of strings
    folds_list = folds.split()

    # Fetch the GOUHFI_HOME environment variable
    gouhfi_home = os.getenv('GOUHFI_HOME')
    if gouhfi_home is None:
        print("Error: GOUHFI_HOME is not set. Please set the GOUHFI_HOME environment variable as explained in the installation steps.")
        exit(1)

    # Construct paths
    input_dir = input_dir.rstrip('/')
    base_dir = os.path.dirname(input_dir)
    output_dir = os.path.join(base_dir, "outputs")
    output_pp_dir = os.path.join(base_dir, "outputs_postprocessed")
    results_dir = os.path.join(gouhfi_home, "trained_model/Dataset014_gouhfi/nnUNetTrainer_NoDA_500epochs_AdamW__nnUNetResEncL__3d_fullres/crossval_results_folds_0_1_2_3_4")
    pp_pkl_file = os.path.join(results_dir, "postprocessing.pkl")
    plans_json = os.path.join(results_dir, "plans.json")

    # Run inference
    inference_duration = run_inference(dataset_id, input_dir, output_dir, config, trainer, plan, folds_list, np)

    # Apply post-processing
    post_processing_duration = apply_post_processing(output_dir, output_pp_dir, pp_pkl_file, np, plans_json)

    print(f"Total duration for inference and post-processing: {inference_duration + post_processing_duration:.2f} seconds.")


def main():

    parser = argparse.ArgumentParser(description="Run nnUNet_v2 inference and post-processing.")
    parser.add_argument("--dataset_id", required=True, help="Dataset ID in the format DatasetXXX_YYYY.")
    parser.add_argument("-i", "--input_dir", required=True, help="Directory containing input data.")
    parser.add_argument("--config", default="3d_fullres", help="Configuration to use for inference.")
    parser.add_argument("--trainer", default="nnUNetTrainer_NoDA_500epochs_AdamW", help="Trainer to use for inference.")
    parser.add_argument("--plan", default="nnUNetResEncL", help="Plan to use for inference.")
    parser.add_argument("--np", type=int, default=8, help="Number of processes for post-processing. Depends on your CPU.")
    parser.add_argument("--folds", default="0 1 2 3 4", help="Folds to use for inference. By default all folds are used and combined together.")

    # Parse arguments
    args = parser.parse_args()

    run_inference_postproc(
        dataset_id=args.dataset_id,
        input_dir=args.input_dir,
        config=args.config,
        trainer=args.trainer,
        plan=args.plan,
        np=args.np,
        folds=args.folds
    )


if __name__ == "__main__":
    main()