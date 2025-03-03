"""
Python Class Diagram Generator

This script generates UML class diagrams from Python code using Pyreverse.
It creates a diagrams/ directory and places the output files there.
"""

import os
import subprocess
import sys

def generate_diagrams(project_name="panel", source_path="."):
    """
    Generate class and package diagrams using Pyreverse.
    
    Args:
        project_name (str): The name of the project (used for output filenames)
        source_path (str): Path to the source code directory
    """
    # Create diagrams directory if it doesn't exist
    diagrams_dir = "diagrams"
    if not os.path.exists(diagrams_dir):
        os.makedirs(diagrams_dir)
        print(f"Created directory: {diagrams_dir}")
    
    # Full path for output files
    output_path = os.path.join(diagrams_dir, project_name)
    
    # Run pyreverse command
    cmd = [
        "pyreverse",
        "-o", "png",            # Output format
        "-p", project_name,     # Project name
        "-k",                   # Include package diagrams
        "--output-directory", diagrams_dir,  # Output directory
        source_path             # Source code path
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Diagram generation successful!")
        print(f"Class diagram: {diagrams_dir}/classes_{project_name}.png")
        print(f"Package diagram: {diagrams_dir}/packages_{project_name}.png")
    except subprocess.CalledProcessError as e:
        print(f"Error generating diagrams: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: pyreverse command not found. Please make sure pylint is installed.")
        print("You can install it with: pip install pylint")
        sys.exit(1)

if __name__ == "__main__":
    # Get arguments from command line or use defaults
    project_name = sys.argv[1] if len(sys.argv) > 1 else "panel"
    source_path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    generate_diagrams(project_name, source_path)
