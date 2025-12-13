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
#----------------------------------------------------------------------------------#
import argparse
import subprocess
import os
import time
from dataclasses import dataclass
from pathlib import Path

#---------------------------------------------------------------------------------#
# Setting up environment variables for nnUNet if not already set
gouhfi_home = os.environ.get("GOUHFI_HOME")
if gouhfi_home is None:
    print("ERROR: GOUHFI_HOME is not set. Please set the GOUHFI_HOME environment variable as explained in the installation steps.")
    raise SystemExit(1)

# Always set GOUHFI-specific nnUNet paths
os.environ["nnUNet_raw"] = os.path.join(gouhfi_home, "nnUNet_raw")  # dummy path (not used in GOUHFI)
os.environ["nnUNet_preprocessed"] = os.path.join(gouhfi_home, "nnUNet_preprocessed")  # dummy path (not used in GOUHFI)
os.environ["nnUNet_results"] = os.path.join(gouhfi_home, "trained_model")  # nnUNet uses this to locate trained models
#---------------------------------------------------------------------------------#


#---------------------------------------------------------------------------------#
# Setting up the three model profiles
@dataclass(frozen=True)
class ModelProfile:
    """Class to hardcode the three models settings."""
    name: str
    dataset_id: str
    trainer: str
    config: str
    plan: str
    dataset_dir_name: str  # folder under trained_model, e.g. Dataset014_gouhfi


# ---- Hardcoded params of the 3 models here ----
MODEL_V1 = ModelProfile(
    name="v1",
    dataset_id="014",
    trainer="nnUNetTrainer_NoDA_500epochs_AdamW",
    config="3d_fullres",
    plan="nnUNetResEncL",
    dataset_dir_name="Dataset014_gouhfi",
)

MODEL_SEG = ModelProfile(
    name="gouhfi_2p0_seg",
    dataset_id="020",  # Dataset020_gouhfi_2p0n2
    trainer="my_nnUNetTrainer_GOUHFI", 
    config="3d_fullres",  
    plan="plans-resencl-gouhfi-2p0n2",  
    dataset_dir_name="Dataset020_gouhfi_2p0n2",
)

MODEL_PARC = ModelProfile(
    name="gouhfi_2p0_parc",
    dataset_id="024",  # Dataset024_gouhfi_parc
    trainer="my_trainer_gouhfi_parc",  
    config="3d_fullres", 
    plan="plans-resencl-3dlin-nonorm",  
    dataset_dir_name="Dataset024_gouhfi_parc",
)
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
# Misc helper functions 
def _postproc_paths(model: ModelProfile) -> tuple[Path, Path]:
    """
    Build pp_pkl_file and plans.json paths for a given model.
    """
    trained_root = Path(gouhfi_home) / "trained_model" / model.dataset_dir_name
    model_subdir = f"{model.trainer}__{model.plan}__{model.config}"

    pp_dir = trained_root / model_subdir / "crossval_results_folds_0_1_2_3_4"
    pp_pkl_file = pp_dir / "postprocessing.pkl"

    plans_dir = trained_root / model_subdir
    plans_json_file = plans_dir / "plans.json"

    return pp_pkl_file, plans_json_file


