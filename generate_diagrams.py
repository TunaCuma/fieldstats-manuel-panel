#!/usr/bin/env python3
"""
Python Class Diagram Generator

This script generates UML class diagrams from Python code using Pyreverse.
It creates a diagrams/ directory and places the output files there.
The script generates both graphical (PNG) and textual (DOT) representations
of the class and package diagrams. It also generates diagrams with the -k option,
which hides module names in class names for a cleaner representation.
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
    os.path.join(diagrams_dir, project_name)

    # Run pyreverse command for PNG output (normal version)
    cmd_png = [
        "pyreverse",
        "-o",
        "png",  # Output format
        "-p",
        project_name,  # Project name
        "--output-directory",
        diagrams_dir,  # Output directory
        source_path,  # Source code path
    ]

    # Run pyreverse command for PNG output with -k option (no module names)
    cmd_png_k = [
        "pyreverse",
        "-o",
        "png",  # Output format
        "-p",
        f"{project_name}_simple",  # Different project name for distinction
        "-k",  # Hide module names
        "--output-directory",
        diagrams_dir,  # Output directory
        source_path,  # Source code path
    ]

    # Run pyreverse command for textual output (dot format - normal version)
    cmd_dot = [
        "pyreverse",
        "-o",
        "dot",  # Output format
        "-p",
        project_name,  # Project name
        "--output-directory",
        diagrams_dir,  # Output directory
        source_path,  # Source code path
    ]

    # Run pyreverse command for textual output with -k option (dot format -
    # simple version)
    cmd_dot_k = [
        "pyreverse",
        "-o",
        "dot",  # Output format
        "-p",
        f"{project_name}_simple",  # Different project name for distinction
        "-k",  # Hide module names
        "--output-directory",
        diagrams_dir,  # Output directory
        source_path,  # Source code path
    ]

    print(f"Running pyreverse commands to generate diagrams...")

    try:
        # Generate standard PNG diagrams
        result_png = subprocess.run(cmd_png, check=True, capture_output=True, text=True)
        print("\n✅ Standard PNG diagrams generated:")
        print(f"  - Class diagram: {diagrams_dir}/classes_{project_name}.png")
        print(f"  - Package diagram: {diagrams_dir}/packages_{project_name}.png")

        # Generate simplified PNG diagrams (-k option)
        result_png_k = subprocess.run(
            cmd_png_k, check=True, capture_output=True, text=True
        )
        print("\n✅ Simplified PNG diagrams generated (-k option):")
        print(f"  - Class diagram: {diagrams_dir}/classes_{project_name}_simple.png")
        print(f"  - Package diagram: {diagrams_dir}/packages_{project_name}_simple.png")

        # Generate standard DOT text files
        result_dot = subprocess.run(cmd_dot, check=True, capture_output=True, text=True)
        print("\n✅ Standard DOT files generated:")
        print(f"  - Class diagram (text): {diagrams_dir}/classes_{project_name}.dot")
        print(f"  - Package diagram (text): {diagrams_dir}/packages_{project_name}.dot")

        # Generate simplified DOT text files (-k option)
        result_dot_k = subprocess.run(
            cmd_dot_k, check=True, capture_output=True, text=True
        )
        print("\n✅ Simplified DOT files generated (-k option):")
        print(
            f"  - Class diagram (text): {diagrams_dir}/classes_{project_name}_simple.dot"
        )
        print(
            f"  - Package diagram (text): {diagrams_dir}/packages_{project_name}_simple.dot"
        )

        print("\nAll diagrams have been generated successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error generating diagrams: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(
            "Error: pyreverse command not found. Please make sure pylint is installed."
        )
        print("You can install it with: pip install pylint")
        sys.exit(1)


if __name__ == "__main__":
    # Get arguments from command line or use defaults
    project_name = sys.argv[1] if len(sys.argv) > 1 else "panel"
    source_path = sys.argv[2] if len(sys.argv) > 2 else "."

    generate_diagrams(project_name, source_path)
