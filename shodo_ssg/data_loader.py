"""
Classes defined in this module are responsible for loading data
from files
"""

import logging
import os
from json import load
from abc import ABC, abstractmethod
from io import TextIOWrapper
from typing import TypedDict
from markdown2 import markdown


class SettingsDict(TypedDict):
    """
    Schema for settings dictionary loaded from build_settings.json
    """

    template_paths: list[str]
    root_path: str
    build_dir: str
    markdown_path: str
    json_config_path: str
    favicon_path: str
    scripts_path: str
    images_path: str
    styles_path: str
    build_dir: str


class DataLoader(ABC):
    """
    Abstract base class for loading data from files.
    """

    def __init__(self, src_path: str):
        """
        Initializes the DataLoader with a specified path to the data, which
        could include Markdown files or JSON
        """
        self.src_path = src_path

    def list_files(self):
        """
        List all files in the path specified during class initialization
        """
        files = []
        # Append all files if src_path is directory
        if os.path.isdir(self.src_path):
            for file in os.listdir(self.src_path):
                files.append(file)
        # Append single file if src_path is file
        if os.path.isfile(self.src_path):
            files.append(self.src_path)
        return files

    @abstractmethod
    def load_args(self):
        """
        Load data from the specified file path.
        This method must be implemented by subclasses.
        """


class MarkdownLoader(DataLoader):
    """
    Handles the loading of markdown files as well as their conversion to html
    strings. Extends DataLoader
    """

    def __init__(self, settings: SettingsDict):
        """
        Extends the DataLoader with the path to the markdown directory pulled from
        the settings dictionary
        """
        super().__init__(settings["markdown_path"])
        self.root_path = settings["root_path"]

    def list_files(self, sub_dir="partials") -> list[tuple[str]]:
        """
        Lists all markdown files in the root path specified during class initialization. Returns
        list of tuple pairs packed with the directory path followed by the file name.
        """
        md_files = []
        md_dirs = self._get_nested_markdown_dirs(os.path.join(self.src_path, sub_dir))
        for md_dir_path in md_dirs:
            for file in os.listdir(md_dir_path):
                if file.endswith(".md"):
                    md_files.append((md_dir_path, file))
        return md_files

    def _log_info(self):
        """
        Prints a status message that markdown files are being read and loaded
        """
        logging.info("\033[94mReading markdown files...\033[0m")

    def _convert_to_html(self, markdown_file: TextIOWrapper) -> str:
        """
        Takes an open markdown file and converts it to an html string
        """
        return markdown(
            markdown_file.read(), extras=["fenced-code-blocks", "code-friendly"]
        )

    def load_args(self):
        """
        Load html converted from markdown files as a dictionary of render arguments,
        where the key is the name of the markdown file, and the value is the converted
        html string to be inserted in the templates.
        """
        self._log_info()
        converted_html = {}
        for md_dir_path, md_file in self.list_files():
            md_file_path = os.path.join(md_dir_path, md_file)
            md_var_name = os.path.splitext(md_file)[0]
            # Get the relative path from the markdown directory
            relative_paths = md_dir_path.replace("src/theme/markdown/partials/", "")
            # Split the relative path into a list of prefixes to append to md variable names
            name_prefixes = [s for s in relative_paths.split("/") if s]
            # Open and convert markdown file to html
            with open(md_file_path, "r", encoding="utf-8") as markdown_file:
                if not name_prefixes:
                    converted_html[md_var_name] = self._convert_to_html(markdown_file)
                else:
                    # Use nested directories as prefixes for the variable name
                    # ex. "collections/quote.md" -> {"collections": {"quote": "<html>"}}
                    # which will be exposed in the template as {{ collections.quote }}
                    keychain = converted_html
                    for prefix in name_prefixes:
                        if prefix not in keychain:
                            keychain[prefix] = {}
                        keychain = keychain[prefix]
                        if name_prefixes[-1] == prefix:
                            if isinstance(keychain, dict):
                                keychain[md_var_name] = self._convert_to_html(
                                    markdown_file
                                )

        return converted_html

    def load_pages(self) -> list[dict[str, str]]:
        """
        Load html for markdown articles and prepare data for each to be loaded
        as a separate page. Returns list of dictionaries with the following
        key/value pairs:
            `"html"`: The full converted html string,
            `"url_segment"`: The path to the markdown file from the markdown/articles directory,
                            used for matching a layout template to the `.md` file
            `"name"`: The name of the file, minus the extension
        """
        markdown_pages = []
        for md_dir_path, md_file in self.list_files("articles"):
            page = {}
            md_file_path = os.path.join(md_dir_path, md_file)
            with open(md_file_path, "r", encoding="utf-8") as markdown_file:
                page["html"] = self._convert_to_html(markdown_file)
            page["url_segment"] = md_dir_path.replace("src/theme/markdown/articles", "")
            page["name"] = os.path.splitext(md_file)[0]
            markdown_pages.append(page)
        return markdown_pages

    def _get_nested_markdown_dirs(
        self, markdown_path="src/theme/markdown/partials", markdown_dirs=None
    ) -> list[str]:
        """
        Retrieves all children directories of a parent markdown directory as a list
        """
        markdown_path = markdown_path.rstrip("/") + "/"

        if markdown_dirs is None:
            markdown_dirs = []

        markdown_dirs.append(markdown_path)
        for path in os.listdir(markdown_path):
            path_from_root = os.path.join(self.root_path, markdown_path + path)
            # For each directory, recursively append all a nested directories
            if os.path.isdir(path_from_root):
                markdown_dirs = self._get_nested_markdown_dirs(
                    markdown_path + path, markdown_dirs
                )
        # When no subdirectories remain, return list of markdown directories
        return markdown_dirs


