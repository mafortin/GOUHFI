import torch
import torch.nn as nn
from torch.optim import AdamW # Added by MAF
from nnunetv2.training.lr_scheduler.polylr import PolyLRScheduler
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer

from typing import Union, Tuple, List
import numpy as np
from batchgeneratorsv2.helpers.scalar_type import RandomScalar
from batchgeneratorsv2.transforms.base.basic_transform import BasicTransform


#-----------------------------------------------------------------------------------------------------------------------
class my_nnUNetTrainer(nnUNetTrainer):

    # MAF: setting the max number of epochs to 500 instead of 1000. Can be set to anything to be honest, just modify the value three lines below.
    def __init__(self, plans: dict, configuration: str, fold: int, dataset_json: dict, unpack_dataset: bool = True,
                 device: torch.device = torch.device('cuda')):
        super().__init__(plans, configuration, fold, dataset_json, unpack_dataset, device)
        self.num_epochs = 500 # Max number of epochs if no early stopping.
        self.initial_lr = 3e-4 # Base Learning Rate

    # Set adamW as the new optimizer + set new base Learning Rate
    def configure_optimizers(self):
        optimizer = AdamW(self.network.parameters(), lr=self.initial_lr, weight_decay=self.weight_decay, amsgrad=True) # Optimizer
        lr_scheduler = PolyLRScheduler(optimizer, self.initial_lr, self.num_epochs) # Learning Rate Scheduler

        return optimizer, lr_scheduler

    def run_training(self):
        self.on_train_start()

        best_val_dice = -1
        epochs_without_improvement = 0
        patience = 100

        for epoch in range(self.current_epoch, self.num_epochs):
            self.on_epoch_start()

            self.on_train_epoch_start()
            train_outputs = []
            for batch_id in range(self.num_iterations_per_epoch):
                train_outputs.append(self.train_step(next(self.dataloader_train)))
            self.on_train_epoch_end(train_outputs)

            with torch.no_grad():
                self.on_validation_epoch_start()
                val_outputs = []
                for batch_id in range(self.num_val_iterations_per_epoch):
                    val_outputs.append(self.validation_step(next(self.dataloader_val)))
                self.on_validation_epoch_end(val_outputs)

            # Early Stop Criterion implementation
            # Get current val Dice
            def get_latest_val_dice(self):
                try:
                    return self.logger.my_fantastic_logging['ema_fg_dice'][-1] # Use 'ema_fg_dice' if you want the moving average, 'mean_fg_dice' for the individual pseudo Dice values. 
                except (KeyError, IndexError):
                    return None  # Or 0.0, depending on your design
            
            current_val_dice = get_latest_val_dice(self)
            
            if current_val_dice is None:
                current_val_dice = 0.0

            if current_val_dice > best_val_dice:
                best_val_dice = current_val_dice
                epochs_without_improvement = 0
            else:
                epochs_without_improvement += 1

            if epochs_without_improvement >= patience:
                print(f"Early stopping triggered at epoch {epoch}")
                break

            self.on_epoch_end()

        self.on_train_end()
    

#-----------------------------------------------------------------------------------------------------------------------
# GOUHFI v2p0 trainer for the **parcellation** task/network.
class my_trainer_gouhfi_parc(my_nnUNetTrainer):

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



