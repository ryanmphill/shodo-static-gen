"""
This module combines all needed components to render templates and static assets to
the destination directory
"""

import os
import shutil

from .template_handler import TemplateHandler
from .data_loader import Loader
from .asset_writer import AssetHandler


class StaticSiteGenerator:
    """
    Handles generating a static website in the destination directory by combining components needed
    to render templates and static assets.
    """

    def __init__(
        self,
        template_handler: TemplateHandler,
        loader: Loader,
        asset_handler: AssetHandler,
    ):
        """
        Initializes the StaticSiteGenerator with the necessary components
        for generating a static site.

        :param template_handler: An instance of TemplateHandler for managing templates.
        :param loader: An instance of Loader for loading markdown and JSON content.
        :param asset_handler: An instance of AssetHandler for writing static assets.
        """
        self.template_handler = template_handler
        self.loader = loader
        self.asset_handler = asset_handler
        self.build_dir = template_handler.build_dir
        self.root_path = template_handler.root_path

    def get_build_dir_path(self):
        """
        Constructs the absolute path of the build directory from the project root
        """
        return os.path.join(self.root_path, self.build_dir)

    def clear_build_dir(self):
        """
        Removes the current build directory
        """
        build_dir_path = self.get_build_dir_path()
        if os.path.exists(build_dir_path):
            # If build directory exists, clear it
            shutil.rmtree(build_dir_path)

    def refresh_and_create_new_build_dir(self):
        """
        Clears build directory if exists and creates a new one
        """
        build_dir_path = self.get_build_dir_path()
        self.clear_build_dir()
        os.makedirs(build_dir_path)

    def build(self):
        """
        Builds the static site by combining templates, markdown content,
        JSON arguments, and static assets.

        This method performs the following steps:
        1. Reads markdown files and converts them to HTML.
        2. Loads JSON configuration and data.
        3. Clears the destination directory and creates a new one.
        4. Writes the favicon, index.html, and linked HTML pages.
        5. Copies scripts, assets, and combines all stylesheets into one file.
        """
        # Load render arguments
        render_args = {}
        render_args.update(self.loader.markdown.load_args())
        render_args.update(self.loader.json.load_args())

        # Load markdown pages
        md_pages = self.loader.markdown.load_pages()

        # Clear destination directory if exists and create new empty directory
        self.refresh_and_create_new_build_dir()

        self.asset_handler.favicon.write()
        self.template_handler.write(render_args, md_pages)
        self.asset_handler.scripts.write()
        self.asset_handler.images.write()
        self.asset_handler.styles.write()
        print("\033[92m" + "Site build successfully completed!" + "\033[0m")
