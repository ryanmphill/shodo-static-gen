"""Tests for the assembler module."""

import os
import shutil
from shodo_ssg.assembler import (
    load_settings,
    initialize_components,
    generate_site,
    build_static_site,
)
from shodo_ssg.template_handler import TemplateHandler
from shodo_ssg.asset_writer import AssetHandler
from tests.build_validation import (
    css_exist_in_build_dir,
    favicon_exists_in_build_dir,
    images_exist_in_build_dir,
    linked_template_pages_exist_in_build_dir,
    markdown_pages_exist_in_build_dir,
    scripts_exist_in_build_dir,
)


def test_load_settings(temp_project_path, settings_dict):
    """Test the load_settings function."""
    temp_abs_path = os.path.abspath(temp_project_path)
    data = load_settings(temp_abs_path)

    assert isinstance(data, dict)
    assert os.path.abspath(data["build_dir"]) == os.path.abspath(
        settings_dict["build_dir"]
    )
    assert data["markdown_path"] == settings_dict["markdown_path"]
    assert data["json_config_path"] == settings_dict["json_config_path"]
    assert data["favicon_path"] == settings_dict["favicon_path"]
    assert data["scripts_path"] == settings_dict["scripts_path"]
    assert data["images_path"] == settings_dict["images_path"]
    assert data["styles_path"] == settings_dict["styles_path"]
    assert set(data["template_paths"]) == set(settings_dict["template_paths"])


def test_initialize_components(settings_dict, static_site_generator_deps):
    """Test the initialize_components function."""
    template_handler = static_site_generator_deps[0]
    components = initialize_components(settings_dict)

    assert isinstance(components, tuple)
    assert isinstance(components[0], TemplateHandler)
    assert isinstance(components[1], AssetHandler)

    assert components[0].build_dir == template_handler.build_dir
    assert components[0].root_path == template_handler.root_path
    assert len(components[0].md_pages) == len(template_handler.md_pages)
    assert set(components[0].render_args.keys()) == set(
        template_handler.render_args.keys()
    )
    assert components[0].markdown_loader
    assert components[0].json_loader
    assert components[1].favicon
    assert components[1].scripts
    assert components[1].images
    assert components[1].styles


def test_generate_site(static_site_generator_deps, settings_dict):
    """Test the generate_site function"""
    template_handler, asset_handler = static_site_generator_deps
    build_path = os.path.abspath(settings_dict["build_dir"])

    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    assert not os.path.exists(build_path)

    generate_site(template_handler, asset_handler)

    assert os.path.exists(build_path)
    assert os.listdir(build_path)
    assert os.path.isdir(build_path)
    assert os.path.exists(os.path.join(build_path, "index.html"))
    assert linked_template_pages_exist_in_build_dir(
        build_path, settings_dict["template_paths"]
    )
    assert markdown_pages_exist_in_build_dir(build_path, template_handler.md_pages)
    assert scripts_exist_in_build_dir(build_path)
    assert css_exist_in_build_dir(build_path)
    assert images_exist_in_build_dir(build_path)
    assert favicon_exists_in_build_dir(build_path)


def test_build_static_site(temp_project_path, template_handler_dependencies):
    """Test the build_static_site function"""
    tmp_proj_root = os.path.abspath(temp_project_path)
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)
    build_path = os.path.abspath(settings["build_dir"])

    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    assert not os.path.exists(build_path)

    build_static_site(tmp_proj_root)

    assert os.path.exists(build_path)
    assert os.listdir(build_path)
    assert os.path.isdir(build_path)
    assert os.path.exists(os.path.join(build_path, "index.html"))
    assert linked_template_pages_exist_in_build_dir(
        build_path, settings["template_paths"]
    )
    assert markdown_pages_exist_in_build_dir(build_path, template_handler.md_pages)
    assert scripts_exist_in_build_dir(build_path)
    assert css_exist_in_build_dir(build_path)
    assert images_exist_in_build_dir(build_path)
    assert favicon_exists_in_build_dir(build_path)
