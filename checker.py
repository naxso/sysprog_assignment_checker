import subprocess
import time
import os
import zipfile
import shutil

# Test case structure
class TestCase:
    def __init__(self, input_data, expected_output, max_time):
        self.input_data = input_data
        self.expected_output = expected_output
        self.max_time = max_time

# Function to build and run Docker container for each submission
def run_in_docker(submission_dir, input_data):
    docker_image = "rust_grader_image"  # The pre-built Docker image for grading
    
    try:
        # Build Docker image if necessary
        subprocess.run(
            ["docker", "build", "-t", docker_image, "."],
            cwd=submission_dir,
            check=True
        )

        # Run the submission in a Docker container
        result = subprocess.run(
            ["docker", "run", "--rm", "-i", docker_image],
            input=input_data.encode(),
            capture_output=True,
            text=True,
            timeout=10  # Max 10 seconds to avoid hanging
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"
    except subprocess.CalledProcessError as e:
        return None, f"Build failed: {e.stderr}"

# Function to check correctness
def check_correctness(output, expected_output):
    return output.strip() == expected_output.strip()

# Function to grade a problem based on test cases
def grade_problem(problem_dir, test_cases):
    passed = 0
    for test_case in test_cases:
        start_time = time.time()
        output, error = run_in_docker(problem_dir, test_case.input_data)
        elapsed_time = time.time() - start_time

        if error:
            print(f"Error: {error}")
            continue
        
        if elapsed_time > test_case.max_time:
            print(f"Test case failed due to timeout: {elapsed_time:.2f}s")
            continue

        if check_correctness(output, test_case.expected_output):
            passed += 1
        else:
            print(f"Test case failed: expected '{test_case.expected_output}', got '{output}'")

    total = len(test_cases)
    return passed, total

# Function to check if the file structure is valid
def check_file_structure(submission_path):
    # Check if all problem directories exist
    for problem_num in range(1, 4):
        problem_dir = os.path.join(submission_path, f"Problem_{problem_num}")
        if not os.path.exists(problem_dir):
            print(f"Problem_{problem_num} directory not found.")
            return False
        if not os.path.exists(os.path.join(problem_dir, "Cargo.toml")):
            print(f"Cargo.toml missing in Problem_{problem_num}.")
            return False
    return True

# Function to unzip the submission
def unzip_submission(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Main grading function
def grade_submission(submission_zip):
    submission_dir = "./submission"
    
    # Clean any existing submission directory
    if os.path.exists(submission_dir):
        shutil.rmtree(submission_dir)
    
    # Unzip the submission
    unzip_submission(submission_zip, submission_dir)

    # Check if the file structure is correct
    if not check_file_structure(submission_dir):
        print("Submission failed due to incorrect file structure.")
        return

    # Test cases for each problem
    test_cases_p1 = [
        TestCase("5 3.59\n4 A+\n3 B+\n3 C+\n1 D0\n3", "A+", 2),
        # Add more test cases here...
    ]

    test_cases_p2 = [
        TestCase("DUP\nMUL\nNUM 2\nADD\nEND\n3\n1\n10\n50", "102\n2502\nERROR", 2),
        # Add more test cases here...
    ]

    test_cases_p3 = [
        TestCase("0 0 0 ...", "1\n3 2", 2),
        # Add more test cases here...
    ]

    # Grade each problem
    p1_passed, p1_total = grade_problem(os.path.join(submission_dir, "Problem_1"), test_cases_p1)
    p2_passed, p2_total = grade_problem(os.path.join(submission_dir, "Problem_2"), test_cases_p2)
    p3_passed, p3_total = grade_problem(os.path.join(submission_dir, "Problem_3"), test_cases_p3)

    # Output the results
    print(f"Problem 1: {p1_passed}/{p1_total}")
    print(f"Problem 2: {p2_passed}/{p2_total}")
    print(f"Problem 3: {p3_passed}/{p3_total}")

    # Calculate the final grade (for example, averaging the results)
    total_passed = p1_passed + p2_passed + p2_total
    total_tests = p1_total + p2_total + p3_total
    final_grade = (total_passed / total_tests) * 100

    print(f"Final Grade: {final_grade:.2f}%")

# Example of running the grading system
if __name__ == "__main__":
    submission_zip = "path/to/submission.zip"
    grade_submission(submission_zip)
