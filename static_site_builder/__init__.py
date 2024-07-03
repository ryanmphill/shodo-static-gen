"""
This package is part of the Shodo Static Site Generator.
It provides the necessary classes and functions for building a static site.

Classes:
- `TemplateHandler`: Handles the rendering of templates.
- `DataLoader`, `MarkdownLoader`, `JSONLoader`, `SettingsLoader` : These 
   classes are responsible for loading data from various sources.
- `FaviconWriter`, `ScriptWriter`, `ImageWriter`, `CSSWriter`: These classes handle
   copying, combining, and writing of various assets.
- `AssetHandler`: Dataclass for holding multiple instances of AssetWriter.
- `StaticSiteGenerator`: This class orchestrates the generation of the static site.

This package is used in the `site_builder.py` script to build the static site.

"""

from .template_handler import TemplateHandler
from .data_loader import DataLoader, MarkdownLoader, JSONLoader, SettingsLoader
from .asset_writer import (
    FaviconWriter,
    ScriptWriter,
    ImageWriter,
    CSSWriter,
    AssetHandler,
)
from .static_site_generator import StaticSiteGenerator
