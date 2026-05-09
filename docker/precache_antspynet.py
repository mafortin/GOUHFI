#!/usr/bin/env python3
"""
Pre-download ANTsPyNet brain extraction model weights during Docker image build.
Weights are stored in /root/.keras/ and later copied to /opt/keras-cache in the
Dockerfile so no internet access is needed at runtime.
"""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from antspynet.utilities import get_pretrained_network

# Modality "t1"      → brainExtractionRobustT1  (default in GOUHFI preprocessing)
# Modality "t2"      → brainExtractionRobustT2
# Modality "t2star"  → brainExtractionRobustT2Star  (common at UHF)
# Modality "flair"   → brainExtractionRobustFLAIR
models = [
    "brainExtractionRobustT1",
    "brainExtractionRobustT2",
    "brainExtractionRobustT2Star",
    "brainExtractionRobustFLAIR",
]

for model in models:
    print(f"Caching {model} ...")
    get_pretrained_network(model, antsxnet_cache_directory=None)
    print(f"  OK")

print("ANTsPyNet weight pre-caching complete.")
