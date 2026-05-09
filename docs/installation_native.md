# Native Installation (conda + pip)

This guide walks through installing GOUHFI directly in a Python virtual environment. If you would rather use Docker (no Python setup required), see [`installation_docker.md`](installation_docker.md).

GOUHFI has been successfully installed on Linux (Ubuntu), macOS, and Windows.

---

## Step 1: Create a Python virtual environment

We strongly recommend installing GOUHFI inside a virtual environment. The steps below use conda ([installation guide](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html)).

```bash
conda create --name gouhfi python=3.10
conda activate gouhfi
```

The name `gouhfi` can be replaced by anything you prefer.

---

## Step 2: Install PyTorch

Inside your activated environment:

```bash
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --index-url https://download.pytorch.org/whl/cu121
```

> **Note**: GOUHFI was tested with CUDA 11.8 and 12.1 and PyTorch 2.1.2. Other versions have not been tested.

---

## Step 3: Clone and install the repository

```bash
cd /path/where/you/want/GOUHFI
git clone https://github.com/mafortin/GOUHFI.git
cd GOUHFI
pip install -e .
```

The `-e` (editable) flag lets you modify the scripts if needed. If you do not have `git`, download the ZIP from the green `< > Code` button on GitHub, extract it, and run `pip install -e .` from inside the extracted folder.

---

## Step 4: Download the trained model weights

The weights are available from Zenodo (official archival release) and Hugging Face (mirror):

- **Zenodo**: https://zenodo.org/records/17920473
- **Hugging Face**: https://huggingface.co/mafortin/GOUHFI2p0

Download all three `.zip` archives:

| File | Description |
|---|---|
| `gouhfi_2p0_brain_seg.zip` | GOUHFI 2.0 subcortical segmentation |
| `gouhfi_2p0_parc.zip` | GOUHFI 2.0 cortical parcellation |
| `GOUHFI.zip` | Original GOUHFI 1.0 subcortical segmentation |

Move the three `.zip` files into the `trained_model/` folder.

---

## Step 5: Unzip the model weights

```bash
cd trained_model/
unzip '*.zip'
```

After unzipping you should have three folders:
- `Dataset014_gouhfi` — GOUHFI 1.0 subcortical segmentation
- `Dataset020_gouhfi_2p0n2` — GOUHFI 2.0 subcortical segmentation
- `Dataset024_gouhfi_parc` — GOUHFI 2.0 cortical parcellation

> **Notes**:
> - Each model is ~7 GB; this step may take 6–7 minutes.
> - If you used your OS file manager to extract the ZIPs, it may have created an extra `GOUHFI/` subfolder. If so, manually move the three `Dataset*` directories back into `trained_model/`.

---

## Step 6: Set the `GOUHFI_HOME` environment variable

GOUHFI needs to know where it is installed. Add the following line to your `~/.bashrc` (Linux) or `~/.zshrc` (macOS):

```bash
export GOUHFI_HOME="/full/path/to/GOUHFI"
```

Then apply the change:

```bash
source ~/.bashrc
```

> **Note**: `source ~/.bashrc` deactivates your conda environment — remember to run `conda activate gouhfi` again before using GOUHFI.
>
> For other shell types or Windows, refer to the [nnUNet environment variable guide](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md) and adapt for `GOUHFI_HOME`.

---

## Step 7: Test the installation

```bash
run_gouhfi --help
```

If the help text appears, you are ready to go. See [`usage.md`](usage.md) for the full command reference.
