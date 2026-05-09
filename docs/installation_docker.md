# Docker Installation

Docker packages all of GOUHFI's software dependencies into a self-contained image. You do not need Python, conda, or any manual environment setup — just Docker and the model weights.

If you prefer a native Python install instead, see [`installation_native.md`](installation_native.md).

---

## Prerequisites

- A Linux, macOS, or Windows machine
- An NVIDIA GPU with ≥8 GB VRAM is **strongly recommended** (inference is ~100× faster than CPU)
- The three GOUHFI model weight archives downloaded from Zenodo or Hugging Face (see [Step 3](#step-3-download-the-model-weights))

---

## Step 1: Install Docker

Follow the official Docker installation guide for your operating system:

- **Linux (Ubuntu/Debian)**: https://docs.docker.com/engine/install/ubuntu/
- **macOS**: https://docs.docker.com/desktop/install/mac-install/
- **Windows**: https://docs.docker.com/desktop/install/windows-install/

On Linux, the quickest install is:

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
```

Verify the installation:

```bash
docker run hello-world
```

> **Troubleshooting — `permission denied` when running docker commands**:  
> This means your user is not yet in the `docker` group. Run `newgrp docker` to apply the change in your current shell, or log out and back in to apply it permanently.

---

## Step 2: Install the NVIDIA Container Toolkit (GPU users only)

Skip this step if you have no NVIDIA GPU or plan to run on CPU only.

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify that Docker can see your GPU:

```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

Your GPU should appear in the output.

---

## Step 3: Download the model weights

The trained model weights are **not** included in the Docker image and must be downloaded separately.

Download all three `.zip` archives from Zenodo or Hugging Face:

- **Zenodo**: https://zenodo.org/records/17920473
- **Hugging Face**: https://huggingface.co/mafortin/GOUHFI2p0

| File | Description |
|---|---|
| `gouhfi_2p0_brain_seg.zip` | GOUHFI 2.0 subcortical segmentation |
| `gouhfi_2p0_parc.zip` | GOUHFI 2.0 cortical parcellation |
| `GOUHFI.zip` | Original GOUHFI 1.0 subcortical segmentation |

Unzip all three archives into a single directory on your machine (e.g. `/data/gouhfi_weights/`):

```bash
cd /data/gouhfi_weights/
unzip '*.zip'
```

After unzipping you should have three folders inside that directory:
- `Dataset014_gouhfi`
- `Dataset020_gouhfi_2p0n2`
- `Dataset024_gouhfi_parc`

---

## Step 4: Pull the Docker image

Pull the pre-built image directly from Docker Hub — no cloning or building required:

```bash
docker pull mafortin30/gouhfi:2.0.1
```

> **CPU-only users**: pull the CPU image instead:
> ```bash
> docker pull mafortin30/gouhfi:2.0.1-cpu
> ```

This downloads all Python dependencies pre-installed inside the image (~9 GB for GPU, ~1.2 GB for CPU). You only need to do it once.

---

## Step 5: Test the installation

```bash
docker run --rm mafortin30/gouhfi:2.0.1 run_gouhfi --help
```

If the help text appears, the image is working correctly.

---

## Quick start

Replace `/data/gouhfi_weights`, `/data/input`, and `/data/output` with your actual paths.

**GPU (recommended):**

```bash
docker run \
  # ── Docker configuration ──────────────────────────────────────────
  --gpus all \                              # pass NVIDIA GPU into container
  --rm \                                    # delete container when done
  --shm-size=16g \                          # shared memory for nnUNet workers
  -e HOST_UID=$(id -u) \                   # output files will be owned by you
  -e HOST_GID=$(id -g) \                   # output files will be owned by you
  -v /data/gouhfi_weights:/opt/gouhfi/trained_model:ro \  # model weights (read-only)
  -v antspynet-cache:/opt/keras-cache \    # ANTsPyNet weight cache (persistent)
  -v /data/input:/input \                  # your input NIfTI files
  -v /data/output:/output \               # where segmentations will be saved
  # ── Image and command ─────────────────────────────────────────────
  mafortin30/gouhfi:2.0.1 \
  run_gouhfi -i /input -o /output
```

**CPU only:**

```bash
docker run \
  # ── Docker configuration ──────────────────────────────────────────
  --rm \                                    # delete container when done
  --shm-size=16g \                          # shared memory for nnUNet workers
  -e HOST_UID=$(id -u) \                   # output files will be owned by you
  -e HOST_GID=$(id -g) \                   # output files will be owned by you
  -v /data/gouhfi_weights:/opt/gouhfi/trained_model:ro \  # model weights (read-only)
  -v antspynet-cache:/opt/keras-cache \    # ANTsPyNet weight cache (persistent)
  -v /data/input:/input \                  # your input NIfTI files
  -v /data/output:/output \               # where segmentations will be saved
  # ── Image and command ─────────────────────────────────────────────
  mafortin30/gouhfi:2.0.1-cpu \
  run_gouhfi -i /input -o /output --cpu
```

Every command available in the native installation like `run_gouhfi`, `run_preprocessing`, `run_renaming`, `run_brain_extraction`, `run_volumetry`, with all their flags, works identically inside Docker. Simply replace the native command with the equivalent `docker run ... mafortin30/gouhfi:2.0.1 <command>` call. See [`usage.md`](usage.md) for the full command reference.

---

## ANTsPyNet brain extraction (preprocessing)

The `run_preprocessing` and `run_brain_extraction` commands use ANTsPyNet, which downloads its own brain extraction weights on **first use** (requires internet, ~300 MB). After that first run the weights are cached in the `antspynet-cache` Docker volume and no internet access is needed.

```bash
docker run \
  # ── Docker configuration ──────────────────────────────────────────
  --rm \
  --shm-size=16g \
  -e HOST_UID=$(id -u) \
  -e HOST_GID=$(id -g) \
  -v antspynet-cache:/opt/keras-cache \    # cache persists between runs
  -v /data/raw_images:/input \
  -v /data/preprocessed:/output \
  # ── Image and command ─────────────────────────────────────────────
  mafortin30/gouhfi:2.0.1 \
  run_preprocessing -i /input -o /output   # internet required on first run only
```

---

## Troubleshooting

- **`Background workers died` / `RuntimeError`**
  - nnUNet's multiprocessing workers need more shared memory than Docker's 64 MB default.
  - Fix: always pass `--shm-size=16g` to `docker run` (already set in `docker-compose.yml`).
  - If it still fails with very large datasets, try increasing to `--shm-size=32g`.

- **`permission denied while trying to connect to the Docker API`**
  - Your current shell session does not have the `docker` group active yet.
  - Fix: run `newgrp docker` to apply it in the current shell, or log out and back in to make it permanent.

- **TensorFlow warnings about CUDA (`Could not find cuda drivers`)**
  - These appear when running without `--gpus all` (e.g. during smoke tests or CPU runs).
  - This is harmless — TensorFlow is only used by ANTsPyNet for brain extraction. The main GOUHFI inference uses PyTorch, which accesses the GPU separately via `--gpus all`.

