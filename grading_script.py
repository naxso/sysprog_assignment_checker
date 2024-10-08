import subprocess
import os
import time
import zipfile
import tempfile
from pathlib import Path
import csv

# Define test cases for Problem 1, 2, and 3 (same as before)
test_cases = {
    "Problem_1": [
        {
            "input": "5 3.59\n4 A+\n3 B+\n3 C+\n1 D0\n3\n",
            "expected_output": "A+\n"
        },
        {
            "input": "3 4.44\n5 A+\n4 A+\n1\n",
            "expected_output": "A0\n"
        },
        {
            "input": "5 2.54\n3 B+\n2 B0\n2 C+\n2 C0\n1\n",
            "expected_output": "F\n"
        },
        {
            "input": "5 3.60\n4 A+\n3 B+\n3 C+\n1 D0\n3\n",
            "expected_output": "impossible\n"
        }
    ],
    "Problem_2": [
        {
            "input": "DUP\nMUL\nNUM 2\nADD\nEND\n3\n1\n10\n50\n\nNUM 1\nNUM 1\nADD\nEND\n2\n42\n43\n\nNUM 600000000\nADD\nEND\n3\n0\n600000000\n1\n\nQUIT",
            "expected_output": "3\n102\n2502\n\nERROR\nERROR\n\n600000000\nERROR\n600000001\n\n"
        }

    ],
    "Problem_3": [
        {
            "input": "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 1 2 0 0 2 2 2 1 0 0 0 0 0 0 0 0 0 0\n0 0 1 2 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0\n0 0 0 1 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 1 2 2 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 1 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 2 1 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n",
            "expected_output": "1\n3 2\n"
        }
    ]
}

# Set a time limit for execution
TIME_LIMIT = 2  # seconds

def get_root_directory(submission_tmp_dir):
    """Check if the extracted files are nested in a single root folder and return the root directory."""
    extracted_items = list(Path(submission_tmp_dir).iterdir())
    
    # If there's exactly one directory and it's a folder, assume it's the root
    if len(extracted_items) == 1 and extracted_items[0].is_dir():
        return extracted_items[0]  # The root folder
    return Path(submission_tmp_dir)  # Otherwise, use the original directory

def log_and_print(message, log_file):
    """Helper function to both print to terminal and log to file."""
    print(message)  # Print to the terminal
    log_file.write(message + '\n')  # Write to the log file

def check_file_structure(submission_dir, log_file):
    """Check if the submission contains the required files and directory structure."""
    required_structure = {
        "Problem_1": ["src/main.rs", "Cargo.toml"],
        "Problem_2": ["src/main.rs", "Cargo.toml"],
        "Problem_3": ["src/main.rs", "Cargo.toml"]
    }
    
    missing_problems = []
    for folder, required_files in required_structure.items():
        folder_path = Path(submission_dir) / folder
        if not folder_path.exists():
            log_and_print(f"Warning: Missing folder {folder}", log_file)
            missing_problems.append(folder)
            continue  # Move to the next problem
        for required_file in required_files:
            file_path = folder_path / required_file
            if not file_path.exists():
                log_and_print(f"Warning: Missing {required_file} in {folder}", log_file)
                missing_problems.append(folder)
                break  # Stop checking this problem and move to the next problem
    return missing_problems

def check_zip_file(zip_file_path, submission_tmp_dir, log_file):
    """Check if the .zip file contains the necessary files."""
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(submission_tmp_dir)

        # Find the actual root directory (handle nested folders)
        root_dir = get_root_directory(submission_tmp_dir)
        missing_problems = check_file_structure(root_dir, log_file)
        return missing_problems, root_dir
    except zipfile.BadZipFile:
        log_and_print(f"Error: {zip_file_path} is a bad zip file.", log_file)
        return None, None

def check_report(submission_dir, log_file):
    """Check if any PDF file exists in the report folder."""
    report_dir = Path(submission_dir)
    if report_dir.exists():
        for file in report_dir.iterdir():
            if file.suffix == '.pdf':
                return True
    log_and_print("Error: No PDF report found.", log_file)
    return False

