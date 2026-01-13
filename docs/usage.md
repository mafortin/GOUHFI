## Usage

- This page contains the full command-line reference for GOUHFI, including the main segmentation/parcellation pipeline (`run_gouhfi`) and helper tools for preprocessing, renaming, label-map manipulation, and volumetry. Each section includes a short description, an example command, and an argument table. 
- **Reminder**: All commands must be run inside your activated Python environment (e.g., `conda activate gouhfi`). 
- **Tip**: For quick testing, example images are provided in `$GOUHFI_HOME/test_data/`.
    - Feel free to replace the `-i/--input_dir` argument in the usage examples below with eiher one of the following:
        - `$GOUHFI_HOME/test_data/input-images-lia-brain-extracted/single-sub`; 
        - `$GOUHFI_HOME/test_data/input-images-lia-brain-extracted/all-subs`; 
        - `$GOUHFI_HOME/test_data/input-images-raw`.

---

### `run_gouhfi`: 

- This is the core command of this repository to obtain (a) the whole brain subcortical segmentation into 35 labels and (b) cortical parcellation from GOUHFI 2.0.
    - The command `run_gouhfi` is used to (1) run the inference (i.e., segment your images using the trained models), (2) apply the post-processing step and (3), if desired, reorder the label values in the segmentations produced from GOUHFI (optional). 
        - More precisely, the third step changes GOUHFI's lookuptable (LUT) to the more frequentely used FreeSurfer LUT in the neuroimaging community. 
- We strongly recommend to use a GPU to run the inference (anything with >8 Gb of VRAM should be strong enough, but not officially tested). CPU can be used but expect a considerable increased in computation time (e.g., ca. ~10 sec/subject on GPU and can be roughly ~100 times longer or even more on the CPU depending on the setup).

