# ============================================================
# GOUHFI 2.0 — GPU Image (CUDA 12.1 + PyTorch 2.1.2)
# ============================================================
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

LABEL maintainer="Marc-Antoine Fortin <marc.a.fortin@ntnu.no>"
LABEL description="GOUHFI 2.0 — Brain segmentation and cortical parcellation for UHF MRI"
LABEL version="2.0.0"

# System libraries required by TensorFlow (antspynet dependency) and graphviz
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        graphviz \
        unzip \
        wget \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/gouhfi

# Copy source tree — large files excluded via .dockerignore
COPY . /opt/gouhfi/

ENV GOUHFI_HOME=/opt/gouhfi
ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=3

# nnUNetv2 expects these directories to exist (set from GOUHFI_HOME at runtime)
RUN mkdir -p /opt/gouhfi/nnUNet_raw \
             /opt/gouhfi/nnUNet_preprocessed \
             /opt/gouhfi/trained_model

# Install GOUHFI and all Python dependencies.
# antspyx is installed explicitly because pyproject.toml lists "ants" which resolves
# to an unrelated stub on PyPI; antspyx is the actual ANTsPy package.
RUN pip install --no-cache-dir -e /opt/gouhfi

# ANTsPyNet brain extraction weights are NOT pre-cached here.
# They are downloaded on first use of run_preprocessing / run_brain_extraction
# and stored in the mounted cache volume (see VOLUME below and docker-compose.yml).
# This avoids redistributing third-party model weights whose figshare license
# terms are separate from the ANTsPyNet Apache 2.0 code license.
ENV KERAS_HOME=/opt/keras-cache

# Mount points:
#   /opt/gouhfi/trained_model  — GOUHFI model weights (read-only, mount from host)
#   /opt/keras-cache           — ANTsPyNet weight cache (persists between runs)
#   /input                     — input NIfTI files
#   /output                    — segmentation output
VOLUME ["/opt/gouhfi/trained_model", "/opt/keras-cache", "/input", "/output"]

CMD ["run_gouhfi", "--help"]