def run_test(problem_name, cargo_path, log_file, result_summary):
    """Run the student's solution and check for correctness and performance."""
    if not Path(cargo_path).exists():
        log_and_print(f"Warning: Folder {cargo_path} does not exist, skipping {problem_name}", log_file)
        result_summary[problem_name] = "X"
        return False  # Skip if the folder doesn't exist

    original_cwd = os.getcwd()  # Save current directory
    test_passed = True

    for i, case in enumerate(test_cases[problem_name]):
        input_data = case["input"]
        expected_output = case["expected_output"]

        # Change directory to the correct Cargo package
        os.chdir(cargo_path)
        # Measure execution time
        start_time = time.time()

        try:
            result = subprocess.run(['cargo', 'run'], input=input_data.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=TIME_LIMIT, check=True)
        except subprocess.TimeoutExpired:
            log_and_print(f"{problem_name} Test Case {i + 1}: FAIL (Time limit exceeded)", log_file)
            test_passed = False
            continue  # Skip to the next test case
        except subprocess.CalledProcessError as e:
            log_and_print(f"Error running cargo for {problem_name}: {e}", log_file)
            os.chdir(original_cwd)
            result_summary[problem_name] = "X"
            return

        elapsed_time = time.time() - start_time

        # Check output against expected result
        actual_output = result.stdout.decode()
        actual_output_stripped = actual_output.strip()
        expected_output_stripped = expected_output.strip()

        # Check both with and without whitespace
        if actual_output == expected_output:
            log_and_print(f"{problem_name} Test Case {i + 1}: PASS (Time: {elapsed_time:.2f}s)", log_file)
        elif actual_output_stripped == expected_output_stripped:
            log_and_print(f"{problem_name} Test Case {i + 1}: PASS (whitespace differences only) (Time: {elapsed_time:.2f}s)", log_file)
        else:
            log_and_print(f"{problem_name} Test Case {i + 1}: FAIL", log_file)
            log_and_print(f"Expected (ignoring whitespace): {expected_output_stripped}", log_file)
            log_and_print(f"Actual (with whitespace):\n{actual_output}", log_file)
            log_and_print(f"Actual (ignoring whitespace): {actual_output_stripped}", log_file)
            test_passed = False

    result_summary[problem_name] = "O" if test_passed else "X"
    os.chdir(original_cwd)  # Change back to the original directory

def grade_assignments(zip_file_path, log_file, csv_writer):
    """Grade the assignment submission based on output, structure, and performance."""
    
    # Extract student identifier from the file name (after "Assignment_1_")
    student_id = os.path.basename(zip_file_path).split("_")[1].replace(".zip", "")
    
    # Initialize summary result for this submission
    result_summary = {"Problem_1": "X", "Problem_2": "X", "Problem_3": "X", "Report": "X"}
    
    # Step 1: Create a unique temporary directory for this submission using TemporaryDirectory
    with tempfile.TemporaryDirectory() as submission_tmp_dir:
        
        # Step 2: Check file structure inside the .zip file, including nesting
        missing_problems, root_dir = check_zip_file(zip_file_path, submission_tmp_dir, log_file)
        if missing_problems is None:
            log_and_print(f"File structure validation failed for {zip_file_path}", log_file)
            return  # Stop grading this submission
        
        # Step 3: Run tests for each problem, even if some are missing
        for problem in ["Problem_1", "Problem_2", "Problem_3"]:
            if problem in missing_problems:
                log_and_print(f"Skipping {problem} due to missing files.", log_file)
                continue  # Skip this problem if files are missing
            cargo_path = os.path.join(root_dir, problem)
            run_test(problem, cargo_path, log_file, result_summary)
        
        # Step 4: Check report file (any .pdf)
        if check_report(root_dir, log_file):
            log_and_print("Report file exists: PASS", log_file)
            result_summary["Report"] = "O"
        else:
            log_and_print("Report file is missing: FAIL", log_file)
    
    # Step 5: Write result summary for this submission into the CSV
    csv_writer.writerow([student_id, result_summary["Problem_1"], result_summary["Problem_2"], result_summary["Problem_3"], result_summary["Report"]])

def grade_all_submissions(directory_path, output_log, output_csv):
    """Grade all .zip files in a given directory and write to log and csv."""
    # Convert to absolute path
    directory_path = os.path.abspath(directory_path)
    
    # Open the log file to write results
    with open(output_log, 'w') as log_file, open(output_csv, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write CSV header
        csv_writer.writerow(["Student ID", "Problem_1", "Problem_2", "Problem_3", "Report"])
        
        # Get all .zip files in the directory
        zip_files = [f for f in os.listdir(directory_path) if f.endswith('.zip')]
        
        if not zip_files:
            log_and_print("No .zip files found in the directory.", log_file)
            return
        
        for zip_file in zip_files:
            log_and_print(f"\nGrading submission: {zip_file}", log_file)
            zip_file_path = os.path.join(directory_path, zip_file)
            grade_assignments(zip_file_path, log_file, csv_writer)

# Specify the directory containing all the zip submissions
submissions_directory = "kulms_submissions"
# Specify the output log file
output_log = "grading_results.log"
# Specify the output CSV file
output_csv = "grading_summary.csv"
grade_all_submissions(submissions_directory, output_log, output_csv)