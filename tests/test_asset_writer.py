"""Tests for the asset_writer module."""

import os
import shutil
from shodo_ssg.asset_writer import (
    BaseAssetWriter,
    FaviconWriter,
    AssetWriter,
    ScriptWriter,
    CSSWriter,
)


def test_base_asset_writer_write(settings_dict):
    """Test the write method of the base BaseAssetWriter Class"""
    dest_path = settings_dict["build_dir"] + "/favicon.ico"

    asset_writer = BaseAssetWriter(settings_dict["favicon_path"], dest_path)

    if not os.path.exists(settings_dict["build_dir"]):
        # Make the dist directory if it doesn't exist
        os.makedirs(settings_dict["build_dir"])

    if os.path.exists(dest_path):
        os.remove(dest_path)
        assert not os.path.exists(dest_path)

    asset_writer.write()

    assert os.path.exists(dest_path)
    assert os.path.isfile(dest_path)


def test_favicon_writer_write(settings_dict):
    """Test the write method of the FaviconWriter class."""
    favicon_writer = FaviconWriter(settings_dict)

    dest_path = settings_dict["build_dir"] + "/favicon.ico"

    if not os.path.exists(settings_dict["build_dir"]):
        # Make the dist directory if it doesn't exist
        os.makedirs(settings_dict["build_dir"])

    if os.path.exists(dest_path):
        os.remove(dest_path)
        assert not os.path.exists(dest_path)

    favicon_writer.write()

    assert os.path.exists(dest_path)
    assert os.path.isfile(dest_path)


def test_script_writer_write(settings_dict):
    """Test the write method of the ScriptWriter class."""
    script_writer = ScriptWriter(settings_dict)

    dest_path = settings_dict["build_dir"] + "/static/scripts"

    if not os.path.exists(settings_dict["build_dir"]):
        # Make the dist directory if it doesn't exist
        os.makedirs(settings_dict["build_dir"])

    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
        assert not os.path.exists(dest_path)

    script_writer.write()

    assert os.path.exists(dest_path)
    assert os.path.isdir(dest_path)


def test_css_writer_write(settings_dict):
    """Test the write method of the CSS writer class"""
    css_writer = CSSWriter(settings_dict)

    dest_path = settings_dict["build_dir"] + "/static/styles"

    if not os.path.exists(settings_dict["build_dir"]):
        # Make the dist directory if it doesn't exist
        os.makedirs(settings_dict["build_dir"])

    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
        assert not os.path.exists(dest_path)

    css_writer.write()

    assert os.path.exists(dest_path)
    assert os.path.isdir(dest_path)


def test_asset_writer_write(settings_dict):
    """Test the write method of the AssetWriter class"""
    asset_writer = AssetWriter(settings_dict)

    dest_path = settings_dict["build_dir"] + "/static/assets"

    if not os.path.exists(settings_dict["build_dir"]):
        # Make the dist directory if it doesn't exist
        os.makedirs(settings_dict["build_dir"])

    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
        assert not os.path.exists(dest_path)

    asset_writer.write()

    assert os.path.exists(dest_path)
    assert os.path.isdir(dest_path)
