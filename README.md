# GOUHFI: novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI
 
Welcome to **GOUHFI**, a novel deep learning (DL) tool for segmentation of brain MR images of **any** contrast, resolution or even field strength. This repository provides detailed instructions on [installation](#installation), [usage](#usage), [related work](#third-party-softwares-related-to-gouhfi) and [licensing](#license).

---

## How was GOUHFI developed?

GOUHFI is a fully automatic, contrast- and resolution-agnostic, DL-based brain segmentation tool optimized for Ultra-High Field MRI (UHF-MRI), while also demonstrating strong performance at 3T compared to other well-established techniques. Using the domain randomization approach proposed in [SynthSeg](https://github.com/BBillot/SynthSeg) and a state-of-the-art 3D U-Net with Residual Encoders from [nnUNetv2](https://github.com/MIC-DKFZ/nnUNet), GOUHFI is able to handle various contrasts, resolutions and even field strengths without requiring fine-tuning or retraining. Tested on multiple datasets, it showed high accuracy and impressive robustness to noise and inhomogeneities, making it a valuable tool for neuroscientists working at both 3T and UHF-MRI. For more details about how GOUHFI was developed please refer to the [following paper]() which i currently under submission.

![GOUHFI](figs/fig-readme.png)

---

## Installation

### Step 1: Create a Python virtual environment

- As for any Python project, we highly recommend you to install GOUHFI inside a virtual environment. Whether you use pip, anaconda or miniconda is up to you, but the steps below use conda. Relevant links related to [conda](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/) in general or [its installation](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html) for Ubuntu distributions (OS dependent).

- If you are using conda, you can use the following command: 
```bash
conda create --name gouhfi python=3.10 
```
- `gouhfi` in the above command line is the name of the virtual environment and can be replaced by anything else if preferred.
- Once your python virtual environment is created, you need to execute the remaining steps inside this virtual environment. Thus, activate thi virtual environment by typing:
```bash
conda activate gouhfi
```

### Step 2: Install PyTorch 

- Follow the instructions on the [PyTorch website](https://pytorch.org/get-started/locally/) to install the stable PyTorch version based on your OS, package manager, language (Python here) and compute platform (CUDA 11.8 tested for GOUHFI, but your system requirements might be different).
- This step **has to be done before** step 2 below as recommended by the nnUNet team. See step #1 [here](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/installation_instructions.md#installation-instructions).


### Step 3: Clone & install the repository locally

```bash
cd path/where/you/want/gouhfi/to/be/installed
git clone https://github.com/mafortin/GOUHFI.git
cd GOUHFI
pip install -e .
```

### Step 4: Download the trained model weights

1) A Zenodo link to the trained model weights is included in the repository in the `trained_model/gouhfi-trained-model-weights.md` file or simply with this [link](https://zenodo.org/records/15255556). This might require you to have a Zenodo account (free).
2) Move this `GOUHFI.zip` in the `trained-model` folder before unzipping it.

### Step 5: Unzip the `GOUHFI.zip`

- To unzip `GOUHFI.zip`, use the following command:
```bash
cd trained_model/
unzip GOUHFI.zip
```

- Once unzipped, you should have a folder called `Dataset014_gouhfi` with all trained folds and related files in the `trained_model` folder.

### Step 6: Set GOUHFI's directory as an environment variable

- For Linux/MacOS:
Add the following line to your `.bashrc` or `.zshrc` file (depending which shell you are using. `.bashrc` for `.sh` and `.zshrc` for `.zsh`.)
```bash
export GOUHFI_HOME=/full/path/to/GOUHFI
```
- where `/full/path/to/GOUHFI` is the full path to your GOUHFI installation directory. 

You can double-check if this step worked properly by typing in your terminal:
```bash
source ~/.bashrc
echo $GOUHFI_HOME
```
- where `~/.bashrc` can be `~/.zshrc`.

- For more information, the [nnUNet documentation](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md) is quite helpful.

### Step 7: Test the installation

- In your terminal, type:

```bash
run_goufhi --help
```

- If you see the help function for `run_gouhfi` (or any other functions related to GOUHFI), you have installed the repository properly. Congrats and happy segmenting!

---


## Usage

- **Reminder**: All these functions need to be executed inside your virtual environment.

### Run Inference:

The command `run_gouhfi` is used to run the inference (i.e., segment your images using the trained model), apply the post-processing and, if desired, reorder the label values in the segmentations from GOUHFI's lookuptable (LUT) (i.e., linearly increasing from 0 to 35) to FreeSurfer's LUT (optional).

```bash
run_gouhfi.py -i /path/to/input_data -o /path/to/output_dir [--np N] [--folds "0 1 2"] [--reorder_labels] [--help]
```

### Arguments

| Argument              | Type    | Default                                                              | Description                                                                                |
|-----------------------|---------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`   | `str`   | **Required**                                                         | Path to the directory containing input `.nii.gz` files.                                    |
| `-o`, `--output_dir`  | `str`   | Derived from `input_dir` as `../outputs/`                            | Directory where the segmentation will be saved.                                            |
| `--np`                | `int`   | `8`                                                                  | Number of parallel CPU processes to use during post-processing.                            |
| `--folds`             | `str`   | `"0 1 2 3 4"`                                                        | Space-separated string of folds to use for inference (we recommend to use all).            |
| `--reorder_labels`    | `flag`  | `False`                                                              | If set, reorders label values from GOUHFI's LUT to FreeSurfer's LUT after post-processing. |


#### Input Requirements

- File:
    - Format: compressed NIfTI (`.nii.gz`)
    - Naming convention: The nnUNet naming convention (i.e., `{CASE_IDENTIFIER}_0000.nii.gz`). More details [here](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md).
    - If you have >1 image to segment, all images should be inside the input directory defined by `--input` under distinctive filenames, and **not** inside different sub-directories. The output segmentations will follow the same naming convention as the input filenames minus the `_0000` string.  

- Image:
    - Contrast: Any
    - Resolution: Any (resampling to isotropic resolution is processed internally. Not tested for highly anisotropic images, but always worth a try.)
    - Field Strength: Any (extensively validated at 3T, 7T and 9.4T)
    - Orientation: LIA (like FastSurfer [see the `run_conforming` command below])
    - Brain-extracted/Skull-stripped [see the `run_brain_extraction` command below]


#### Output

File:
- `{CASE_IDENTIFIER}.nii.gz` —> Segmentation result/Label map for the `{CASE_IDENTIFIER}` subject.

Segmentation/Label map:
- The labels are linearly ordered from 0 (background) to 35 by default. The complete list of labels is shown in file `misc/label-list-lut.txt`.

---

### Run conforming:

The command `run_conforming` conforms all `.nii` or `.nii.gz` images in a specified input directory using FastSurfer’s `conform.py` script. The output will be saved to a specified directory or to a default `inputs-cfm/` directory.

```bash
run_conforming -i /path/to/input_dir [-o /path/to/output_dir] [--order 3] [--dtype float32] [--seg_input]
```

#### Arguments

| Argument             | Default                   | Description                                                                                                 |
|----------------------|---------------------------|-------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`  | -                         | Path to directory containing input NIfTI files (required).                                                  |
| `-o`, `--output_dir` | *input_dir*/`inputs-cfm/` | Directory to save the conformed images. If not set, defaults to `inputs-cfm` next to input.                 |
| `--order`            | `3`                       | Interpolation order for resampling. Common values: 0 (nearest), 1 (linear), 3 (cubic spline).               |
| `--dtype`            | `"float32"`               | Data type of output images. Options include: `float32`, `uint8`, `int16`, `int32`.                          |
| `--seg_input`        | *False*                   | Use this flag if the input images are label maps (e.g. segmentations). Uses nearest-neighbor interpolation. |


---

### Run brain extraction:


The command `run_conforming` conforms all `.nii` or `.nii.gz` images in a specified input directory using FastSurfer’s `conform.py` script. The output will be saved to a specified directory or to a default `inputs-cfm/` directory.

```bash
run_brain_extraction -i /path/to/input_dir [-o /path/to/output_dir] [--order 3] [--dtype float32] [--seg_input]
```

#### Arguments

| Argument             | Default        | Description                                                                                                                            |
|----------------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`  | -              | Path to directory containing input NIfTI files (required).                                                                             |
| `-o`, `--output_dir` | -              | Directory to save the conformed images. If not set, defaults to `inputs-cfm` next to input.                                            |
| `--modality`         | `t1`           | Modality for brain extraction (default: t1).                                                                                           |
| `--skip_morpho`      | -              | Skip morphological operations on the brain mask and directly save the newly brain-extracted image(s).                                 |
| `--dilation_voxels`  | 0              | Number of voxels for dilation (default: 0).                                                                                            |
| `--rename`           | -              | Flag to rename the brain-extracted image(s) by adding the '_masked' suffix. Otherwise, brain extracted images will keep the same name. |
| `--mask_folder`      | -              | Path to the folder containing masks for morphological operations (requires the morphological operations to be applied).               |


---

### Run label map reordering:

If you did not use the `--reorder_labels` flag when running `run_gouhfi`, you can reorder the labels using the `run_labels_reordering` command as shown below.

```bash
run_labels_reordering -i /path/to/input_dir -o /path/to/output_dir --old_labels_file ./misc/gouhfi-label-list-lut.txt --new_labels_file ./misc/freesurfer-label-list-lut.txt
```

#### Arguments

| Argument             | Default        | Description                                                                                                                       |
|----------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`  | -              | Path to the input directory containing label maps (required).                                                                      |
| `-o`, `--output_dir` | -              | Path to the output directory to save processed label maps (optional).                                                               |
| `--old_labels_file`  | -              | Path to the text file containing GOUHFI's label definitions (label IDs and names) [in the `/misc/` subdirectory] (required).        |
| `--new_labels_file`  | -              | Path to the text file containing FreeSurfer/new label definitions (label IDs and names) [in the `/misc/` subdirectory] (required). |

---

### Run rename_images:

If your images are ready to be segmented, but do not respect the nnunet naming convention, you cna use the command `run_renaming` as shown here:

```bash
run_renaming -i /path/to/input_dir -o /path/to/output_dir --old_labels_file ./misc/gouhfi-label-list-lut.txt --new_labels_file ./misc/freesurfer-label-list-lut.txt
```

#### Arguments

| Argument               | Default        | Description                                                                                                                                                 |
|------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`    | -              | Path to the input directory containing files to rename (required).                                                                                          |
| `-o`, `--output_dir`   | *input_dir*    | Path to the output directory to save the renamed files and JSON correspondence file. Defaults to same as input directory.                                   |
| `--start_substring`    | `sub`          | Substring that marks the beginning of the subject ID within filenames. If omitted along with `--end_substring`, the full filename (minus extension) is used. |
| `--end_substring`      | `_`            | Substring that marks the end of the subject ID within filenames. See `--start_substring` for default behavior if omitted.                                   |
| `--segms`              | -              | Use this flag if the files are label maps. The renamed files will **not** include the `_0000` suffix.                                                       |

A `subject_id_correspondence.json` file will be created and saved in `input_dir` to keep tract of the correspondence between the old and new filenames.

---

## Third-Party softwares related to GOUHFI

This project incorporates code from the following projects, used under the Apache License 2.0:

Image preparation/preprocessing:
- [FastSurfer/FastSurferVINN](https://github.com/Deep-MI/FastSurfer):
    - In this project, the script `conform.py` from FastSurfer/FastSurferVINN was used for 'conforming' the images to be segmented by GOUHFI (i.e., reorienting to LIA, resampling to isotropic resolution and normalizing signal values between 0 and 255). The script has been used as is, without modification, and is shared as part of the GOUHFI repository to make the repository more self-contained. If you have an already up and running FastSurfer installation, you can use it directly from there. In this repository, the function `run_conforming` will execute this script.
- [ANTsPyNet](https://github.com/ANTsX/ANTsPyNet):
    - For brain extraction. Quick and efficient brain extraction tool (`antspynet.brain_extraction`) if you need to do this for your images to be segmented. We provide a script called `brain_extraction_antspynet.py` where we wrapped an unmodified implementation of `antspynet.brain_extraction` to make the repository more self-contained. If you have an already up and running ANTsPyNet installation, you can use it directly from there. In this repository, the function `run_brain_extraction` will execute this script.

Training:
- [nnU-Net v2](https://github.com/MIC-DKFZ/nnUNet):
    - The nnUNet v2 framework was used for training, inference, post-processing and evaluation of GOUHFI. This repository contains the full `nnunetv2` directory from v2.4.1 of the nnUNet. If you would like to reproduce the full training as explained in the GOUHFI paper, you should be able to do so with GOUHFI's installation alone. However, we recommend the users to refer to the [nnUNet documentation](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/) for more information on how to proceed since the documentation is not included in this repository.

Generating synthetic images for training:
- [SynthSeg](https://github.com/BBillot/SynthSeg):
    - The synthetic images used to train GOUHFI were generated from the generative model proposed in SynthSeg. The generative model parameters used are described in the appendices of the paper related to this repository. 

---


## Citation

If you use **GOUHFI** in your research, please cite the following:

For the paper (currently under submission):
```
@article{fortin2025gouhfi,
  title={GOUHFI: a novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI},
  author={Fortin, Marc-Antoine et al.},
  journal={Imaging Neuroscience (currently under submission)},
  year={2025}
}
```

For the trained model:
```
@misc{fortin2025gouhfi,
  author       = {Fortin, M.-A. and Larsen, M. and Kristoffersen, A. L. and Goa, P. E.},
  title        = {GOUHFI: Generalized and Optimized segmentation tool for Ultra-High Field Images},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.15255556},
  url          = {https://doi.org/10.5281/zenodo.15255556}
}
```

---

## Contributing

We welcome contributions. If you find bugs, have suggestions, or would like to extend the tool, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.

---

## Maintainer

Marc-Antoine Fortin  
Norwegian University of Science and Technology (NTNU)  
Contact: [marc.a.fortin@ntnu.no](mailto:marc.a.fortin@ntnu.no)