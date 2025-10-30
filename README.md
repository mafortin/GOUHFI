# GOUHFI: novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI
 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15255556.svg)](https://doi.org/10.5281/zenodo.15255556)

Welcome to **GOUHFI**, a novel deep learning (DL) tool for segmentation of brain MR images of **any** contrast, resolution or even field strength. This README provides detailed instructions on [Installation](#installation), [Usage](#usage), [Related work](#third-party-softwares-related-to-gouhfi), [Citation](#citation) and [Licensing](#license). While the main goal of this repository is to share GOUHFI with the community, some useful commands for neuroscientists/imagers working with label maps are also shared (see [Usage section](#usage) for some examples). 

## Updates

 - 29/09/25: 🎉 **GOUHFI's paper has been accepted for publication in the _Imaging Neuroscience_ journal!** 🎉 The accepted version is available online [here](https://direct.mit.edu/imag/article/doi/10.1162/IMAG.a.960/133411/GOUHFI-a-novel-contrast-and-resolution-agnostic).

---

## How was GOUHFI developed?

GOUHFI is a fully automatic, contrast- and resolution-agnostic, DL-based brain segmentation tool optimized for Ultra-High Field MRI (UHF-MRI), while also demonstrating strong performance at 3T compared to other well-established techniques. Using the domain randomization approach proposed in [SynthSeg](https://github.com/BBillot/SynthSeg) and a state-of-the-art 3D U-Net with Residual Encoders from the [nnUNetv2](https://github.com/MIC-DKFZ/nnUNet) framework, GOUHFI is able to handle various contrasts, resolutions and even field strengths without requiring fine-tuning or retraining. Tested on multiple datasets, it showed high accuracy and impressive robustness to noise and inhomogeneities, making it a valuable tool for neuroscientists working at both 3T and UHF-MRI. For more details on how GOUHFI was developed, please refer to the corresponding [paper](https://direct.mit.edu/imag/article/doi/10.1162/IMAG.a.960/133411/GOUHFI-a-novel-contrast-and-resolution-agnostic) published in Imaging Neuroscience.

![GOUHFI](figs/fig-readme.png)

---

## Installation

If you already have `conda` and `git` running on your device, the following installation procedure should be pretty straight forward. Helpful (hopefully) links were provided in some fo the steps to guide the user. GOUHFI has been successfully installed on Linux Ubuntu, Mac and Windows Operating Systems (OS).

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

- Inside your newly created python virtual environment run the following command:
```bash
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --index-url https://download.pytorch.org/whl/cu121
```
- **Note**: GOUHFI was tested for CUDA 11.8 and 12.1 and created with PyTorch 2.1.2. Other versions have **not** been tested.

### Step 3: Clone & install the repository locally

```bash
cd PATH/WHERE/THE/GOUHFI/DIRECTORY/WILL/BE/CREATED
git clone https://github.com/mafortin/GOUHFI.git
cd GOUHFI
pip install -e .
```

- where `PATH/WHERE/THE/GOUHFI/DIRECTORY/WILL/BE/CREATED` is the directory where a new directory called `GOUHFI` will be created from the `git clone` command. 
- The `pip install -e .` command allows you to install the GOUHFI repository in editable mode where you can modify the different scripts to your liking.
- **Note**: If you do not have git installed on your machine, you can manually download the ZIP file of the repository by clicking on the green `< > Code` dropdown menu on GitHub and click on the `Download ZIP` button. Once the download is completed, move the `.zip` file downloaded into the `PATH/WHERE/THE/GOUHFI/DIRECTORY/WILL/BE/CREATED` described above, extract/unzip the file and continue with the remaining installation steps from the `cd GOUHFI` and then `pip install -e .` command.

### Step 4: Download the trained model weights

1) A Zenodo link to the trained model weights is included in the repository in the `trained_model/gouhfi-trained-model-weights.md` file or simply with this [link](https://zenodo.org/records/15255556).
2) Move this `GOUHFI.zip` in the `trained-model` folder before unzipping it.

### Step 5: Unzip the `GOUHFI.zip`

- To unzip `GOUHFI.zip`, use the following command:
```bash
cd trained_model/
unzip GOUHFI.zip
```

- Once unzipped, you should have a folder called `Dataset014_gouhfi` with all five trained folds and related files in the `trained_model` folder. This is the trained GOUHFI model.
- **Note**: If you manually extracted GOUHFI with your OS GUI (i.e., not using the unzip function shown above), be careful. It might have created an additional and unwanted directory called `GOUHFI` where the `Dataset014_gouhfi` is hidden inside. Manually move `Dataset014_gouhfi` back into `trained_model` if that's the case. 

### Step 6: Set GOUHFI's directory as an environment variable

- **Note**: If you are not familiar with how to setup environment variables for different OS or shell types, please refer to the [nnUNet documentation](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md) where they have examples for their environment variables for all OS types (Here you will do it for `GOUHFI_HOME` instead of their own environment variables).

- If you’re using Linux, open your `.bashrc` file by typing `nano ~/.bashrc` in the terminal, and then add the following line: 

```bash
export GOUHFI_HOME="/PATH/WHERE/THE/GOUHFI/DIRECTORY/WILL/BE/CREATED/GOUHFI"
```
- where `/PATH/WHERE/THE/GOUHFI/DIRECTORY/WAS/CREATED/GOUHFI` is the full path to your GOUHFI installation directory.
- **Note**: For Mac, it should be the `.zshrc` file instead of the `.bashrc` file.

- Now, either open a new terminal tab or source your `.bashrc` file in the same terminal tab by typing:
```bash
source ~/.bashrc
```
- **Note**: This will deactivate the `gouhfi` virtual environment, don't forget to reactivate it before using GOUHFI!

### Step 7: Test the installation

- In your terminal, type:

```bash
run_gouhfi --help
```

- **Note**: Remember to reactivate your GOUHFI virtual environment after sourcing the `.bashrc` file.
- If you see the help function for `run_gouhfi` (or any other functions related to GOUHFI described [below](#usage)), you have installed the repository properly. Congrats and happy segmenting! :)

---


## Usage

- **Reminder**: All these functions need to be executed inside your virtual environment.
- **Tip**: A few test images are provided for testing the different command lines below in the `$GOUHFI_HOME/test_data` directory. 
    - Feel free to replace the `-i/--input_dir` argument in the usage examples below with eiher one of the following:
        - `$GOUHFI_HOME/test_data/input-images-lia-brain-extracted/single-sub`; 
        - `$GOUHFI_HOME/test_data/input-images-lia-brain-extracted/all-subs`; 
        - `$GOUHFI_HOME/test_data/input-images-raw`.

### `run_gouhfi`: 

- This is the command to obtain the whole brain segmentation into 35 labels from GOUHFI.
    - The command `run_gouhfi` is used to (1) run the inference (i.e., segment your images using the trained model), (2) apply the post-processing step and (3), if desired, reorder the label values in the segmentations produced from GOUHFI (optional). 
        - More precisely, the third step changes GOUHFI's lookuptable (LUT) (i.e., label values from 0 to 35) to the FreeSurfer LUT which is commonly used by the neuroimaging community. 
- We strongly recommend to use a GPU to run the inference (anything with >8 Gb of VRAM should be strong enough, but not officially tested). CPU can be used but expect a considerable increased in computation time (e.g., ca. ~10 sec/subject on GPU and can be roughly ~75 times longer or even more on the CPU depending on the setup).

- **Note**: **Before** running the example command line below, remember that the images to be segmented need to (1) be preprocessed (i.e., conformed + brain extraction, see [this](#run_preprocessing)) and (2) renamed to the nnUNet naming convention (see [that](#run_renaming)).

Example command line:

```bash
run_gouhfi -i /path/to/input_data -o /path/to/output_dir [--np N] [--folds "0 1 2 3 4"] [--reorder_labels] [--cpu]
```

### Arguments

| Argument              | Type    | Default                                                              | Description                                                                                |
|-----------------------|---------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`   | `str`   | **Required**                                                         | Path to the directory containing input `.nii.gz` files.                                    |
| `-o`, `--output_dir`  | `str`   | Derived from `input_dir` as `../outputs/`                            | Directory where the segmentations will be saved.                                            |
| `--np`                | `int`   | `4`                                                                  | Number of parallel CPU processes to use during post-processing.                            |
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
    - Preprocessed --> conformed + brain-extracted (see [this](#run_preprocessing) for both steps combined into one)
        - Each preprocessing step can be run individually if desired with the following two scripts for [conforming](#run_conforming) and [brain extraction](#run_brain_extraction).


#### Outputs

File:
- `{SUBJECT_ID}.nii.gz` —> Segmentation/Label map for the `{SUBJECT_ID}` subject.

Segmentation/Label map:
- The labels are linearly ordered from 0 (background) to 35 by default if not reordered as described above. The complete list of labels is shown in file [misc/gouhfi-label-list-lut.txt](https://github.com/mafortin/GOUHFI/blob/main/misc/gouhfi-label-list-lut.txt).
- As for **any** automatic segmentation tool, we recommend the user to visually inspect the quality of the segmetation outputs produced by GOUHFI.
   - While the technique has been extensively tested, it may still have unknown limitations. We kindly encourage users to report any issues or unexpected behavior to help guide future improvements and development.
   - Keep in mind that GOUHFI is a research tool, not a clinically-approved diagnostic tool for patients on an indiviudal basis.

---

### `run_preprocessing`:

- The command `run_preprocessing` performs the full preprocessing pipeline required for GOUHFI in one go (i.e., reorienting to LIA + rescaling to 0-255 + brain extraction) for all `.nii` or `.nii.gz` images found in the specified input directory. You can customize both steps or skip brain extraction entirely.
    - *Note*: This is simply a convenient wrapper for running both `run_conforming` and `run_brain_extraction` in one step. If you prefer running them individually, please check the following two functions.

```bash
run_preprocessing -i /path/to/input_dir [-o /path/to/output_dir] [--modality t1] [--skip_morpho] [--dilation_voxels 0] [--rename] [--no_brain_extraction] [--orientation LIA] [--min 0] [--max 255] [--pmin 0.5] [--pmax 99.5]
```

#### Arguments

| Argument                  | Type      | Default                        | Description                                                                                                         |
|---------------------------|-----------|--------------------------------|---------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`       | `str`     | **Required**                   | Path to raw input images.                                                                                           |
| `-o`, `--output_dir`      | `str`     | *input_dir* + `_preproc`       | Directory to save preprocessed images. If not set, defaults to `input_dir` + `_preproc`.                            |
| `--modality`              | `str`     | `t1`                           | Modality for brain extraction (default: t1).                                                                        |
| `--skip_morpho`           | `flag`    | `True`                         | Skip morphological operations on the brain mask (default: True).                                                    |
| `--dilation_voxels`       | `int`     | `0`                            | Dilation radius in voxels for brain mask (default: 0).                                                              |
| `--rename`                | `flag`    | `False`                        | Rename brain-extracted files with '_masked' suffix.                                                                 |
| `--no_brain_extraction`   | `flag`    | `False`                        | Skip brain extraction step entirely.                                                                                |
| `--orientation`           | `str`     | `LIA`                          | Orientation for conforming step (default: LIA).                                                                     |
| `--min`                   | `float`   | `0`                            | Minimum value for intensity rescaling (default: 0). Can be any value.                                                                |
| `--max`                   | `float`   | `255`                          | Maximum value for intensity rescaling (default: 255). Can be any value.                                                               |
| `--pmin`                  | `float`   | `0.5`                          | Lower percentile for intensity rescaling (default: 0.5). If you already have brain-extracted images, could be a good idea to set to 0.1 instead (dataset-dependent).                                                           |
| `--pmax`                  | `float`   | `99.5`                         | Upper percentile for intensity rescaling (default: 99.5). If you already have brain-extracted images, could be a good idea to set to 99.9 instead (dataset-dependent).                                                          |

#### Input Requirements

- File format: compressed NIfTI (`.nii.gz`)
- Images should be placed in the input directory, not in subdirectories.

#### Outputs

- Preprocessed images saved in the specified output directory.
- If brain extraction is performed, output images will be skull-stripped and optionally renamed with the `_masked` suffix.

---

### `run_conforming`:

- The command `run_conforming` *conforms* all the `.nii` or `.nii.gz` images found in the specified input directory.
- This step reorients your images to the LIA orientation and rescales the voxel values between 0 and 255 (both steps are modifiable by passing a different value while running `run_conforming`).

```bash
run_conforming -i /path/to/input_dir [-o /path/to/output_dir] [-r LIA] [--min 0] [--max 255]
```

#### Arguments

| Argument             | Default                   | Description                                                                                                 |
|----------------------|---------------------------|-------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`  | -                         | Path to directory containing input NIfTI files (required).                                                  |
| `-o`, `--output_dir` | *input_dir*/`inputs-cfm/` | Directory to save the conformed images. If not set, defaults to `inputs-cfm` next to input.                 |
| `-r`, `--orientation`            | `LIA`         | Images need to be reoriented to LIA since it was trained in that orientation.             |
| `--min`            | 0               | Minimum value to use for rescaling voxel values.                          |
| `--max`        | 255                   | Maximum value to use for rescaling voxel values. |


---

### `run_brain_extraction`:


- The command `run_brain_extraction` brain-extracts/skull-strips all the `.nii` or `.nii.gz` images found in the specified input directory using `antspynet.brain_extraction` function.
- *Note*: We recommend the users to do this step as the final step before segmenting the images with GOUHFI to avoid unwanted non-zero voxels outside the brain (i.e., run `run_conforming` before this script).

```bash
run_brain_extraction -i /path/to/input_dir [-o /path/to/output_dir] [--modality t1] [--dilatation_voxels 2] [--skip_morpho] [--rename]
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


---

### `run_labels_reordering`:

- If you did not use the `--reorder_labels` flag when running `run_gouhfi`, you can reorder the labels using the `run_labels_reordering` command as shown below. 
- Once reordered, your label maps can be used in the same quantitative pipeline as label maps produced by *FreeSurfer*/*FastSurfer*.

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
run_renaming -i /path/to/input_dir -o /path/to/output_dir [--start_substring ./misc/gouhfi-label-list-lut.txt] [--end_substring ./misc/freesurfer-label-list-lut.txt] [--segms]
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

For the paper published in _Imaging Neuroscience_:
```
@article{fortin2025gouhfi,
    author = {Fortin, Marc-Antoine and Kristoffersen, Anne Louise and Larsen, Michael Staff and Lamalle, Laurent and Stirnberg, Rüdiger and Goa, Pål Erik},
    title = {GOUHFI: A novel contrast- and resolution-agnostic segmentation tool for ultra-high-field MRI},
    journal = {Imaging Neuroscience},
    volume = {3},
    pages = {IMAG.a.960},
    year = {2025},
    month = {10},
    issn = {2837-6056},
    doi = {10.1162/IMAG.a.960},
    url = {https://doi.org/10.1162/IMAG.a.960},
    eprint = {https://direct.mit.edu/imag/article-pdf/doi/10.1162/IMAG.a.960/2556634/imag.a.960.pdf},
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
