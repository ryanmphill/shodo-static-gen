"""
This module is responsible for writing static assets, including
styles, scripts, and images to the destination build directory
"""

from dataclasses import dataclass
import os
import shutil


class AssetWriter:
    """
    Base class for writing and compiling static assets that are to be included in the final build
    """

    def __init__(self, src_path: str, destination_path: str):
        self.src_path = src_path
        self.destination_path = destination_path

    def log_info(self):
        """
        Prints a status message that the file writing operation is taking place
        """
        print(
            "\033[94m"
            + f"Copying contents from {self.src_path} to {self.destination_path}..."
            + "\033[0m"
        )

    def write(self):
        """
        Copies contents of either a single file OR an entire directory from the
        provided source path to the destination path.
        """
        self.log_info()
        if os.path.isfile(self.src_path):
            shutil.copyfile(self.src_path, self.destination_path)
        if os.path.isdir(self.src_path):
            shutil.copytree(self.src_path, self.destination_path)


class CSSWriter(AssetWriter):
    """
    Handles writing all CSS files to the destination directory as a single CSS file
    """

    def log_info(self):
        """
        Prints a status message that the css file writing operation is taking place
        """
        print(
            "\033[94m"
            + f"Combining all stylesheets from {self.src_path} "
            + f"to {self.destination_path.rstrip('/')}/main.css..."
            + "\033[0m"
        )

    def write(self):
        """
        Combines all CSS files and writes to the destination directory
        """
        self.log_info()
        destination_path = self.destination_path.rstrip("/") + "/"
        os.makedirs(destination_path)
        css_files = []

        for file in os.listdir(self.src_path):
            if file.endswith(".css"):
                css_files.append(file)

        with open(f"{destination_path}main.css", "w", encoding="utf-8") as outfile:
            for index, css_file in enumerate(css_files):
                css_file_path = os.path.join(self.src_path, css_file)
                with open(css_file_path, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
                # Add a newline character after each file's content, skipping last iteration
                if index < len(css_files) - 1:
                    outfile.write("\n\n")


@dataclass
class AssetHandler:
    """
    Data class that holds logic for writing static site files to the build directory,
    including favicon, scripts, styles, and images
    """

    favicon: AssetWriter
    scripts: AssetWriter
    images: AssetWriter
    styles: CSSWriter
