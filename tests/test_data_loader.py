"""Tests for the data_loader module."""

import json
import os

from shodo_ssg.data_loader import (
    MarkdownLoader,
    JSONLoader,
    SettingsLoader,
)


def test_markdown_loader_list_files(
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test the list_files method of the MarkdownLoader class."""
    loader = MarkdownLoader(settings_dict)
    files = loader.list_files()
    assert isinstance(files, list)
    assert isinstance(files[0], tuple)
    md_path, md_file_name = files[0]
    assert "src/theme/markdown/" in md_path
    assert md_file_name.endswith(".md")


def test_markdown_loader_load_args(
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test the load_args method of the MarkdownLoader class."""
    loader = MarkdownLoader(settings_dict)
    args = loader.load_args()
    assert isinstance(args, dict)


def test_markdown_loader_load_pages(
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test the load_pages method of the MarkdownLoader class."""
    loader = MarkdownLoader(settings_dict)
    pages = loader.load_pages()
    assert isinstance(pages, list)


def test_json_loader_list_files(
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test the list_files method of the JSONLoader class."""
    loader = JSONLoader(settings_dict)
    files = loader.list_files()
    json_path, json_file_name = files[0]
    assert isinstance(files, list)
    assert isinstance(files[0], tuple)
    assert "src/store/" in json_path
    assert json_file_name.endswith(".json")


def test_json_loader_load_args(
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test the load_args method of the JSONLoader class."""
    loader = JSONLoader(settings_dict)
    args = loader.load_args()
    assert isinstance(args, dict)


def test_json_loader_load_args_handles_head_extra_metadata(
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test that JSONLoader correctly loads head_extra metadata."""
    loader = JSONLoader(settings_dict)
    args = loader.load_args()
    config = args.get("config", {})
    metadata = config.get("metadata", {})
    assert isinstance(metadata, dict)
    assert "head_extra" in metadata
    head_extra = metadata["head_extra"]
    assert isinstance(head_extra, list)
    assert len(head_extra) == 8  # There are 8 elements in the head_extra list

    assert " ".join(
        head_extra[0].strip().replace("\n", "").replace("\t", "").split()
    ) == " ".join(
        '<script type="application/ld+json">{\n'
        '                "@context": "https://schema.org",\n'
        '                "@type": "Article",\n'
        '                "headline": "LD+JSON Article",\n'
        '                "description": "This article has ld+json in head extra."\n'
        "            }</script>".strip().replace("\n", "").replace("\t", "").split()
    )
    assert " ".join(
        head_extra[1].strip().replace("\n", "").replace("\t", "").split()
    ) == " ".join(
        '<script type="application/ld+json">{\n'
        '                "@context": "https://schema.org",\n'
        '                "@type": "Article",\n'
        '                "headline": "LD+JSON Article",\n'
        '                "description": "This article has ld+json in head extra."\n'
        "            }</script>".strip().replace("\n", "").replace("\t", "").split()
    )
    assert " ".join(
        head_extra[2].strip().replace("\n", "").replace("\t", "").split()
    ) == " ".join(
        '<script type="application/ld+json">{\n'
        '                "@context": "https://schema.org",\n'
        '                "@type": "Article",\n'
        '                "headline": "LD+JSON Article",\n'
        '                "description": "This article has ld+json in head extra."\n'
        "            }</script>".strip().replace("\n", "").replace("\t", "").split()
    )

    # Also assert the remaining elements are rendered correctly in double quotes
    assert " ".join(
        head_extra[3].strip().replace("\n", "").replace("\t", "").split()
    ) == " ".join(
        (
            '<link rel="icon" href="/static/images/favicons/site-favicon-light.ico"'
            + ' type="image/x-icon" media="(prefers-color-scheme: light)">'
        )
        .strip()
        .replace("\n", "")
        .replace("\t", "")
        .split()
    )
    assert " ".join(
        head_extra[4].strip().replace("\n", "").replace("\t", "").split()
    ) == " ".join(
        (
            '<link rel="icon" href="/static/images/favicons/site-favicon-dark.ico"'
            + ' type="image/x-icon" media="(prefers-color-scheme: dark)">'
        )
        .strip()
        .replace("\n", "")
        .replace("\t", "")
        .split()
    )
    assert " ".join(
        head_extra[5].strip().replace("\n", "").replace("\t", "").split()
    ) == " ".join(
        '<link rel="apple-touch-icon" href="/static/images/favicons/site-favicon-dark.png">'.strip()
        .replace("\n", "")
        .replace("\t", "")
        .split()
    )
    assert " ".join(
        head_extra[6].strip().replace("\n", "").replace("\t", "").split()
    ) == " ".join(
        '<script type="text/javascript" src="/static/scripts/theme-loader.js"></script>'.strip()
        .replace("\n", "")
        .replace("\t", "")
        .split()
    )
    assert " ".join(
        head_extra[7].strip().replace("\n", "").replace("\t", "").split()
    ) == " ".join(
        '<link rel="stylesheet" href="/static/styles/extra-styles.css">'.strip()
        .replace("\n", "")
        .replace("\t", "")
        .split()
    )


def test_json_loader_load_args_handles_quotes_in_values(
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test that JSONLoader correctly loads JSON with quotes in values."""
    loader = JSONLoader(settings_dict)
    args = loader.load_args()
    quotes = args.get("quotes", {})
    assert isinstance(quotes, dict)
    assert "quote" in quotes
    assert quotes["quote"] == "She said, 'This is a great article!' and smiled."
    assert "another_quote" in quotes
    assert quotes["another_quote"] == 'He replied, "Indeed, it is!"'
    assert "third_quote" in quotes
    assert quotes["third_quote"] == 'She said, "Let\'s test quotes!"'
    assert "fourth_quote" in quotes
    assert quotes["fourth_quote"] == 'He responded, "Let\'s do it!"'


def test_settings_loader_data(
    temp_project_path,
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test the data attribute of the SettingsLoader class."""
    temp_abs_path = os.path.abspath(temp_project_path)
    loader = SettingsLoader(temp_abs_path)
    data = loader.data

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


def test_settings_loader_load_args(
    temp_project_path,
):  # pylint: disable=redefined-outer-name
    """Test the load_args method of the SettingsLoader class."""
    temp_abs_path = os.path.abspath(temp_project_path)
    loader = SettingsLoader(temp_abs_path)
    args = loader.load_args()
    settings_path = os.path.join(temp_project_path, "build_settings.json")
    with open(settings_path, "r", encoding="utf-8") as settings_file:
        test_settings = json.load(settings_file)

    assert isinstance(args, dict)
    assert args["build_dir"] == test_settings["build_dir"]
    assert args["markdown_path"] == test_settings["markdown_path"]
    assert args["json_config_path"] == test_settings["json_config_path"]
    assert args["favicon_path"] == test_settings["favicon_path"]
    assert args["scripts_path"] == test_settings["scripts_path"]
    assert args["images_path"] == test_settings["images_path"]
    assert args["styles_path"] == test_settings["styles_path"]