def _ensure_exists(path: Path, what: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{what} not found: {path}")

def _count_nii_files(dir_path: Path) -> int:
    return sum(1 for p in dir_path.iterdir()
               if p.is_file() and (p.name.endswith(".nii") or p.name.endswith(".nii.gz")))

def _announce_inputs(stage: str, dir_path: Path, require_nonzero: bool = True) -> int:
    if not dir_path.exists():
        raise FileNotFoundError(f"{stage}: input directory does not exist: {dir_path}")
    if not dir_path.is_dir():
        raise NotADirectoryError(f"{stage}: input path is not a directory: {dir_path}")

    n = _count_nii_files(dir_path)
    print(f"{stage}: detected {n} NIfTI file(s) (.nii/.nii.gz) in: {dir_path}")
    if require_nonzero and n == 0:
        raise FileNotFoundError(
            f"{stage}: no .nii/.nii.gz files found in {dir_path}. "
            f"Please verify the input directory."
        )
    return n
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
# Core functions to run inference, post-processing, reordering, and parcellation input prep
def run_inference(model: ModelProfile, input_dir: str, output_dir: Path, folds: list[str], num_pr: int, cpu: bool) -> float:
    start_time = time.time()

    inference_command = [
        "nnUNetv2_predict",
        "-d", model.dataset_id,
        "-i", str(input_dir),
        "-o", str(output_dir),
        "-tr", model.trainer,
        "-c", model.config,
        "-p", model.plan,
        "-f",
    ] + folds + [
        "-chk", "checkpoint_best.pth",
        "-npp", str(num_pr),
        "-nps", str(num_pr),
    ]

    if cpu:
        print("CPU will be used to run the inference. Expect a considerable increase in inference time.")
        inference_command += ["-device", "cpu"]

    print(f"Running inference ({model.name}) with the following command: {' '.join(map(str, inference_command))}")
    subprocess.run(inference_command, check=True)

    duration = time.time() - start_time
    print(f"Inference ({model.name}) completed in {duration:.2f} seconds.")
    return duration


def apply_post_processing(input_dir: Path, output_dir: Path, pp_pkl_file: Path, np: int, plans_json: Path, tag: str) -> float:
    start_time = time.time()

    post_processing_command = [
        "nnUNetv2_apply_postprocessing",
        "-i", str(input_dir),
        "-o", str(output_dir),
        "-pp_pkl_file", str(pp_pkl_file),
        "-np", str(np),
        "-plans_json", str(plans_json),
    ]
    print(f"Applying post-processing ({tag}) with the following command: {' '.join(map(str, post_processing_command))}")
    subprocess.run(post_processing_command, check=True)

    duration = time.time() - start_time
    print(f"Post-processing ({tag}) completed in {duration:.2f} seconds.")
    return duration


def apply_reordering(input_dir: Path, output_dir: Path, in_lut: str, out_lut: str, tag: str) -> float:
    start_time = time.time()

    reorder_command = [
        "run_labels_reordering",
        "--input_dir", str(input_dir),
        "--output_dir", str(output_dir),
        "--old_labels_file", str(in_lut),
        "--new_labels_file", str(out_lut),
    ]
    print("--------------------------------------------------------------------------------")
    print(f"Reordering labels ({tag}) with the following command: {' '.join(map(str, reorder_command))}")
    subprocess.run(reorder_command, check=True)

    duration = time.time() - start_time
    print(f"Label reordering ({tag}) completed in {duration:.2f} seconds.")
    print("--------------------------------------------------------------------------------")
    return duration


def prepare_parcellation_inputs(seg_output_pp_dir: Path, parc_input_dir: Path, num_workers: int) -> float:
    """
    Prepare inputs for cortex parcellation by combining cortex labels:
    - Left cortex labels (1000-1999) -> 3
    - Right cortex labels (2000-2999) -> 42

    Uses:
      $GOUHFI_HOME/data_utils/remove_keep_reindex_labels.py --combine-ctx
    """
    start_time = time.time()

    script_path = Path(gouhfi_home) / "data_utils" / "remove_keep_reindex_labels.py"
    _ensure_exists(script_path, "remove_keep_reindex_labels.py")

    prepare_command = [
    "python3", str(script_path),
    "--input", str(seg_output_pp_dir),
    "--output", str(parc_input_dir),
    "--keep-labels", "2", "21",
    "--prep4ctx",
    "--num-workers", str(num_workers),
    ]

    print("--------------------------------------------------------------------------------")   
    print(f"Preparing parcellation inputs with: {' '.join(map(str, prepare_command))}")
    subprocess.run(prepare_command, check=True)

    duration = time.time() - start_time
    
    print(f"Parcellation input preparation completed in {duration:.2f} seconds.")
    print("--------------------------------------------------------------------------------")
    return duration
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
# Functions to run the two different pipelines: v1 (old) and v2 (new)
def run_pipeline_v1(input_dir: str, output_root: Path | None, np: int, folds: str, reorder_labels: bool, cpu: bool) -> None:
    """Old behavior, only when --v1 is used."""
    folds_list = folds.split()

    input_path = Path(input_dir).resolve()
    if output_root is None:
        out_inf = input_path / "outputs"
        out_pp = input_path / "outputs_postpro"
        out_reo = input_path / "outputs_postpro_reo"
    else:
        output_root = Path(output_root).resolve()
        out_inf = output_root
        out_pp = output_root / "outputs_postpro"
        out_reo = output_root / "outputs_postpro_reo"

    out_inf.mkdir(parents=True, exist_ok=True)
    out_pp.mkdir(parents=True, exist_ok=True)
    if reorder_labels:
        out_reo.mkdir(parents=True, exist_ok=True)

    pp_pkl, plans_json = _postproc_paths(MODEL_V1)
    _ensure_exists(pp_pkl, "postprocessing.pkl")
    _ensure_exists(plans_json, "plans.json")

    print("--------------------------------------------------------------------------------")
    _announce_inputs("GOUHFI 1.0 subcortical segmentation: ", input_path)
    print("--------------------------------------------------------------------------------")
    run_inference(MODEL_V1, input_dir=input_dir, output_dir=out_inf, folds=folds_list, num_pr=np, cpu=cpu)
    apply_post_processing(out_inf, out_pp, pp_pkl, np, plans_json, tag="v1")

    if reorder_labels:
        print("--------------------------------------------------------------------------------")
        print("Reordering label maps to FreeSurfer's lookup table (v1)...")
        in_lut = os.path.join(gouhfi_home, "misc/gouhfi_v2p0_brain_labels_lut.txt")
        out_lut = os.path.join(gouhfi_home, "misc/freesurfer_brain_labels_lut.txt")
        apply_reordering(out_pp, out_reo, in_lut=in_lut, out_lut=out_lut, tag="v1")
        print("--------------------------------------------------------------------------------")


def run_pipeline_v2(input_dir: str,
                    output_root: Path | None,
                    np: int,
                    folds: str,
                    reorder_labels: bool,
                    cpu: bool,
                    skip_seg: bool,
                    skip_parc: bool) -> None:
    """
    New default: run segmentation -> prepare inputs for parcellation -> run parcellation.
    Output folders are separated: outputs_seg* and outputs_parc*.
    """
    folds_list = folds.split()
    input_path = Path(input_dir).resolve()

    # Decide where outputs live
    base_out = Path(output_root).resolve() if output_root is not None else input_path

    # --- SEG output dirs ---
    seg_out_inf = base_out / "outputs_seg"
    seg_out_pp = base_out / "outputs_seg_postpro"
    seg_out_reo = base_out / "outputs_seg_postpro_reo"

    # --- PARC input + output dirs ---
    parc_in_dir = base_out / "cortex_seg_only"   # intermediate cortex segmentation inputs for parc model
    parc_out_inf = base_out / "outputs_parc"
    parc_out_pp = base_out / "outputs_parc_postpro"
    parc_out_reo = base_out / "outputs_parc_postpro_reo"

    # Create dirs depending on what we run
    if not skip_seg:
        seg_out_inf.mkdir(parents=True, exist_ok=True)
        seg_out_pp.mkdir(parents=True, exist_ok=True)
        if reorder_labels:
            seg_out_reo.mkdir(parents=True, exist_ok=True)

    if not skip_parc:
        parc_in_dir.mkdir(parents=True, exist_ok=True)
        parc_out_inf.mkdir(parents=True, exist_ok=True)
        parc_out_pp.mkdir(parents=True, exist_ok=True)
        if reorder_labels:
            parc_out_reo.mkdir(parents=True, exist_ok=True)

    # --- SEG stage ---
    if not skip_seg:
        seg_pp_pkl, seg_plans_json = _postproc_paths(MODEL_SEG)
        _ensure_exists(seg_pp_pkl, "postprocessing.pkl")
        _ensure_exists(seg_plans_json, "plans.json")
        
        print("--------------------------------------------------------------------------------")
        _announce_inputs("GOUHFI 2.0 Subcortical segmentation: ", input_path)
        print("--------------------------------------------------------------------------------")
        run_inference(MODEL_SEG, input_dir=input_dir, output_dir=seg_out_inf, folds=folds_list, num_pr=np, cpu=cpu)
        print("--------------------------------------------------------------------------------")
        apply_post_processing(seg_out_inf, seg_out_pp, seg_pp_pkl, np, seg_plans_json, tag="seg")

        if reorder_labels:
            print("--------------------------------------------------------------------------------")
            print("Reordering label maps to FreeSurfer's lookup table (subcortical segmentation)...")
            in_lut = os.path.join(gouhfi_home, "misc/gouhfi_v2p0_brain_labels_lut.txt")
            out_lut = os.path.join(gouhfi_home, "misc/freesurfer_brain_labels_lut.txt")
            apply_reordering(seg_out_pp, seg_out_reo, in_lut=in_lut, out_lut=out_lut, tag="seg")
            print("--------------------------------------------------------------------------------")

    # --- Prepare inputs for PARC stage + PARC inference ---
    if not skip_parc:
        # Determine parcellation input directory:
        # - default: created from seg_out_pp using remove_keep_reindex_labels.py --combine-ctx
        # - if --skip_seg: user must provide a directory that already contains the isolated cortex seg inputs
        if skip_seg:
            parc_model_input_dir = input_path  # use the -i/--input_dir provided by user

            if not parc_model_input_dir.exists():
                raise FileNotFoundError(f"Input directory not found: {parc_model_input_dir}")

            # Provide a helpful note if they forgot to give cortex-only inputs
            print(
                "NOTE: --skip_seg was set. The parcellation model will use the provided --input_dir directly.\n"
                "      Make sure --input_dir contains the isolated cortex segmentation inputs expected by the parc model,\n"
                "      i.e., outputs previously produced by the segmentation stage or by running\n"
                "      $GOUHFI_HOME/data_utils/remove_keep_reindex_labels.py with the --combine-ctx flag."
            )
        else:
            # We ran seg (or will have seg outputs), so prepare cortex-only inputs for parc
            if not seg_out_pp.exists():
                raise FileNotFoundError(
                    f"Expected segmentation post-processed outputs at: {seg_out_pp}\n"
                    f"Run without --skip_seg, or provide cortex-only inputs and use --skip_seg."
                )

            _announce_inputs("Cortical parcellation input preparation: ", seg_out_pp)
            prepare_parcellation_inputs(seg_output_pp_dir=seg_out_pp, parc_input_dir=parc_in_dir, num_workers=np)
            parc_model_input_dir = parc_in_dir

        parc_pp_pkl, parc_plans_json = _postproc_paths(MODEL_PARC)
        _ensure_exists(parc_pp_pkl, "postprocessing.pkl")
        _ensure_exists(parc_plans_json, "plans.json")
        print("--------------------------------------------------------------------------------")
        _announce_inputs("GOUHFI 2.0 Cortical parcellation: ", parc_in_dir)

        run_inference(
            MODEL_PARC,
            input_dir=str(parc_model_input_dir),
            output_dir=parc_out_inf,
            folds=folds_list,
            num_pr=np,
            cpu=cpu
        )
        print("--------------------------------------------------------------------------------")
        apply_post_processing(parc_out_inf, parc_out_pp, parc_pp_pkl, np, parc_plans_json, tag="parc")

        if reorder_labels:
            print("--------------------------------------------------------------------------------")
            print("Reordering label maps to FreeSurfer's lookup table (cortex parcellation)...")
            in_lut = os.path.join(gouhfi_home, "misc/gouhfi_v2p0_cortex_labels_lut.txt")
            out_lut = os.path.join(gouhfi_home, "misc/freesurfer_cortex_labels_lut.txt")
            apply_reordering(parc_out_pp, parc_out_reo, in_lut=in_lut, out_lut=out_lut, tag="parc")
            print("--------------------------------------------------------------------------------")

#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
# Main function to parse arguments and run the appropriate pipeline
def main():
    parser = argparse.ArgumentParser(description="Run GOUHFI nnUNet_v2 inference pipelines (v1 or v2).")
    parser.add_argument("-i", "--input_dir", required=True, help="Directory containing input data.")
    parser.add_argument("-o", "--output_dir", help="Directory to save output data (root). If omitted, outputs go next to input_dir.")
    parser.add_argument("--np", type=int, default=4, help="Number of CPU processes to run post-processing in parallel.")
    parser.add_argument("--folds", default="0 1 2 3 4", help="Folds to use for inference. Default: all folds.")
    parser.add_argument("--reorder_labels", action="store_true", help="Reorder label values to the FreeSurfer lookup table after post-processing.")
    parser.add_argument("--cpu", action="store_true", help="Use CPU for inference. Expect a considerable increase in inference time.")

    # New flags
    parser.add_argument("--v1", action="store_true", help="Use the original v1 single-model pipeline (GOUHFI 1.0).")
    parser.add_argument("--skip_parc", action="store_true", help="Skip cortical parcellation stage (v2 pipeline only).")
    parser.add_argument("--skip_seg", action="store_true", help="Skip subcortical segmentation stage (v2 pipeline only).")

    args = parser.parse_args()

    # Normalize input_dir
    input_dir = args.input_dir.rstrip("/")

    # Pick pipeline
    if args.v1:
        # Old behavior only when explicitly requested
        run_pipeline_v1(
            input_dir=input_dir,
            output_root=args.output_dir,
            np=args.np,
            folds=args.folds,
            reorder_labels=args.reorder_labels,
            cpu=args.cpu,
        )
    else:
        # New default behavior
        run_pipeline_v2(
            input_dir=input_dir,
            output_root=args.output_dir,
            np=args.np,
            folds=args.folds,
            reorder_labels=args.reorder_labels,
            cpu=args.cpu,
            skip_seg=args.skip_seg,
            skip_parc=args.skip_parc,
        )


if __name__ == "__main__":
    main()