class JSONLoader(DataLoader):
    """
    Handles the loading of JSON key value pairs to be inserted into
    templates as dictionary render arguments
    """

    def __init__(self, settings: SettingsDict):
        """
        Extends the DataLoader with the path to the JSON config file pulled from
        the settings dictionary
        """
        super().__init__(settings["json_config_path"])
        self.root_path = settings["root_path"]

    def list_files(self, sub_dir="") -> list[tuple[str]]:
        """
        Lists all JSON files in the root path specified during class initialization. Returns
        list of tuple pairs packed with the directory path followed by the file name.
        """
        json_files = []
        json_dirs = self._get_nested_json_dirs(os.path.join(self.src_path, sub_dir))
        for json_dir_path in json_dirs:
            for file in os.listdir(json_dir_path):
                if file.endswith(".json"):
                    json_files.append((json_dir_path, file))
        return json_files

    def _log_info(self):
        """
        Prints a status message that JSON is being loaded
        """
        logging.info("\033[94mLoading JSON...\033[0m")

    def load_args(self):
        """
        Load JSON from the specified file path as a Python dict, where the key is the
        variable name in the template files, and the value is the data to be inserted.
        """
        self._log_info()
        loaded_args = {}
        for json_dir_path, json_file in self.list_files():
            json_file_path = os.path.join(json_dir_path, json_file)
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                converted_json: dict = load(json_file)
                loaded_args.update(converted_json)

        return loaded_args

    def _get_nested_json_dirs(
        self, json_path="src/theme/json", json_dirs=None
    ) -> list[str]:
        """
        Retrieves all children directories of a parent JSON directory as a list
        """
        json_path = json_path.rstrip("/") + "/"

        if json_dirs is None:
            json_dirs = []

        json_dirs.append(json_path)
        for path in os.listdir(json_path):
            path_from_root = os.path.join(self.root_path, json_path + path)
            # For each directory, recursively append all a nested directories
            if os.path.isdir(path_from_root):
                json_dirs = self._get_nested_json_dirs(json_path + path, json_dirs)
        # When no subdirectories remain, return list of JSON directories
        return json_dirs


class SettingsLoader(DataLoader):
    """
    Handles the loading of build settings, including source paths and the
    destination build directory
    """

    def __init__(self, root_path: str):
        """
        Extends the JSONLoader with the absolute path to the build settings
        as an argument.
        """
        super().__init__(src_path=os.path.join(root_path, "build_settings.json"))
        self._data = None
        self.root_path = root_path

    @property
    def data(self):
        """
        The loaded arguments from the build settings json config file
        """
        if self._data is None:
            self._data = self.load_args()
            self._data["template_paths"] = self.get_all_template_paths(
                self._data["root_template_paths"]
            )
            self._data["root_path"] = self.root_path
            self._data["build_dir"] = self._format_build_dir()

        args: SettingsDict = self._data
        return args

    def load_args(self):
        """
        Load JSON from the specified file path as a Python dict, where the key is the
        variable name in the template files, and the value is the data to be inserted.
        """
        with open(self.src_path, "r", encoding="utf-8") as settings_file:
            settings = load(settings_file)

        if isinstance(settings, dict):
            return settings

        return {}

    def _log_info(self):
        """
        Prints a status message that JSON settings are being loaded
        """
        logging.info("\033[94mLoading settings and configuration...\033[0m")

    def _format_build_dir(self):
        """
        Returns the build directory from the build_settings.json with
        any trailing slashes removed
        """
        build_dir = self._data["build_dir"]
        if isinstance(build_dir, str):
            build_dir = build_dir.strip("/")
        else:
            build_dir = ""

        return build_dir

    def get_nested_template_dirs(
        self, template_path="src/theme/views/", template_dirs=None
    ):
        """
        Retrieves all children directories of a parent template directory as a list
        """
        template_path = template_path.rstrip("/") + "/"

        if template_dirs is None:
            template_dirs = []

        template_dirs.append(template_path)
        for path in os.listdir(template_path):
            path_from_root = os.path.join(self.root_path, template_path + path)
            # For each directory, recursively append all a nested directories
            if os.path.isdir(path_from_root):
                template_dirs = self.get_nested_template_dirs(
                    template_path + path, template_dirs
                )
        # When no subdirectories remain, return list of template directories
        return template_dirs

    def get_all_template_paths(self, root_template_paths: list[str]):
        """
        Retrieves a list of all nested template paths for each defined root template path
        """
        template_paths = []
        for path in root_template_paths:
            template_paths.extend(self.get_nested_template_dirs(path))

        return template_paths
