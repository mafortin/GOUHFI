import os
import argparse
import subprocess
import pandas as pd


def conform_images(input_dir, output_dir, order, rename, dtype, seg_input):
    # Ensure output directory exists
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.join(os.path.dirname(input_dir), 'inputs-cfm')
        os.makedirs(output_dir, exist_ok=True)

    # Prepare for renaming if needed
    rename_mapping = []

    # Iterate over all files in the input directory
    for idx, filename in enumerate(sorted(os.listdir(input_dir))):
        if filename.endswith(".nii.gz"):
            input_path = os.path.join(input_dir, filename)
            if rename:
                new_filename = f"image_{idx:04d}_0000.nii.gz"
                output_path = os.path.join(output_dir, new_filename)
                rename_mapping.append({'Old Filename': filename, 'New Filename': new_filename})
            else:
                output_path = os.path.join(output_dir, filename)

            # Construct the command
            command = [
                "python", "./FastSurferCNN/data_loader/conform.py",
                "-i", input_path,
                "-o", output_path,
                "--conform_min",
                "--verbose",
                "--order", str(order),
                "--dtype", dtype
            ]

            # Add the --seg_input flag if specified
            if seg_input:
                command.append("--seg_input")

            # Run the command
            subprocess.run(command, check=True)
            print(f"Processed {filename}")

    # Save rename mapping if renaming was done
    if rename:
        rename_df = pd.DataFrame(rename_mapping)
        rename_df.to_csv(os.path.join(output_dir, 'rename_mapping.csv'), index=False)
        print(f"Rename mapping saved to {os.path.join(output_dir, 'rename_mapping.csv')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conform NIfTI images in a directory.")
    parser.add_argument("-i", "--input_dir", required=True, help="Path to the input directory containing NIfTI images.")
    parser.add_argument("-o", "--output_dir",
                        help="Path to the output directory to save conformed images. If not provided, input files will be overwritten.")
    parser.add_argument("--order", type=int, default=3, help="Order of interpolation to use (default: 3).")
    parser.add_argument("--rename", action='store_true',
                        help="Rename conformed images in a chronological order and save the mapping to a CSV file.")
    parser.add_argument("--dtype", type=str, default="float32",
                        help="Data type to use for the conformed images (default: float32. Other options: uin8, int16, int32).")
    parser.add_argument("--seg_input", action='store_true',
                        help="Indicate that the image to be conformed is a label map.")

    args = parser.parse_args()

    conform_images(args.input_dir, args.output_dir, args.order, args.rename, args.dtype, args.seg_input)