# GOUHFI: novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI

**GOUHFI** is a deep learning-based fully automatic brain segmentation tool optimized for ultra-high field MRI (i.e., ≥ 7T MRI). Using the domain randomization approach proposed in [SynthSeg](https://github.com/BBillot/SynthSeg), GOUHFI is able to segment images of any contrast, resolution and field strength, making it broadly applicable across scanners, imaging protocols and centers. 

---

## How was GOUHFI developed?

- ***MAF: More detailed explanation of what we did? [long abstract style]***
- This repository is based on the nnUNet v2 framework and uses the same naming convention and requirements for running inference and postprocessing.
- Robust 3D U-Net model trained using [nnU-Net v2](https://github.com/MIC-DKFZ/nnUNet)
- Domain randomization for contrast and resolution generalization
- Validated on both UHF (7T) and standard 3T MRI
- Easy-to-use CLI for inference
- Fully open-source and Pythonic

---

## Installation


### Step 1: Install PyTorch 

- Follow the instructions on the [PyTorch website](https://pytorch.org/get-started/locally/).
- This step **has** to be done **before** step 2 below as recommended by the nnUNet team [step #1 here](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/installation_instructions.md#installation-instructions).

### Step 2: Install the repository locally

#### Option 1: Install Directly from GitHub (Recommended)

```bash
pip install git+https://github.com/mafortin/GOUHFI.git
```

This installs the `run_goufhi` command line tool.

---

#### Option 2: Clone and Install Locally

```bash
git clone https://github.com/mafortin/GOUHFI.git
cd GOUHFI
pip install -e .
```

### Step 3: Download the trained model weights from Zenodo

A Zenodo link to the trained model weights is included in the repository under `trained_model/` subdirectory or simply with this [link](https://zenodo.org/records/15255556).

### Step 4: 

---

## Usage

### Run Inference

```bash
run_goufhi --input /path/to/image.nii.gz --output /output/folder/ [--conform]
```

| Argument  | Description                        |
|-----------|------------------------------------|
| `--input`  | Path to the directory containing the input image(s) to be segmented. |
| `--output` | Folder where the segmentations will be saved. |

This command runs the model on your input image and saves the output segmentation mask to the specified folder.

---

## Input Requirements

- File:
    - Format: NIfTI (`.nii or .nii.gz`)
    - Naming convention: The nnUNet naming convention (i.e., `{CASE_IDENTIFIER}_0000.nii.gz`). More details [here](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md).
    - If you want to segment >1 image/subject, all images should be inside the input directory defined by `--input` under distinctive filenames. The output segmentations will follow the same naming convetion as the input filenames minus the `_0000` string.  

- Image:
    - Contrast: Any
    - Resolution: Any (resampling to isotropic resolution is processed internally. Not tested for highly anisotropic images, but always worth a try.)
    - Orientation: LIA (like FastSurfer [see the `conform_images` command])

---

## Output

- `{CASE_IDENTIFIER}.nii.gz` — Segmentation results for the `{CASE_IDENTIFIER}` subject (i.e., subcortical segmentation of the brain into 35 labels).

---

## Dependencies

The following dependencies are installed automatically when using pip:

- `torch` (PyTorch)
- `nibabel`
- `scipy`
- `nnunetv2`
- `antspynet`




---

## Citation

If you use **GOUHFI** in your research, please cite the following:

```
@article{fortin2025gouhfi,
  title={GOUHFI: a novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI},
  author={Fortin, Marc-Antoine et al.},
  journal={Imaging Neuroscience},
  year={2025}
}
```

---

## Contributing

We welcome contributions. If you find bugs, have suggestions, or would like to extend the tool, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.

---

## Related Projects

- [nnU-Net v2](https://github.com/MIC-DKFZ/nnUNet)
    - For the training, inference, post-processing and evaluation of the 3D U-Net.
- [SynthSeg](https://github.com/BBillot/SynthSeg)
    - For the generative model to create synthetic images for training.
- [FastSurfer](https://github.com/Deep-MI/FastSurfer)
    - For the conforming step of images to be segmented.
- [ANTsPyNet](https://github.com/ANTsX/ANTsPyNet)
    - For brain extraction.

---

## Maintainer

Marc-Antoine Fortin  
Norwegian University of Science and Technology (NTNU)  
Contact: [marc.a.fortin@ntnu.no](mailto:marc.a.fortin@ntnu.no)