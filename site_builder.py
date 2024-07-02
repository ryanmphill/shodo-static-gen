"""
This module builds a static site in the destination directory from jinja2
templates and all static assets
"""

import os
from static_site_builder import (
    TemplateHandler,
    MarkdownLoader,
    JSONLoader,
    SettingsLoader,
    FaviconWriter,
    ScriptWriter,
    ImageWriter,
    CSSWriter,
    AssetHandler,
    StaticSiteGenerator,
)


def load_settings(root_path: str):
    """
    Loads the settings from the settings.json file in the root directory.

    Returns:
        dict: The settings data loaded from the settings.json file
    """
    settings_loader = SettingsLoader(root_path)
    return settings_loader.data


def initialize_components(settings: dict):
    """
    Initializes the components necessary for building the static site.

    Args:
        settings (dict): The settings data loaded from the settings.json file

    Returns:
        Tuple[TemplateHandler, AssetHandler]: A tuple containing the initialized components
    """
    md_loader = MarkdownLoader(settings)
    json_loader = JSONLoader(settings)
    template_handler = TemplateHandler(settings, md_loader, json_loader)
    favicon_writer = FaviconWriter(settings)
    script_writer = ScriptWriter(settings)
    image_writer = ImageWriter(settings)
    css_writer = CSSWriter(settings)

    asset_handler = AssetHandler(
        favicon_writer, script_writer, image_writer, css_writer
    )

    return (template_handler, asset_handler)


def generate_site(template_handler: TemplateHandler, asset_handler: AssetHandler):
    """
    Generates the static site by calling the build method of the StaticSiteGenerator.

    Args:
        template_handler (TemplateHandler): The initialized TemplateHandler
        asset_handler (AssetHandler): The initialized AssetHandler
    """
    site_generator = StaticSiteGenerator(template_handler, asset_handler)
    site_generator.build()


def build_static_site():
    """
    Builds a static site by initializing the necessary components and calling the build method.

    This function sets up the TemplateHandler with the MarkdownLoader and JSONLoader, as well as
    various writers for favicon, scripts, images, and CSS. It then creates a StaticSiteGenerator
    instance and calls its build method to generate the static site.
    """
    # Set the ROOT_PATH variable to the directory of this file
    root_path = os.path.dirname(os.path.abspath(__file__))

    # Load settings
    settings = load_settings(root_path)

    # Initialize components
    template_handler, asset_handler = initialize_components(settings)

    # Build the static site
    generate_site(template_handler, asset_handler)


if __name__ == "__main__":
    build_static_site()
