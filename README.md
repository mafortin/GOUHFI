# GOUHFI: novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI

The Generalized and Optimized segmentation tool for Ultra-High Field Images (GOUHFI) is a deep learning-based fully automatic brain segmentation tool optimized for ultra-high field MRI (i.e., ≥ 7T MRI). Using the domain randomization approach proposed in [SynthSeg](https://github.com/BBillot/SynthSeg), GOUHFI is able to segment images of any contrast, resolution and field strength, making it broadly applicable across scanners, imaging protocols and centers. 

![GOUHFI](figs/fig-readme.png)

---

## How was GOUHFI developed?

- ***MAF: TO BE DONE More detailed explanation of what we did? [long abstract style]***
- This repository is based on the nnUNet v2 framework and uses the same naming convention and requirements for running inference and postprocessing.
- Robust 3D U-Net model trained using [nnU-Net v2](https://github.com/MIC-DKFZ/nnUNet)
- Domain randomization for contrast and resolution generalization
- Validated on both UHF (7T) and standard 3T MRI
- Easy-to-use CLI for inference
- Fully open-source and Pythonic

---

## Installation

### Step 1: Create a Python virtual environment

- As for any Python project, we highly recommend you to install GOUHFI inside a virtual environment. Whether you use pip, anaconda or miniconda is up to you, but the steps below use conda. Relevant links related to [conda](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/) in general or [its installation](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html) for Ubuntu distributions (OS dependent).

- If you are using conda, you can use the following command: 
```bash
conda create --name gouhfi python=3.10 
```
- `gouhfi` in the above command line is the name of the virtual environment and can be replaced by anything else if preferred.
- Once your (empty) virtual environment is created, execute the following steps inside this virtual environment by typing:
```bash
conda activate gouhfi
```

### Step 2: Install PyTorch 

- Follow the instructions on the [PyTorch website](https://pytorch.org/get-started/locally/) to install the stable PyTorch version based on your OS, package manager, language (Python here) and compute platform (usually the latest CUDA is recommended).
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
cd /path/to/GOUHFI.zip
unzip GOUHFI.zip
```

- Once unzipped, you should have a folder called `Dataset014_gouhfi` with all trained folds and related files in the `trained_model` folder.


### Step 6: Test the installation

- In your terminal, type:

```bash
run_goufhi --help
```

- If you see the help function for `run_gouhfi`, you have installed the repository properly. Congrats and happy segmenting!

---


## Usage

### Run Inference

```bash
run_goufhi --input /path/to/input/folder/ --output path/to/output/folder/
```

| Argument  | Description                        |
|-----------|------------------------------------|
| `--input`  | Path to the directory containing the input image(s) to be segmented. |
| `--output` | Folder where the segmentations will be saved. |

- This command runs the model on your input image(s) and saves the corresponding output segmentations/label maps to the specified folder.
- Moreover, this command **needs** to be performed inside your newly created virtual python environment (see step 0 from [go to instllation](#installation)).

---

## Input Requirements

- File:
    - Format: compressed NIfTI (`.nii.gz`)
    - Naming convention: The nnUNet naming convention (i.e., `{CASE_IDENTIFIER}_0000.nii.gz`). More details [here](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md).
    - If you want to segment >1 image/subject, all images should be inside the input directory defined by `--input` under distinctive filenames. The output segmentations will follow the same naming convention as the input filenames minus the `_0000` string.  

- Image:
    - Contrast: Any
    - Resolution: Any (resampling to isotropic resolution is processed internally. Not tested for highly anisotropic images, but always worth a try.)
    - Orientation: LIA (like FastSurfer [see the `conform_images` command])

---

## Output

File:
- `{CASE_IDENTIFIER}.nii.gz` —> Segmentation result/Label map for the `{CASE_IDENTIFIER}` subject.

Segmentation/Label map:
- The labels are linearly ordered from 0 (background) to 35. The complete list of labels is shown in file `misc/label-list-lut.txt`.
    - **Tip**: If you have a version of [*FreeSurfer*](https://surfer.nmr.mgh.harvard.edu/fswiki) installed with *Freeview*, you can easily visualize the segmentation outputs overlaid on your input images. In order to visualize the segmentations wih the same color scheme/lookuptable as used by the *FreeSurfer/FastSurfer* team, simply copy the `label-list-lut.txt` inside your `$FREESURFER_HOME/luts/` folder (label values are not the same, but the colors will be). Then, this new lookuptable should be available in your Colormap/Lookuptable dropdown menu.

---

## Citation

If you use **GOUHFI** in your research, please cite the following:

For the paper:
```
@article{fortin2025gouhfi,
  title={GOUHFI: a novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI},
  author={Fortin, Marc-Antoine et al.},
  journal={Imaging Neuroscience},
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

## Third-Party softwares/librairies related to GOUHFI

This project incorporates code from the following projects, used under the Apache License 2.0:

Image preparation/preprocessing:
- [FastSurfer/FastSurferVINN](https://github.com/Deep-MI/FastSurfer):
    - In this project, the script `conform.py` from FastSurfer/FastSurferVINN was used for 'conforming' the images to be segmented by GOUHFI (i.e., reorienting to LIA, resampling to isotropic resolution and normalizing signal values between 0 and 255). The script has been used as is, without modification, and is shared as part of the GOUHFI repository to make the repository more self-contained. If you have an already up and running FastSurfer installation, you can use it directly from there. In this repository, the function `run_conforming` will execute this script.
- [ANTsPyNet](https://github.com/ANTsX/ANTsPyNet):
    - For brain extraction. Quick and efficient brain extraction tool (`antspynet.brain_extraction`) if you need to do this for your images to be segmented. We provide a script called `brain_extraction_antspynet.py` where we wrapped an unmodified implementation of `antspynet.brain_extraction` to make the repository more self-contained. If you have an already up and running ANTsPyNet installation, you can use it directly from there. In this repository, the function `run_brain_extraction` will execute this script.

Retraining:
- [nnU-Net v2](https://github.com/MIC-DKFZ/nnUNet):
    - The nnUNet v2 framework was used for training, inference, post-processing and evaluation of GOUHFI. When you are installing GOUHFI as explained above in this README file, you should have all the required nnUNet functions to run inference, post-processing and evaluation as done by the nnUNet. However, if you would like to reproduce the full training as explained in the related paper, you would need a full local installation of the nnUNet, which is not provided by this repository. See the [nnUNet installation documentation](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/installation_instructions.md) for more information on how to proceed.

Generating synthetic images for training:
- [SynthSeg](https://github.com/BBillot/SynthSeg):
    - The synthetic images used to train GOUHFI were generated from the generative model proposed in SynthSeg. The generative model parameters used are described in the appendices of the paper related to this repository. 

---

## Maintainer

Marc-Antoine Fortin  
Norwegian University of Science and Technology (NTNU)  
Contact: [marc.a.fortin@ntnu.no](mailto:marc.a.fortin@ntnu.no)