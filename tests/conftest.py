"""Pytest global fixtures and configuration for the shodo_ssg package."""

import json
import os
import shutil
import pytest

from shodo_ssg.api import API
from shodo_ssg.data_loader import (
    SettingsDict,
    MarkdownLoader,
    JSONLoader,
)

from shodo_ssg.front_matter_processor import FrontMatterProcessor
from shodo_ssg.html_root_layout_builder import HTMLRootLayoutBuilder
from shodo_ssg.pagination_handler import PaginationHandler
from shodo_ssg.template_context import TemplateContext
from shodo_ssg.template_handler import TemplateHandler

from shodo_ssg.asset_writer import (
    FaviconWriter,
    ScriptWriter,
    ImageWriter,
    CSSWriter,
    AssetHandler,
)


@pytest.fixture
def temp_project_path(tmp_path):
    """
    Create a copy of the project_template directory tree in the temporary testing directory
    and return the path.
    """
    temp_path = tmp_path / "project_template"
    temp_path.mkdir()
    # Create a copy of the project_template directory
    src_dir = "shodo_ssg/project_template"
    dest_dir = os.path.abspath(temp_path)
    # Copy files and folders
    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)

    # Replace the existing settings.json file with test settings that use the tmp_path
    test_settings = create_test_build_settings_from_temp_path(temp_path)

    settings_file = os.path.join(dest_dir, "build_settings.json")
    if os.path.exists(settings_file):
        os.remove(settings_file)
    with open(settings_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(test_settings))

    yield temp_path

    # Remove the project_template directory
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)


@pytest.fixture
def settings_dict(temp_project_path):  # pylint: disable=redefined-outer-name
    """
    Create a dictionary of settings for testing. This should be the equivalent of the dictionary
    returned when accessing the data property of the SettingsLoader class instance. The SettingsDict
    type is used to instantiate several classes in the shodo_ssg package. It is similar in structure
    to the build_settings.json file, but includes all nested template directory paths as well as the
    root_path.
    """
    temp_abs_path = os.path.abspath(temp_project_path)
    return SettingsDict(
        {
            "template_paths": [
                os.path.join(temp_project_path, "src/theme/views/"),
                os.path.join(temp_project_path, "src/theme/views/articles/"),
                os.path.join(temp_project_path, "src/theme/views/articles/blog/"),
                os.path.join(
                    temp_project_path, "src/theme/views/articles/blog/subject/"
                ),
                os.path.join(temp_project_path, "src/theme/views/articles/newsletter/"),
                os.path.join(temp_project_path, "src/theme/views/pages/"),
                os.path.join(temp_project_path, "src/theme/views/pages/nested-route/"),
                os.path.join(
                    temp_project_path,
                    "src/theme/views/pages/nested-route/double-nested-route/",
                ),
                os.path.join(temp_project_path, "src/theme/views/partials/"),
            ],
            "root_path": temp_abs_path,
            "build_dir": os.path.join(temp_project_path, "dist"),
            "markdown_path": os.path.join(temp_project_path, "src/theme/markdown"),
            "json_config_path": os.path.join(temp_project_path, "src/store"),
            "favicon_path": os.path.join(temp_project_path, "src/favicon.ico"),
            "scripts_path": os.path.join(temp_project_path, "src/theme/static/scripts"),
            "images_path": os.path.join(temp_project_path, "src/theme/static/images"),
            "styles_path": os.path.join(temp_project_path, "src/theme/static/styles"),
        }
    )


@pytest.fixture
def front_matter_processor_dependencies(
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """
    Create the dependencies for the FrontMatterProcessor class.
    """
    json_loader = JSONLoader(settings_dict)
    return json_loader


@pytest.fixture
def template_context_dependencies(
    settings_dict,
    front_matter_processor_dependencies,
):  # pylint: disable=redefined-outer-name
    """
    Create the dependencies for the TemplateContext class.
    """
    markdown_loader = MarkdownLoader(settings_dict)
    json_loader = front_matter_processor_dependencies
    front_matter_processor = FrontMatterProcessor(json_loader)
    return markdown_loader, json_loader, front_matter_processor


@pytest.fixture
def template_handler_dependencies(
    settings_dict, template_context_dependencies
):  # pylint: disable=redefined-outer-name
    """
    Create the dependencies for the TemplateHandler class.
    """
    root_layout_builder = HTMLRootLayoutBuilder()
    markdown_loader, json_loader, front_matter_processor = template_context_dependencies
    template_context = TemplateContext(
        markdown_loader, json_loader, front_matter_processor
    )
    api = API(template_context, front_matter_processor)
    pagination_handler = PaginationHandler(template_context, root_layout_builder, api)
    return SettingsDict(settings_dict), root_layout_builder, pagination_handler, api


@pytest.fixture
def static_site_generator_deps(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """
    Create the dependencies for the StaticSiteGenerator class.
    """
    settings, root_layout_builder, pagination_handler, api = (
        template_handler_dependencies
    )
    template_handler = TemplateHandler(
        settings, root_layout_builder, pagination_handler, api
    )
    favicon_writer = FaviconWriter(settings)
    script_writer = ScriptWriter(settings)
    image_writer = ImageWriter(settings)
    css_writer = CSSWriter(settings)
    asset_handler = AssetHandler(
        favicon_writer, script_writer, image_writer, css_writer
    )
    return template_handler, asset_handler


def create_test_build_settings_from_temp_path(temp_path):
    """Create a dictionary of settings for testing."""
    return {
        "root_template_paths": [f"{os.path.join(temp_path, 'src/theme/views')}"],
        "markdown_path": f"{os.path.join(temp_path, 'src/theme/markdown')}",
        "json_config_path": f"{os.path.join(temp_path, 'src/store')}",
        "favicon_path": f"{os.path.join(temp_path, 'src/favicon.ico')}",
        "scripts_path": f"{os.path.join(temp_path, 'src/theme/static/scripts')}",
        "images_path": f"{os.path.join(temp_path, 'src/theme/static/images')}",
        "styles_path": f"{os.path.join(temp_path, 'src/theme/static/styles')}",
        "build_dir": f"{os.path.join(temp_path, 'dist')}",
    }
