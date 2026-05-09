# GOUHFI: novel contrast- and resolution-agnostic segmentation tool for Ultra-High Field MRI

[![Paper](https://img.shields.io/badge/Paper-Imaging%20Neuroscience-green)](https://doi.org/10.1162/IMAG.a.960)
[![arXiv](https://img.shields.io/badge/arXiv-2601.09006-b31b1b)](https://arxiv.org/abs/2601.09006)
[![Zenodo](https://img.shields.io/badge/Model-Zenodo-blue)](https://doi.org/10.5281/zenodo.17920473)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-HuggingFace-yellow)](https://huggingface.co/mafortin/GOUHFI2p0)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE)

Welcome to **GOUHFI 2.0**, a novel deep learning (DL) toolbox for subcortical segmentation, cortical parcellation and volumetry of brain MR images of **any contrast, resolution and field strength**.

This README provides a project overview with links to the full [Installation](#installation) and [Usage](#usage) documentation. 

Helper commands for neuroscientists/neuroimagers working with label maps are also documented in **[`docs/usage.md`](docs/usage.md)**.

---

## Updates

- 09/05/26: **GOUHFI 2.0.1: Docker support added!**
  - In order to make GOUHFI more accessible to the community, we made a Docker implementation for GOUHFI. That way, GOUHFI can now be run without any Python setup using only a few installation steps. See **[`docs/installation_docker.md`](docs/installation_docker.md)** for the full guide.
- 13/12/25: **GOUHFI 2.0** is finally available!
    - In addition of an improved subcortical segmentation tool on clinical cohorts, GOUHFI 2.0 now also offers (a) contrast-, resolution- and field-agnostic cortex parcellation following the Desikan-Killiany-Tourville (DKT) atlas and (b) Total Intracranial Volume (TIV) estimations for normalized volumetry analyses.
    - The related arXiv publication for GOUHFI 2.0 is available [here](https://doi.org/10.48550/arXiv.2601.09006).
- 29/09/25: 🎉 **GOUHFI's paper has been accepted for publication in the _Imaging Neuroscience_ journal!** 🎉 The accepted version is available online [here](https://direct.mit.edu/imag/article/doi/10.1162/IMAG.a.960/133411/GOUHFI-a-novel-contrast-and-resolution-agnostic).

---

## How was GOUHFI developed?

GOUHFI is a fully automatic, contrast- and resolution-agnostic, DL-based brain segmentation tool optimized for Ultra-High Field MRI (UHF-MRI), while also demonstrating strong performance at 1.5T/3T compared to other well-established techniques.

Using the domain randomization approach proposed in [SynthSeg](https://github.com/BBillot/SynthSeg) and a state-of-the-art 3D U-Net with Residual Encoders from the [nnUNetv2](https://github.com/MIC-DKFZ/nnUNet) framework, GOUHFI is able to handle various contrasts, resolutions and even field strengths without requiring fine-tuning or retraining. Tested on multiple datasets, it showed high accuracy and impressive robustness to noise and inhomogeneities, making it a valuable tool for neuroscientists working at both 3T and UHF-MRI.

For more details on how GOUHFI was developed, please refer to the corresponding [paper](https://direct.mit.edu/imag/article/doi/10.1162/IMAG.a.960/133411/GOUHFI-a-novel-contrast-and-resolution-agnostic) published in Imaging Neuroscience.

More recently, we released a major update under the name **GOUHFI 2.0**. This new version retains the original subcortical segmentation approach, based on the same domain randomization principles, but benefits from an improved and expanded training dataset. In addition, **GOUHFI 2.0** introduces cortical parcellation and Total Intracranial Volume (TIV) estimation, enabling independent normalized volumetric analyses. Further details about the development of GOUHFI 2.0 are provided in the corresponding [ArXiv publication](https://arxiv.org/abs/2601.09006).

![GOUHFI](figs/fig-readme.png)

---

## Installation

Two installation methods are available:

| Method | Best for | Guide |
|---|---|---|
| **Docker** | Most users who just want to segment their images. Easiest, no Python knowledge  required | [`docs/installation_docker.md`](docs/installation_docker.md) |
| **Native (conda + pip)** | Developers or users who want to modify the code | [`docs/installation_native.md`](docs/installation_native.md) |

Both methods require the user to download the trained model weights from [Zenodo](https://zenodo.org/records/17920473) or [Hugging Face](https://huggingface.co/mafortin/GOUHFI2p0) (~7 GB each, 3 models in total).

---

## Usage

GOUHFI is operated through command-line tools (`run_gouhfi`, `run_preprocessing`, `run_renaming`, etc.).

The full command reference and detailed examples are in **[`docs/usage.md`](docs/usage.md)**.

### Quick start (minimum pipeline)

**Native installation:**
```bash
conda activate gouhfi
run_preprocessing -i /path/to/raw_images -o /path/to/preprocessed
run_renaming -i /path/to/preprocessed -o /path/to/renamed
run_gouhfi -i /path/to/renamed
```

**Docker (GPU):**
```bash
docker run --gpus all --rm --shm-size=16g \
  -e HOST_UID=$(id -u) -e HOST_GID=$(id -g) \
  -v /path/to/weights:/opt/gouhfi/trained_model:ro \
  -v antspynet-cache:/opt/keras-cache \
  -v /path/to/input:/input -v /path/to/output:/output \
  gouhfi:2.0.1 run_gouhfi -i /input -o /output
```

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
            - You can create synthetic images for label maps containing the 'Extra-Cerebral' label (see [run_add_label](docs/usage.md#run_add_label) for how to perform this).
    - More details about the generative model can be found in the [brain_generator.py](https://github.com/BBillot/SynthSeg/blob/master/SynthSeg/brain_generator.py) script and questions about the generative model should be addressed to the [SynthSeg team](https://github.com/BBillot/SynthSeg).

---

## Citation

If you use **GOUHFI** in your research, please cite the following:

### Papers:

- For the original GOUHFI paper published in _Imaging Neuroscience_:
```
Marc-Antoine Fortin, Anne Louise Kristoffersen, Michael Staff Larsen, Laurent Lamalle, Rüdiger Stirnberg, Pål Erik Goa; GOUHFI: A novel contrast- and resolution-agnostic segmentation tool for ultra-high-field MRI. Imaging Neuroscience 2025; 3 IMAG.a.960. doi: https://doi.org/10.1162/IMAG.a.960
```
- Bibtex entry:
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

- For GOUHFI 2.0, currently on ArXiV:
```
Marc-Antoine Fortin, Anne Louise Kristoffersen, Pål Erik Goa; GOUHFI 2.0: A Next-Generation Toolbox for Brain Segmentation and Cortex Parcellation at Ultra-High Field MRI. ArXiv. doi: https://doi.org/10.48550/arXiv.2601.09006
```
- Bibtex entry:
```
@misc{fortin2026gouhfi,
  title         = {GOUHFI 2.0: A Next-Generation Toolbox for Brain Segmentation and Cortex Parcellation at Ultra-High Field MRI},
  author        = {Fortin, Marc-Antoine and Kristoffersen, Anne Louise and Goa, Paal Erik},
  year          = {2026},
  eprint        = {2601.09006},
  archivePrefix = {arXiv},
  primaryClass  = {eess.IV},
  doi           = {10.48550/arXiv.2601.09006},
  url           = {https://arxiv.org/abs/2601.09006}
}
```

### Models:

- For the original GOUHFI subcortical segmentation model:
```
@misc{fortin2025gouhfi,
  author       = {Fortin, M.-A. and Larsen, M. and Kristoffersen, A. L. and Goa, P. E.},
  title        = {GOUHFI: Generalized and Optimized segmentation tool for Ultra-High Field Images},
  year         = {2025},
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.15255556},
  url          = {https://doi.org/10.5281/zenodo.15255556}
}
```

- For GOUHFI 2.0 subcortical segmentation and/or cortical parcellation models:
```
@misc{fortin2025gouhfi_2p0,
  author       = {Fortin, M.-A. and Larsen, M. and Kristoffersen, A. L. and Goa, P. E.},
  title        = {GOUHFI 2.0: Generalized and Optimized segmentation tool for Ultra-High Field Images},
  year         = {2025},
  publisher    = {Zenodo},
  version      = {2.0.0},
  number       = {3},
  doi          = {10.5281/zenodo.17920473},
  url          = {https://doi.org/10.5281/zenodo.17920473}
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
