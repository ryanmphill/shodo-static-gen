"""
This module is responsible for writing static assets, including
styles, scripts, and images to the destination build directory
"""

from dataclasses import dataclass
import os
import shutil

from shodo_ssg.data_loader import SettingsDict


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


class FaviconWriter(AssetWriter):
    """
    Handles writing the favicon file to the destination directory
    """

    def __init__(self, settings: SettingsDict):
        """
        Initializes the FaviconWriter with the source and destination paths for the favicon
        """
        super().__init__(
            settings["favicon_path"], f"{settings['build_dir']}/favicon.ico"
        )


class ScriptWriter(AssetWriter):
    """
    Handles writing all script files to the destination directory
    """

    def __init__(self, settings: SettingsDict):
        """
        Initializes the ScriptWriter with the source and destination paths for the scripts
        """
        super().__init__(
            settings["scripts_path"], f"{settings['build_dir']}/static/scripts"
        )


class ImageWriter(AssetWriter):
    """
    Handles writing all image files to the destination directory
    """

    def __init__(self, settings: SettingsDict):
        """
        Initializes the ImageWriter with the source and destination paths for the images
        """
        super().__init__(
            settings["images_path"], f"{settings['build_dir']}/static/images"
        )


class CSSWriter(AssetWriter):
    """
    Handles writing all CSS files to the destination directory as a single CSS file
    """

    def __init__(self, settings: SettingsDict):
        """
        Initializes the CSSWriter with the source and destination paths for the stylesheets
        """
        super().__init__(
            settings["styles_path"], f"{settings['build_dir']}/static/styles"
        )

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

    favicon: FaviconWriter
    scripts: ScriptWriter
    images: ImageWriter
    styles: CSSWriter
