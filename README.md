# GOUHFI: novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI
 
Welcome to **GOUHFI**, a novel deep learning (DL) tool for segmentation of brain MR images of **any** contrast, resolution or even field strength. This repository provides detailed instructions on [Installation](#installation), [Usage](#usage), [Related work](#third-party-softwares-related-to-gouhfi) and [Licensing](#license). While the main goal of this repository is to share GOUHFI with the community, few useful commands/scripts for neuroscientists/neuroimagers working with label maps are also shared (see [Usage section](#usage) for some examples). 

---

## How was GOUHFI developed?

GOUHFI is a fully automatic, contrast- and resolution-agnostic, DL-based brain segmentation tool optimized for Ultra-High Field MRI (UHF-MRI), while also demonstrating strong performance at 3T compared to other well-established techniques. Using the domain randomization approach proposed in [SynthSeg](https://github.com/BBillot/SynthSeg) and a state-of-the-art 3D U-Net with Residual Encoders from the [nnUNetv2](https://github.com/MIC-DKFZ/nnUNet) framework, GOUHFI is able to handle various contrasts, resolutions and even field strengths without requiring fine-tuning or retraining. Tested on multiple datasets, it showed high accuracy and impressive robustness to noise and inhomogeneities, making it a valuable tool for neuroscientists working at both 3T and UHF-MRI. For more details on how GOUHFI was developed, please refer to the [following paper]() which i currently under submission.

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
- Once your python virtual environment is created, you need to execute the remaining steps inside this virtual environment. Thus, activate the virtual environment by typing:
```bash
conda activate gouhfi
```

### Step 2: Install PyTorch 

- Follow the instructions on the [PyTorch website](https://pytorch.org/get-started/locally/) to install the stable PyTorch version based on your OS (Linux, Mac or Windows), package manager (choose `pip` if unsure), language (Python) and compute platform (CUDA 11.8 was tested for GOUHFI, but your system requirements might be different and more recent versions probably work [but not tested]).
- This step should be done before step 3 below [as recommended at step #1 here](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/installation_instructions.md#installation-instructions) by the nnUNet team. I do not know why, but better safe than sorry.


### Step 3: Clone & install the repository locally

```bash
cd path/where/you/want/gouhfi/to/be/installed
git clone https://github.com/mafortin/GOUHFI.git
cd GOUHFI
pip install -e .
```

- The `pip install -e .` command allows you to install the GOUHFI repository in "editable" mode where you can modify the different scripts to your liking.

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
Add the following lines to your `.bashrc` or `.zshrc` file (depending on which shell you are using. `.bashrc` for `.sh` and `.zshrc` for `.zsh`.)
```bash
export GOUHFI_HOME=/full/path/to/GOUHFI
export nnUNet_results=/path/to/nnUNet_results
```
- where `/full/path/to/GOUHFI` is the full path to your GOUHFI installation directory.
- where `/path/to/nnUNet_results` is the full path to the nnUNet results directory.
   - **Note**: Setting this variable as the `trained_model` directory can be a good idea, while not an actual requirement. If you already have a nnUNet installation installed from previous work, this line is probably already set (no need to add it a second time).

You can double-check if this step worked properly by typing in your terminal:
```bash
source ~/.bashrc
echo $GOUHFI_HOME
```
- where `~/.bashrc` can be `~/.zshrc`.

- For more information, the [nnUNet documentation](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md) is quite helpful (no need to set the nnUNet environment variables as described in this link **except** if you plan on retraining GOUHFI).

### Step 7: Test the installation

- In your terminal, type:

```bash
run_goufhi --help
```

- If you see the help function for `run_gouhfi` (or any other functions related to GOUHFI described [below](#usage)), you have installed the repository properly. Congrats and happy segmenting!

---


## Usage

- **Reminder**: All these functions need to be executed inside your virtual environment.

### `run_gouhfi`: 

- This is the command to obtain the whole brain segmentation into 35 labels from GOUHFI.
    - The command `run_gouhfi` is used to (1) run the inference (i.e., segment your images using the trained model), (2) apply the post-processing step and (3), if desired, reorder the label values in the segmentations produced from GOUHFI (optional). 
        - More precisely, the third step changes GOUHFI's lookuptable (LUT) (i.e., label values from 0 to 35) to the FreeSurfer LUT which is commonly used by the neuroimaging community. 
- We strongly recommend to use a GPU to run the inference (anything with >8 Gb of VRAM should be strong enough, but not officially tested). CPU can be used but expect a considerable increased in computation time (e.g., ca. ~10 sec/subject on GPU and can be roughly ~75 times longer or even more on the CPU depending on the setup).
- **Tip**: A few images are available for testing purposes in the `test_data` directory if you just want to quickly test GOUHFI.

Example command line:

```bash
run_gouhfi -i /path/to/input_data -o /path/to/output_dir [--np N] [--folds "0 1 2 3 4"] [--reorder_labels] [--cpu]
```

### Arguments

| Argument              | Type    | Default                                                              | Description                                                                                |
|-----------------------|---------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`   | `str`   | **Required**                                                         | Path to the directory containing input `.nii.gz` files.                                    |
| `-o`, `--output_dir`  | `str`   | Derived from `input_dir` as `../outputs/`                            | Directory where the segmentations will be saved.                                            |
| `--np`                | `int`   | `8`                                                                  | Number of parallel CPU processes to use during post-processing.                            |
| `--folds`             | `str`   | `"0 1 2 3 4"`                                                        | Space-separated string of folds to use for inference (we recommend to use all).            |
| `--reorder_labels`    | `flag`  | `False`                                                              | If set, reorders label values from GOUHFI's LUT to FreeSurfer's LUT after post-processing. |
| `--cpu`               | `flag`  | `False`                                                              | If set, the cpu will be used instead of the GPU for running the inference.                 |

#### Input Requirements

- File:
    - Format: compressed NIfTI (`.nii.gz`)
    - Naming convention: The nnUNet naming convention (i.e., `{SUBJECT_ID}_0000.nii.gz`). More details [here](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md). See [run_renaming](#run_renaming) if not the case.
    - If you have >1 image to segment, all images should be inside the input directory defined by `--input_dir` under distinctive filenames, and **not** inside different sub-directories. The output segmentations will follow the same naming convention as the input filenames minus the `_0000` string.  

- Image:
    - Contrast: Any
    - Resolution: Any (resampling to isotropic resolution is processed internally. Not tested for highly anisotropic images, but always worth a try).
    - Field Strength: Any (extensively validated at 3T, 7T and 9.4T)
    - Orientation: LIA (like FastSurfer [see [run_conforming](#run_conforming)])
    - Brain-extracted/Skull-stripped [see [run_brain_extraction](#run_brain_extraction)]


#### Outputs

File:
- `{SUBJECT_ID}.nii.gz` —> Segmentation/Label map for the `{SUBJECT_ID}` subject.

Segmentation/Label map:
- The labels are linearly ordered from 0 (background) to 35 by default if not reordered as described above. The complete list of labels is shown in file [misc/gouhfi-label-list-lut.txt](https://github.com/mafortin/GOUHFI/blob/main/misc/gouhfi-label-list-lut.txt).
- As for **any** automatic segmentation tool, we recommend the user to visually inspect the quality of the segmetation outputs produced by GOUHFI.
   - While the technique has been extensively tested, it may still have unknown limitations. We kindly encourage users to report any issues or unexpected behavior to help guide future improvements and development. 

---

### `run_conforming`:

- The command `run_conforming` *conforms* all the `.nii` or `.nii.gz` images found in the specified input directory using FastSurfer’s `conform.py` script.
- This step basically reorients your image to LIA orientation, rescales the values between 0 and 255 and resamples the image to the minimal isotropic resolution (i.e., to the smallest voxel dimension). More details [here](https://github.com/deep-mi/FastSurfer/blob/dev/FastSurferCNN/data_loader/conform.py).

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

### `run_brain_extraction`:


- The command `run_brain_extraction` brain-extracts/skull-strips all the `.nii` or `.nii.gz` images found in the specified input directory using `antspynet.brain_extraction` function.

```bash
run_brain_extraction -i /path/to/input_dir [-o /path/to/output_dir] [--modality t1] [--dilatation_voxels 2] [--mask_folder /path/to/new/masked] [--skip_morpho --rename ]
```

#### Arguments

| Argument             | Default        | Description                                                                                                                            |
|----------------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`  | -              | Path to directory containing input NIfTI files (required).                                                                             |
| `-o`, `--output_dir` | -              | Directory to save the brain-extracted images. If not set, defaults to `--input_dir`.                                         |
| `--modality`         | `t1`           | Modality for brain extraction (default: t1).                                                                                           |
| `--skip_morpho`      | -              | Skip morphological operations on the brain mask and directly save the newly brain-extracted image(s).                                 |
| `--dilation_voxels`  | 0              | Number of voxels for dilation (default: 0).                                                                                            |
| `--rename`           | -              | Flag to rename the brain-extracted image(s) by adding the '_masked' suffix. Otherwise, brain extracted images will keep the same name. |
| `--mask_folder`      | -              | Path to the folder containing masks for morphological operations (requires the morphological operations to be applied).               |


---

### `run_labels_reordering`:

- If you did not use the `--reorder_labels` flag when running `run_gouhfi`, you can reorder the labels using the `run_labels_reordering` command as shown below. 
- Once reordered, your label maps can be used in the same quantiative pipeline as label maps produced by *FreeSurfer*/*FastSurfer*.

```bash
run_labels_reordering -i /path/to/input_dir [-o /path/to/output_dir] --old_labels_file ./misc/gouhfi-label-list-lut.txt --new_labels_file ./misc/freesurfer-label-list-lut.txt
```

#### Arguments

| Argument             | Default        | Description                                                                                                                       |
|----------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`  | -              | Path to the input directory containing label maps (required).                                                                      |
| `-o`, `--output_dir` | -              | Path to the output directory to save processed label maps (optional).                                                               |
| `--old_labels_file`  | -              | Path to the text file containing GOUHFI's label definitions (label IDs and names) [in the `/misc/` subdirectory] (required).        |
| `--new_labels_file`  | -              | Path to the text file containing FreeSurfer/new label definitions (label IDs and names) [in the `/misc/` subdirectory] (required). |

---

### `run_renaming`:

- If your images are ready to be segmented, but do not respect the [nnunet naming convention](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md), you can use the `run_renaming` command as shown here:

```bash
run_renaming -i /path/to/input_dir -o /path/to/output_dir [--start_substring ./misc/gouhfi-label-list-lut.txt --end_substring ./misc/freesurfer-label-list-lut.txt --segms]
```

#### Arguments

| Argument               | Default        | Description                                                                                                                                                 |
|------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`    | -              | Path to the input directory containing files to rename (required).                                                                                          |
| `-o`, `--output_dir`   | *input_dir*    | Path to the output directory to save the renamed files and JSON correspondence file. Defaults to same as input directory.                                   |
| `--start_substring`    | `sub`          | Substring that marks the beginning of the subject ID within filenames. If omitted along with `--end_substring`, the full filename (minus extension) is used. |
| `--end_substring`      | `_`            | Substring that marks the end of the subject ID within filenames. See `--start_substring` for default behavior if omitted.                                   |
| `--segms`              | -              | Use this flag if the files are label maps. The renamed files will **not** include the `_0000` suffix.                                                       |

- **Note**: A `subject_id_correspondence.json` file will be created and saved in `input_dir` to keep tract of the correspondence between the old and new filenames.


### `run_add_label`:

- If you want to reproduce what we did for creating the synthetic images for training from label maps with the additional 'Extra-Cerebral' label, use the following shown below.
    - As mentioned in [Third-Party softwares related to GOUHFI](#third-party-softwares-related-to-gouhfi), this repository does **not** include the necessary scripts to create synthetic images from SynthSeg. Please refer to [SynthSeg's repository](https://github.com/BBillot/SynthSeg) for this.

```bash
run_add_label -i /path/to/input_dir -o /path/to/output_dir [--labelmap aseg] [--mask mask.mgz] [--image orig.mgz] [--dilate-iters 4] [--save_new_mask] [--new_label 257] [--fill_holes] [--new_labelmap_name aseg_mod.nii.gz]
```


| Argument               | Default                          | Description                                                                                                                     |
|------------------------|----------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`     | -                                | Directory containing input files (label map, mask, and MRI image inside the **same** folder) (required).                                                  |
| `-o`, `--output_dir`    | -                                | Directory to save the output files. If not provided, defaults to the input directory.                                          |
| `--labelmap`            | `aseg`                           | Substring to identify the label map file (e.g., 'aseg.mgz').                                                                   |
| `--mask`                | `mask.mgz`                       | Substring to identify the mask file (e.g., 'mask.mgz').                                                                         |
| `--image`               | `orig.mgz`                       | Substring to identify the input MRI image (e.g., 'orig.mgz').                                                                   |
| `--fill_holes`          | -                                | Flag to fill holes in the mask.                                                                                                 |
| `--dilate-iters`        | None                             | Number of iterations for morphological dilation (default: skipped if not provided).                                            |
| `--save_new_mask`       | -                                | Flag to save the modified mask with morphological operations applied.                                                           |
| `--new_label`           | `257`                            | New label value to be added to the label map (default: 257).                                                                    |
| `--new_labelmap_name`   | `aseg_mod.nii.gz`                | New name for the modified label map. Include the file extension (default: 'aseg_mod.nii.gz').                                   |


---

## Third-Party softwares related to GOUHFI

This project incorporates code from the following projects, used under the Apache License 2.0:

Image preparation/preprocessing:
- [FastSurfer/FastSurferVINN](https://github.com/Deep-MI/FastSurfer):
    - In this project, the script `conform.py` from FastSurfer/FastSurferVINN was used for *conforming* the images to be segmented by GOUHFI (i.e., reorienting to LIA, resampling to isotropic resolution and normalizing signal values between 0 and 255). 
    - The script has been used as is, without modification, and is shared as part of the GOUHFI repository to make the repository more self-contained. 
    - If you have an already up and running FastSurfer installation, you can use it directly from there. In this repository, the function `run_conforming` will execute this script.
- [ANTsPyNet](https://github.com/ANTsX/ANTsPyNet):
    - For brain extraction. Quick and efficient brain extraction tool (`antspynet.brain_extraction`) if you need to do this for your images to be segmented. 
    - We provide a script called `brain_extraction_antspynet.py` where we wrapped an unmodified implementation of `antspynet.brain_extraction` to make the repository more self-contained. 
    - If you have an already up and running ANTsPyNet installation, you can use it directly from there. In this repository, the function `run_brain_extraction` will execute this script.

Training:
- [nnU-Net v2](https://github.com/MIC-DKFZ/nnUNet):
    - The nnUNet v2 framework was used for training, inference, post-processing and evaluation of GOUHFI.
    - This repository contains the full nnUNetv2 directory (version [v2.4.1](https://github.com/MIC-DKFZ/nnUNet/releases/tag/v2.4.1)).
    - If you would like to reproduce the full training pipeline as explained in the GOUHFI paper (or retrain a model from scratch), you should be able to do so with GOUHFI's installation alone. 
        - However, we recommend the users to refer to the [nnUNet documentation](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/) for more information on how to proceed since the documentation is not included in this repository.

Generating synthetic images for training:
- [SynthSeg](https://github.com/BBillot/SynthSeg):
    - The synthetic images used to train GOUHFI were generated from the generative model proposed in SynthSeg. 
    - Since SynthSeg is a complex beast on its own, we have decided to **not** include it in this repository. 
    - However, the approach used to create the synthetic training data for GOUHFI is very similar to the one shown in the [2-generation_explained.py](https://github.com/BBillot/SynthSeg/blob/master/scripts/tutorials/2-generation_explained.py) tutorial script available in the [SynthSeg GitHub repository](https://github.com/BBillot/SynthSeg). Thus, we recommend to people interested in reproducing the full pipeline with the synthetic image generation process to install SynthSeg on its own and follow their well designed tutorials.
        - Basically, by 
            1) Swapping the original *labels_classes_priors* files from SynthSeg in the [2-generation_explained.py](https://github.com/BBillot/SynthSeg/blob/master/scripts/tutorials/2-generation_explained.py) file by the ones shared in the [/misc/](https://github.com/mafortin/GOUHFI/tree/main/misc) subdirectory here in this repository (the four `.npy` files),
            2) setting the variable `n_neutral_labels` to 6 and `randomise_res` to False, and
            3) using the model parameters described in the appendices of the paper (under submission) for the generative model,
            - You can create synthetic images for label maps containing the 'Extra-Cerebral' label (see [run_add_label](#run_add_label) for how to perform this). 
    - More details about the generative model can be found in the [brain_generator.py](https://github.com/BBillot/SynthSeg/blob/master/SynthSeg/brain_generator.py) script and questions about the generative model should be addressed to the [SynthSeg team](https://github.com/BBillot/SynthSeg).

---

## Citation

If you use **GOUHFI** in your research, please cite the following:

For the paper (currently under submission):
```
@article{fortin2025gouhfi,
  title         = {GOUHFI: A Novel Contrast- and Resolution-Agnostic Segmentation Tool for Ultra-High Field MRI},
  author        = {Fortin, Marc-Antoine and others},
  journal       = {arXiv preprint arXiv:XXXX.XXXXX},
  year          = {2025},
  archivePrefix = {arXiv},
  eprint        = {XXXX.XXXXX},
  primaryClass  = {eess.IV}
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

[Marc-Antoine Fortin](https://www.ntnu.no/ansatte/marc.a.fortin)  
Norwegian University of Science and Technology (NTNU)  
Contact: [marc.a.fortin@ntnu.no](mailto:marc.a.fortin@ntnu.no)
