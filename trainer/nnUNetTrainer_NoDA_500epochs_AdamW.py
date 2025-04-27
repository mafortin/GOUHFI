import torch
import torch.nn as nn
from torch.optim import Adam, AdamW # Added by MAF
from trainer.training.lr_scheduler.polylr import PolyLRScheduler
from trainer.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from typing import Union, Tuple, List
import numpy as np
from batchgeneratorsv2.helpers.scalar_type import RandomScalar
from batchgeneratorsv2.transforms.base.basic_transform import BasicTransform

class nnUNetTrainer_NoDA_500epochs_AdamW(nnUNetTrainer):

    # MAF: setting the max number of epochs to 500 instead of 1000. Can be set to anything to be honest, just modify the value three lines below.
    def __init__(self, plans: dict, configuration: str, fold: int, dataset_json: dict, unpack_dataset: bool = True,
                 device: torch.device = torch.device('cuda')):
        super().__init__(plans, configuration, fold, dataset_json, unpack_dataset, device)
        self.num_epochs = 500 # Max number of epochs if no early stopping.

    # Set adamW as the new optimizer + set new base Learning Rate
    def configure_optimizers(self):
        self.initial_lr = 3e-4 # Base Learning Rate
        optimizer = AdamW(self.network.parameters(), lr=self.initial_lr, weight_decay=self.weight_decay, amsgrad=True) # Optimizer
        lr_scheduler = PolyLRScheduler(optimizer, self.initial_lr, self.num_epochs) # Learning Rate Scheduler

        return optimizer, lr_scheduler

    # MAF: This is the part for removing the Data Augmentation step.
    @staticmethod
    def get_training_transforms(
            patch_size: Union[np.ndarray, Tuple[int]],
            rotation_for_DA: RandomScalar,
            deep_supervision_scales: Union[List, Tuple, None],
            mirror_axes: Tuple[int, ...],
            do_dummy_2d_data_aug: bool,
            use_mask_for_norm: List[bool] = None,
            is_cascaded: bool = False,
            foreground_labels: Union[Tuple[int, ...], List[int]] = None,
            regions: List[Union[List[int], Tuple[int, ...], int]] = None,
            ignore_label: int = None,
    ) -> BasicTransform:
        return nnUNetTrainer.get_validation_transforms(deep_supervision_scales, is_cascaded, foreground_labels,
                                                       regions, ignore_label)

    def configure_rotation_dummyDA_mirroring_and_inital_patch_size(self):
        rotation_for_DA, do_dummy_2d_data_aug, _, _ = \
            super().configure_rotation_dummyDA_mirroring_and_inital_patch_size()
        mirror_axes = None
        self.inference_allowed_mirroring_axes = None
        initial_patch_size = self.configuration_manager.patch_size
        return rotation_for_DA, do_dummy_2d_data_aug, initial_patch_size, mirror_axes


    