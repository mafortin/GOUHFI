import argparse
import os
import nibabel as nib
from nibabel.processing import resample_from_to
import numpy as np
from scipy.ndimage import binary_fill_holes, binary_dilation

def find_file(directory, substring):
    for file_name in os.listdir(directory):
        if substring in file_name and (
                file_name.endswith('.nii') or file_name.endswith('.nii.gz') or file_name.endswith('.mgz')):
            return os.path.join(directory, file_name)
    return None

def load_nifti(file_path):
    img = nib.load(file_path)
    data = img.get_fdata()
    return img, data

def save_nifti(output_path, data, reference_img):
    new_img = nib.Nifti1Image(data, affine=reference_img.affine, header=reference_img.header)
    nib.save(new_img, output_path)

def resample_to_target(source_img, target_img, interpolation='cubic'):
    target_shape = target_img.shape
    target_affine = target_img.affine

    if interpolation == 'cubic':
        order = 3
    elif interpolation == 'nearest':
        order = 0
    elif interpolation == 'linear':
        order = 2

    return resample_from_to(source_img, (target_shape, target_affine), order=order)

def process_mask(mask_data, fill_holes=True, dilation_iterations=None, save_new_mask=False):
    closed_mask = binary_fill_holes(mask_data) if fill_holes else mask_data
    return binary_dilation(closed_mask, iterations=dilation_iterations) if dilation_iterations else closed_mask

def add_extra_label(label_map, mask, extra_label=np.int32(257)):
    new_label_map = label_map.copy()
    new_label_map[(mask > 0) & (label_map == 0)] = extra_label
    return np.round(new_label_map).astype(np.int32)

def get_masked_image_filename(input_image_path):
    og_img_filename = os.path.basename(input_image_path)
    if og_img_filename.endswith('.mgz'):
        new_masked_img_filename = og_img_filename.replace(".mgz", "_masked.nii.gz")
    elif og_img_filename.endswith('.nii.gz'):
        new_masked_img_filename = og_img_filename.replace(".nii.gz", "_masked.nii.gz")
    elif og_img_filename.endswith('.nii'):
        new_masked_img_filename = og_img_filename.replace(".nii", "_masked.nii.gz")
    else:
        exit("Wrong image file extension.")
    return new_masked_img_filename


