import os
import argparse
import numpy as np
import nibabel as nib
from nibabel.processing import resample_from_to

def resample_nn(label_img, ref_img):
    return resample_from_to(label_img, ref_img, order=0)

def resample_onehot(label_img, ref_img):
    label_data = label_img.get_fdata()
    unique_labels = np.unique(label_data).astype(int)
    onehot_channels = []

    for label in unique_labels:
        binary_mask = (label_data == label).astype(np.float32)
        binary_img = nib.Nifti1Image(binary_mask, label_img.affine, label_img.header)
        resampled = resample_from_to(binary_img, ref_img, order=1)
        onehot_channels.append(resampled.get_fdata())

    onehot_stack = np.stack(onehot_channels, axis=-1)
    argmax_indices = np.argmax(onehot_stack, axis=-1)
    conformed_data = unique_labels[argmax_indices]
    return nib.Nifti1Image(conformed_data.astype(np.int16), ref_img.affine, ref_img.header)

def match_subject_ids(label_files, image_files):
    matched_pairs = []
    for label_file in label_files:
        label_id = os.path.basename(label_file).split('.')[0]
        for image_file in image_files:
            image_id = os.path.basename(image_file).split('.')[0]
            if label_id in image_id or image_id in label_id:
                matched_pairs.append((label_file, image_file))
                break
    return matched_pairs

def main(input_labels, input_images, output_dir, method):
    os.makedirs(output_dir, exist_ok=True)
    label_files = [os.path.join(input_labels, f) for f in os.listdir(input_labels) if f.endswith('.nii') or f.endswith('.nii.gz')]
    image_files = [os.path.join(input_images, f) for f in os.listdir(input_images) if f.endswith('.nii') or f.endswith('.nii.gz')]
    matched = match_subject_ids(label_files, image_files)

    for label_path, image_path in matched:
        subject_id = os.path.basename(label_path).split('.')[0]
        output_path = os.path.join(output_dir, f"{subject_id}.nii.gz")
        label_img = nib.load(label_path)
        ref_img = nib.load(image_path)

        if method == 'nn':
            conformed_img = resample_nn(label_img, ref_img)
        elif method == 'onehot_lin':
            conformed_img = resample_onehot(label_img, ref_img)
        else:
            raise ValueError("Invalid method. Choose 'nn' or 'onehot_lin'.")

        nib.save(conformed_img, output_path)
        print(f"Saved conformed label for {subject_id} to {output_path}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Conform label maps to match reference images.")
    parser.add_argument("--input_labels", required=True, help="Directory containing label maps.")
    parser.add_argument("--input_images", required=True, help="Directory containing reference images.")
    parser.add_argument("--output_dir", required=True, help="Directory to save conformed label maps.")
    parser.add_argument("--method", choices=['nn', 'onehot_lin'], default='nn', help="Resampling method: 'nn' or 'onehot'")
    args = parser.parse_args()

    main(args.input_labels, args.input_images, args.output_dir, args.method)