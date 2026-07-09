import subprocess
import sys

def main():
    print("==================================================")
    print("Running GALXY Module 3 (Products) API Test Suite...")
    print("==================================================")
    
    # Execute pytest as a python module to avoid PATH search issues
    result = subprocess.run(["python", "-m", "pytest", "-v"], capture_output=False)
    
    if result.returncode == 0:
        print("\n[SUCCESS] All unit tests passed! The Backend Admin API for Module 3 (Products) is verified and fully functional.")
        sys.exit(0)
    else:
        print(f"\n[FAILURE] Some tests failed. Exit code: {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
