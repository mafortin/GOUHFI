import argparse
import subprocess
import os
import glob
import time


def run_inference(dataset_id, input_dir, output_dir, config, trainer, plan, folds, num_pr):
    start_time = time.time()
    # Command for inference
    inference_command = [
                            "nnUNetv2_predict",
                            "-d", dataset_id,
                            "-i", input_dir,
                            "-o", output_dir,
                            "-tr", trainer,
                            "-c", config,
                            "-p", plan,
                            "-f"
                        ] + folds + [
                            "-chk", "checkpoint_best.pth",
                            "-npp", str(num_pr),
                            "-nps", str(num_pr)
                        ]
    print(f"Running inference with the following command: {' '.join(inference_command)}")
    subprocess.run(inference_command)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Inference completed in {duration:.2f} seconds.")
    return duration


def apply_post_processing(input_dir, output_dir, pp_pkl_file, np, plans_json):
    start_time = time.time()
    # Command for applying post processing
    post_processing_command = [
        "nnUNetv2_apply_postprocessing",
        "-i", input_dir,
        "-o", output_dir,
        "-pp_pkl_file", pp_pkl_file,
        "-np", str(np),
        "-plans_json", plans_json
    ]
    print(f"Applying post-processing with the following command: {' '.join(post_processing_command)}")
    subprocess.run(post_processing_command)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Post-processing completed in {duration:.2f} seconds.")
    return duration


def run_evaluation(input_dir, gt_dir, djfile, pfile, output_eval, skip_asd):
    start_time = time.time()
    # Command for evaluation
    evaluation_command = [
        "nnUNetv2_evaluate_folder", #nnUNetv2_evaluate_folder_asd
        gt_dir,
        input_dir,
        "-djfile", djfile,
        "-pfile", pfile,
        "-o", output_eval
    ]

    if skip_asd:
        evaluation_command.append("--skip_asd")

    print(f"Running evaluation with the following command: {' '.join(evaluation_command)}")
    subprocess.run(evaluation_command)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Evaluation completed in {duration:.2f} seconds.")
    return duration


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run nnUNet_v2 inference, post-processing, and optional evaluation.")

    parser.add_argument("--dataset_id", required=True, help="Dataset ID in the format DatasetXXX_YYYY.")
    parser.add_argument("--input_dir", required=True, help="Directory containing input data.")
    parser.add_argument("--config", default="3d_fullres", help="Configuration to use for inference.")
    parser.add_argument("--trainer", default="nnUNetTrainer_NoDA_500epochs_AdamW", help="Trainer to use for inference.")
    parser.add_argument("--plan", default="nnUNetResEncL", help="Plan to use for inference.")
    parser.add_argument("--np", default=12, help="Number of processes for post-processing.")
    parser.add_argument("--folds", default="0 1 2 3 4", help="Folds to use for inference.")
    parser.add_argument("--eval", action='store_true', help="Flag to run evaluation.")
    parser.add_argument("--eval_only", action='store_true', help="Flag to run evaluation only.")
    parser.add_argument("--gt_dir", help="Directory containing ground truth data for evaluation.")
    parser.add_argument("--skip_asd", action='store_true',
                        help="Flag to skip ASD calculation and set ASD values to NaN.")

    args = parser.parse_args()

    # Convert folds argument to a list of strings
    folds_list = args.folds.split()

    # Construct paths based on input_dir and dataset_id
    input_dir = args.input_dir.rstrip('/')
    base_dir = os.path.dirname(input_dir)
    output_dir = os.path.join(base_dir, "outputs")
    output_pp_dir = os.path.join(base_dir, "outputs_pp")
    results_dir = f"/home/marcantf/Data/nnunet/results/{args.dataset_id}/{args.trainer}__{args.plan}__{args.config}/crossval_results_folds_0_1_2_3_4/"
    pp_pkl_file = os.path.join(results_dir, "postprocessing.pkl")
    plans_json = os.path.join(results_dir, "plans.json")

    if not args.eval_only:
        # Run inference
        inference_duration = run_inference(args.dataset_id, input_dir, output_dir, args.config, args.trainer,
                                           args.plan, folds_list,
                                           args.np)
        #print(f"Total duration for inference: {inference_duration:.2f} seconds.")

        # Apply post-processing
        post_processing_duration = apply_post_processing(output_dir, output_pp_dir, pp_pkl_file, args.np, plans_json)
        #print(f"Total duration for post-processing: {post_processing_duration:.2f} seconds.")

    # Run evaluation if the --eval or --eval_only flag is set
    if args.eval or args.eval_only:
        if not args.gt_dir:
            raise ValueError("Ground truth directory must be specified when --eval or --eval_only flag is set.")

        # Find all .json files containing the substring "_eval_" in them
        json_files = glob.glob(f"/home/marcantf/Data/nnunet/raw/{args.dataset_id}/*_eval_*.json")

        for json_file in json_files:
            eval_name = os.path.basename(json_file).split('_eval_')[1].split('.json')[0]
            output_eval = os.path.join(output_pp_dir, f"eval_metrics_{eval_name}.json")
            evaluation_duration = run_evaluation(output_pp_dir, args.gt_dir, json_file, plans_json, output_eval, args.skip_asd)
            #print(f"Total duration for evaluation ({eval_name}): {evaluation_duration:.2f} seconds.")