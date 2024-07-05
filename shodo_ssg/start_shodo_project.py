"""
This module provides a script to scaffold a new static site project using Shodo.

The script takes command-line arguments to specify the project name and the template folder to use.
It creates a new project directory with the specified name and copies the files and folders from the 
template directory into it.

Usage:
    python start_shodo_project.py <project_name> [-t <template_folder>]

Arguments:
    project_name (str): The name of the project. If not provided, the default name is 
    'new_shodo_project'.
    -t, --template (str): The template folder to use. If not provided, the default template 
    folder is 'project_template'.

Example:
    python start_shodo_project.py my_project -t my_template

Note:
    - If you want to start a project in the current directory, specify the project name 
    as a period '.'.
    - The template folder should exist in the same directory as this script.

Author: Your Name
Date: Today's Date
"""

import sys
import os
import argparse
import shutil

# Globals
cwd = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))


def start_shodo_project(_argv):
    """
    Main entry point for the script to scaffold a new static site project.
    """
    # Arguments
    parser = argparse.ArgumentParser(description="Scaffold a Static Site Project.")
    parser.add_argument(
        "project_name", help="The name of the project", default="new_shodo_project"
    )
    parser.add_argument(
        "-t",
        "--template",
        help="The template folder to use.",
        default="project_template",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        if len(sys.argv) < 2:
            print(
                "If you want to start a project in the current directory, specify with a period '.'"
            )
            sys.exit(1)

    # Variables
    project_name = args.project_name
    full_path = os.path.join(cwd, project_name)
    template_dir = os.path.join(script_dir, args.template)

    # Ensure the template exists
    if not os.path.exists(template_dir):
        print(f"Template '{args.template}' does not exist.")
        sys.exit(1)

    # Copy files and folders
    shutil.copytree(template_dir, full_path, dirs_exist_ok=True)

    print(f"\033[92mProject created successfully at '{full_path}'.")


if __name__ == "__main__":
    start_shodo_project(sys.argv)
