import os
import argparse
import nibabel as nib
import numpy as np
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor


def process_file(args):
    # In the function signature:
    file_path, output_dir, keep_labels, min_label, max_label, reindex, set_to_one, combine_ctx = args


    seg_nii = nib.load(file_path)
    seg = seg_nii.get_fdata()
    seg = np.round(seg).astype(np.int32)

    if keep_labels is not None:
        seg[~np.isin(seg, keep_labels)] = 0

    if min_label is not None:
        seg[seg < min_label] = 0

    if max_label is not None:
        seg[seg > max_label] = 0

    if combine_ctx:
        seg[(seg >= 1000) & (seg < 2000)] = 3    # Left cortex in FS LUT
        seg[(seg >= 2000) & (seg < 3000)] = 42   # Right cortex in FS LUT

    if set_to_one == "all":
        seg[seg != 0] = 1
    elif isinstance(set_to_one, list):
        for label in set_to_one:
            seg[seg == label] = 1

    if reindex:
        unique_labels = sorted(list(set(np.unique(seg)) - {0}))
        label_mapping = {old: new for new, old in enumerate(unique_labels, start=1)}
        reindexed = np.zeros_like(seg, dtype=np.int32)
        for old_label, new_label in label_mapping.items():
            reindexed[seg == old_label] = new_label
        seg = reindexed

    seg = seg.astype(np.uint8)
    output_path = os.path.join(output_dir, os.path.basename(file_path))
    new_nii = nib.Nifti1Image(seg, affine=seg_nii.affine, header=seg_nii.header)
    nib.save(new_nii, output_path)
    return output_path


def parse_set_to_one(value_list):
    if len(value_list) == 1 and value_list[0].lower() == "all":
        return "all"
    return [int(v) for v in value_list]


def main():
    parser = argparse.ArgumentParser(description="Set unwanted labels to 0, optionally reindex, or map labels to 1.")
    parser.add_argument("--input", required=True, help="Input directory containing .nii or .nii.gz files.")
    parser.add_argument("--output", required=True, help="Output directory to save processed label maps.")
    parser.add_argument("--keep-labels", type=int, nargs="+", help="Labels to keep (all others set to 0).")
    parser.add_argument("--min-label", type=int, help="Minimum label value to keep (others set to 0).")
    parser.add_argument("--max-label", type=int, help="Maximum label value to keep (others set to 0).")
    parser.add_argument("--set-to-one", nargs="+", type=str, help="Labels to set to 1, or 'all' to set all non-zero labels.")
    parser.add_argument("--reindex", action="store_true", help="Reindex remaining labels to 1..N.")
    parser.add_argument("--combine-ctx", action="store_true", help="Combine left cortex labels (1000s) to 3 and right cortex labels (2000s) to 42.")
    parser.add_argument("--num-workers", type=int, default=4, help="Number of parallel workers.")
    args = parser.parse_args()

    set_to_one = parse_set_to_one(args.set_to_one) if args.set_to_one else None

    os.makedirs(args.output, exist_ok=True)

    files = [os.path.join(args.input, f) for f in os.listdir(args.input)
             if f.endswith(".nii.gz") or f.endswith(".nii")]

    print(f"Processing {len(files)} files with {args.num_workers} workers...")

    task_args = [
        (f, args.output, args.keep_labels, args.min_label, args.max_label, args.reindex, set_to_one, args.combine_ctx)
        for f in files
    ]



    with ProcessPoolExecutor(max_workers=args.num_workers) as executor:
        list(tqdm(executor.map(process_file, task_args), total=len(files), desc="Processing"))

    print("All files processed.")


if __name__ == "__main__":
    main()