def main():
    parser = argparse.ArgumentParser(description="Process MRI images and segmentation maps.")
    parser.add_argument('-i', '--input_dir', required=True, help="Directory containing input files (label map + mask + input image).")
    parser.add_argument('-o','--output_dir', help="Directory to save the output files. If not provided, defaults to the input directory.")
    parser.add_argument('--labelmap', default="aseg", help="Substring to identify the labelmap file (e.g., 'aseg.mgz').")
    parser.add_argument('--mask', default="mask.mgz", help="Substring to identify the mask file (e.g., 'mask.mgz').")
    parser.add_argument('--image', default="orig.mgz", help="Substring to identify the input MRI image (e.g., 'orig.mgz').")
    parser.add_argument('--fill_holes', action='store_true', help="Set flag if you want the holes in the mask to be filled.")
    parser.add_argument('--dilate-iters', type=int, help="Number of iterations for morphological dilation (default: skipped if not provided). Moreover, if the input image (--image flag) is orig.mgz, the dilation step is ignored no matter the value set here.")
    parser.add_argument('--save_new_mask', action='store_true', help="Set flag if you want to save the newly modified mask (the original mask is kept intact).")
    parser.add_argument('--new_label', type=int, default=np.int32(257), help="New label value to be added to the label map (default: 257).")
    parser.add_argument('--new_labelmap_name', type=str, help="New name for the modified label map. Include the file extension in it (default: 'aseg_mod.nii.gz').")
    
    args = parser.parse_args()

    # Set output directory
    output_dir = args.output_dir if args.output_dir else args.input_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)    
        
    # Locate the labelmap, mask, and input image files
    labelmap_file = find_file(args.input_dir, args.labelmap)
    mask_file = find_file(args.input_dir, args.mask)
    input_file = find_file(args.input_dir, args.image)

    if not labelmap_file or not mask_file or not input_file:
        raise FileNotFoundError("Could not find label map, mask, or input file in the specified directory.")

    print(f"Found labelmap file: {labelmap_file}")
    print(f"Found mask file: {mask_file}")
    print(f"Found input image file: {input_file}")

    # Load labelmap, mask, and input image
    label_img, label_data = load_nifti(labelmap_file)
    mask_img, mask_data = load_nifti(mask_file)
    input_img, input_data = load_nifti(input_file)

    # Resample the label map to the input image if necessary
    if args.image in ['orig.mgz', 'orig.nii.gz']:
        print("Since the input image provided is the 'orig' from FreeSurfer/FastSurfer, no need to resample it to the mask (because it is already).")
    else:
        print("Resampling the input image to the labelmap in order to create a masked/brain extracted version of the input image.")
        resampled_input_img = resample_to_target(input_img, label_img, interpolation='cubic')
        print("Resampling done.")

    # Creation of the new label map

    # Ensure mask is binary
    mask_data = (mask_data > 0).astype(np.uint8)

    # Prepare the original label map
    unique_raw_labels = np.unique(label_data)
    print("Unique label values in the original label map provided: ", unique_raw_labels)
    rounded_int_label_map = np.round(label_data).astype(np.int32)
    #print("Label map (1) rounded and (2) converted/enforced to np.int32 datatype for consistency.")

    # Apply morphological operations on the mask
    print("Starting: morphological operations on the original mask.")
    processed_mask = process_mask(mask_data, fill_holes=args.fill_holes, dilation_iterations=args.dilate_iters)
    print("Completed: morphological operations on the original mask.")

    # Save the new mask if desired
    if args.save_new_mask:
        dir2new_mask = output_dir 
        og_mask_name = os.path.basename(mask_file)
        new_mask_name = og_mask_name.replace(".mgz", "_mod.nii.gz")
        path2new_mask = os.path.join(dir2new_mask, new_mask_name)
        save_nifti(path2new_mask, processed_mask.astype(np.uint8), mask_img)
        print(f"The new modified mask was saved as {path2new_mask}.")

    # Add extra label to the label map
    print("Starting: adding the extra-cerebrum label to the label map.")
    modified_label_map = add_extra_label(rounded_int_label_map, processed_mask, extra_label=args.new_label)
    print("Completed: adding the extra-cerebrum label to the label map.")

    # Save the new label map
    rounded_int_modified_label_map = np.round(modified_label_map).astype(np.int32)

    new_affine = label_img.affine
    new_header = label_img.header
    new_header.set_data_dtype(np.int32) # If you wonder, I add many many many issues with precision levels of label maps, so I prefer being safer than sorry.

    if args.new_labelmap_name is None:
        new_labelmap_name = os.path.basename(labelmap_file).replace(".mgz", "_mod.nii.gz")

    new_label_map = nib.Nifti1Image(rounded_int_modified_label_map, affine=new_affine, header=new_header)
    label_map_output_path = os.path.join(output_dir, new_labelmap_name)
    nib.save(new_label_map, label_map_output_path)
    print(f"Modified label map saved as: {label_map_output_path}")

    if 'orig' in args.image:
        print("Starting: masking the input image.")
        input_masked_data = input_data * processed_mask
        input_masked_output = os.path.join(output_dir, get_masked_image_filename(input_file))
        save_nifti(input_masked_output, input_masked_data.astype(np.float32), input_img)
        print(f"Masked input image saved as: {input_masked_output}")
    else:
        print("Starting: masking the resampled input image.")
        resampled_input_data = resampled_input_img.get_fdata()
        input_masked_data = resampled_input_data * processed_mask
        input_masked_output = os.path.join(output_dir, get_masked_image_filename(input_file))
        save_nifti(input_masked_path, input_masked_data.astype(np.float32), resampled_input_img)
        print(f"Masked input image saved as: {input_masked_path}")

    print("Done! :)")

if __name__ == "__main__":
    main()
