# run_tests.py
# Adam Morehouse, Ryan Fosco, Brandon Coulter
# 14 April 2025
# Runs all our Project 2 test cases and saves outputs to test_results.txt

import subprocess
import os

# List of test cases, matching our documentation
tests = [
    {"name": "Test 1", "command": ["python", "project2.py", "transactions.txt", "1", "1", "1"]},
    {"name": "Test 2", "command": ["python", "project2.py", "transactions.txt", "1", "2", "5"]},
    {"name": "Test 3", "command": ["python", "project2.py", "transactions.txt", "2", "1", "5"]},
    {"name": "Test 4", "command": ["python", "project2.py", "transactionsMedium.txt", "2", "2", "3"]},
    {"name": "Test 5", "command": ["python", "project2.py", "transactionsHeavy.txt", "3", "3", "10"]},
    {"name": "Test 6", "command": ["python", "project2.py", "transactionsSingle.txt", "1", "1", "1"]},
    {"name": "Test 7", "command": ["python", "project2.py", "transactionsEasy.txt", "1", "2", "2"]}
]

# Files we need
required_files = [
    "project2.py",
    "transactions.txt",
    "transactionsEasy.txt",
    "transactionsMedium.txt",
    "transactionsHeavy.txt",
    "transactionsSingle.txt"
]

def check_files():
    """Make sure all files are here before we start."""
    for file in required_files:
        if not os.path.exists(file):
            print(f"Oops, {file} is missing!")
            return False
    return True

def run_test(test):
    """Run a single test and get its output."""
    print(f"Running {test['name']}...")
    try:
        # Run the command, capture output, timeout after 30 seconds
        result = subprocess.run(
            test["command"],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += "\nErrors:\n" + result.stderr
        return output
    except subprocess.TimeoutExpired:
        return f"{test['name']} timed out after 30 seconds!"
    except Exception as e:
        return f"{test['name']} failed: {str(e)}"

def main():
    # Check if files exist
    if not check_files():
        print("Can’t run tests, fix the missing files first.")
        return
    
    # Open output file
    with open("test_results.txt", "w") as f:
        f.write("CSC433A Project 2 Test Results\n")
        f.write("Adam Morehouse, Ryan Fosco, Brandon Coulter\n")
        f.write("14 April 2025\n\n")
        
        # Run each test
        for test in tests:
            f.write(f"--- {test['name']} ---\n")
            f.write(f"Command: {' '.join(test['command'])}\n\n")
            output = run_test(test)
            f.write(output)
            f.write("\n" + "="*50 + "\n\n")
    
    print("All done! Check test_results.txt for results.")

if __name__ == "__main__":
    main()