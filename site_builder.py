"""This module builds a static site in the destination directory from jinja2
templates and all static assets
"""

import os
from static_site_builder import (
    TemplateHandler,
    MarkdownLoader,
    JSONLoader,
    SettingsLoader,
    Loader,
    AssetWriter,
    CSSWriter,
    AssetHandler,
    StaticSiteGenerator,
)


def build_static_site():
    """
    Builds a static site by initializing the necessary components and calling the build method.

    This function sets up the TemplateHandler, MarkdownLoader, JSONLoader, and various writers for
    favicon, scripts, images, and CSS. It then creates a StaticSiteGenerator instance and calls
    its build method to generate the static site.
    """
    # Set the ROOT_PATH environment variable to the directory of this file
    os.environ.setdefault("ROOT_PATH", os.path.dirname(os.path.abspath(__file__)))

    # Load settings
    settings_loader = SettingsLoader()
    args = settings_loader.data
    build_dir = settings_loader.get_build_dir()

    # Initialize components
    template_handler = TemplateHandler(args["template_paths"], build_dir)
    markdown_loader = MarkdownLoader(args["markdown_path"])
    json_loader = JSONLoader(args["json_config_path"])
    favicon_writer = AssetWriter(args["favicon_path"], f"{build_dir}/favicon.ico")
    script_writer = AssetWriter(args["scripts_path"], f"{build_dir}/static/scripts")
    image_writer = AssetWriter(args["images_path"], f"{build_dir}/static/images")
    css_writer = CSSWriter(args["styles_path"], f"{build_dir}/static/styles")

    loader = Loader(markdown_loader, json_loader)
    asset_handler = AssetHandler(
        favicon_writer, script_writer, image_writer, css_writer
    )

    site_generator = StaticSiteGenerator(template_handler, loader, asset_handler)

    # Build the static site
    site_generator.build()


if __name__ == "__main__":
    build_static_site()