- **Note**: **Before** running the example command line below, remember that the images to be segmented need to (1) be preprocessed (i.e., conformed + brain extraction, see [this](#run_preprocessing)) and (2) renamed to the nnUNet naming convention (see [that](#run_renaming)).

Example command line:

```bash
run_gouhfi -i /path/to/input_data -o /path/to/output_dir [--np N] [--folds "0 1 2 3 4"] [--v1] [--skip_parc] [--skip_seg] [--reorder_labels] [--cpu]
```


| Argument              | Type    | Default                                                              | Description                                                                                |
|-----------------------|---------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`   | `str`   | **Required**                                                         | Path to the directory containing input `.nii.gz` files.                                    |
| `-o`, `--output_dir`  | `str`   | Derived from `input_dir` as `../outputs/`                            | Directory where the segmentations will be saved.                                            |
| `--np`                | `int`   | `4`                                                                  | Number of parallel CPU processes to use during post-processing.                            |
| `--folds`             | `str`   | `"0 1 2 3 4"`                                                        | Space-separated string of folds to use for inference (we recommend to use all).            |
| `--reorder_labels`    | `flag`  | `False`                                                              | If set, reorders label values from GOUHFI's LUT to FreeSurfer's LUT after post-processing. |
| `--cpu`               | `flag`  | `False`                                                              | If set, the cpu will be used instead of the GPU for running the inference.                 |
| `--skip_parc`               | `flag`  | `False`                                                              | If set, the cortical parcellation step will be skipped.                 |
| `--skip_seg`               | `flag`  | `False`                                                              | If set, the subcortical segmentation step will be skipped. Note: The user is then responsible to provide cortex segmentation isolated (see command [`run_label_modif`](#run_label_modif) below).                 |
| `--v1`               | `flag`  | `False`                                                              | If set, the original GOUHFI subcortical segmentation model will be used (doesn't apply to cortical parcellation).                 |

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

Files:
- `$OUTPUT_DIR/outputs_seg[parc]/{SUBJECT_ID}.nii.gz` —> Not postprocessed subcortical segmentation/cortical parcellation for the `{SUBJECT_ID}` subject.
- `$OUTPUT_DIR/outputs_seg[parc]_postpro/{SUBJECT_ID}.nii.gz` —> Postprocessed subcortical segmentation/cortical parcellation for the `{SUBJECT_ID}` subject.
    - **Note**: The postprocessed segmentations/parcellations are the ones to use for analyses.

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


| Argument               | Default        | Description                                                                                                                                                 |
|------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-i`, `--input_dir`    | -              | Path to the input directory containing files to rename (required).                                                                                          |
| `-o`, `--output_dir`   | *input_dir*    | Path to the output directory to save the renamed files and JSON correspondence file. Defaults to same as input directory.                                   |
| `--start_substring`    | `sub`          | Substring that marks the beginning of the subject ID within filenames. If omitted along with `--end_substring`, the full filename (minus extension) is used. |
| `--end_substring`      | `_`            | Substring that marks the end of the subject ID within filenames. See `--start_substring` for default behavior if omitted.                                   |
| `--segms`              | -              | Use this flag if the files are label maps. The renamed files will **not** include the `_0000` suffix.                                                       |

- **Note**: A `subject_id_correspondence.json` file will be created and saved in `input_dir` to keep tract of the correspondence between the old and new filenames.

---
### `run_label_modif`:

- Useful helper function to modify label maps in general. We are sharing it simply because it has been quite helpful for the development of GOUHFI, so we wanted to make it accessible to the coomunity! :) 
- However, this command is **not required** at any stage of the pipeline and can be ignored if you are not interested in modifying label maps. 
- Briefly, it can filter labels (keep only specific labels, or filter by keeping only the labels above/below a defined value), merge all individual cortex labels into one left- and right-hemisphere FreeSurfer-LUT cortex IDs (i.e., all 1000s -> 3 and all 2000s -> 42), set all labels to 1, reindex labels (from 1 -> N), and optionally rename outputs to nnUNet naming convention by appending `_0000`.

```bash
run_label_modif --input /path/to/input_dir --output /path/to/output_dir 
  [--keep-labels 3 42] [--min-label N] [--max-label N] \
  [--combine-ctx] [--set-to-one all|<label_ids...>] [--reindex] \
  [--prep4ctx] [--num-workers N]
```

| Argument        | Default | Description                                                                                                                |
| --------------- | ------: | -------------------------------------------------------------------------------------------------------------------------- |
| `--input`       |       - | Path to directory containing input label maps (`.nii` / `.nii.gz`) (required).                                             |
| `--output`      |       - | Directory to save processed label maps (required).                                                                         |
| `--keep-labels` |       - | List of label IDs to keep (all others are set to 0).                                                                       |
| `--min-label`   |       - | Minimum label value to keep (values below are set to 0).                                                                   |
| `--max-label`   |       - | Maximum label value to keep (values above are set to 0).                                                                   |
| `--combine-ctx` | `False` | Combine cortex labels: 1000–1999 → `3` (LH cortex) and 2000–2999 → `42` (RH cortex).                                       |
| `--set-to-one`  |       - | Set labels to 1. Use `all` to set all non-zero labels to 1, or provide specific label IDs.                                 |
| `--reindex`     | `False` | Reindex remaining non-zero labels to `1..N` (preserves background 0).                                                      |
| `--prep4ctx`    | `False` | Ensure output filenames follow nnUNet single-channel convention by appending `_0000` before `.nii`/`.nii.gz` (if missing). |
| `--num-workers` |     `4` | Number of parallel workers for processing files.                                                                           |

- Output:
    - Modified label maps in `--output`.

---

### `run_vol_extraction`:

- The command `run_vol_extraction` computes volumetry from all `.nii`/`.nii.gz` label maps found inside a directory.
- It outputs a CSV containing per-label absolute volumes (mm³) and normalized volumes:
    - `brain`: normalized by TIV (total intracranial volume) and brain volume (BV) (brain volume = TIV − CSF)
    - `cortex`: normalized by cortex volume (CV)
- A label lookup table is used to map label IDs to names. If not provided, GOUHFI defaults are used.

```bash
run_vol_extraction -i /path/to/input_dir [-o /path/to/output_dir]
  -t brain|cortex [-l /path/to/label_lut.txt] [-d DATASET_ID]
```

| Argument             |            Default | Description                                                                                                                                                                                  |
| -------------------- | -----------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-i`, `--input_dir`  |                  - | Directory containing `.nii` / `.nii.gz` label maps (required).                                                                                                                               |
| `-o`, `--output_dir` |        *input_dir* | Directory to save the output CSV. If not set, defaults to the input directory.                                                                                                               |
| `-t`, `--task`       |                  - | Segmentation task: `brain` or `cortex` (required).                                                                                                                                           |
| `-l`, `--label_file` | GOUHFI default LUT | Optional label mapping `.txt` file. If not provided: `brain` uses `$GOUHFI_HOME/misc/gouhfi_v2p0_brain_labels_lut.txt`, `cortex` uses `$GOUHFI_HOME/misc/gouhfi_v2p0_cortex_labels_lut.txt`. |
| `-d`, `--dataset_id` |               `""` | Optional dataset ID appended to the output filename.                                                                                                                                         |

- Output:
    - Produces a CSV named:
        - `volumetry_brain[_DATASET_ID].csv` or;
        - `volumetry_cortex[_DATASET_ID].csv`
    - Saved in `--output_dir` (or `input_dir` if `--output_dir` is not set).

---

### `run_add_label`:

- **Note**: Since GOUHFI 2.0, this is less relevant since we moved away from the 'Extra-Cerebral' label approach. For legacy reasons, we will keep it here if someone would stil like to use it.
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
