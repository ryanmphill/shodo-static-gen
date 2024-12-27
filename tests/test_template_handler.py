"""Tests for the template_handler module."""

import os
from shodo_ssg.template_handler import TemplateHandler


def test_template_handler_init(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the __init__ method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    assert template_handler.template_env
    assert template_handler.build_dir
    assert template_handler.root_path
    assert template_handler.markdown_loader
    assert template_handler.json_loader


def test_template_handler_render_args(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the render_args property of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    assert template_handler.render_args
    assert isinstance(template_handler.render_args, dict)
    assert "metadata" in template_handler.render_args
    assert "title" in template_handler.render_args["metadata"]
    assert "description" in template_handler.render_args["metadata"]
    assert "author" in template_handler.render_args["metadata"]
    assert "short" in template_handler.render_args
    assert "collections" in template_handler.render_args
    assert "another_short" in template_handler.render_args["collections"]
    assert "list_of_words" in template_handler.render_args
    assert "home_page_title" in template_handler.render_args


def test_template_handler_md_pages(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the md_pages property of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    assert template_handler.md_pages
    assert isinstance(template_handler.md_pages, list)
    assert template_handler.md_pages[0]
    assert isinstance(template_handler.md_pages[0], dict)
    assert "html" in template_handler.md_pages[0]
    assert "url_segment" in template_handler.md_pages[0]
    assert "name" in template_handler.md_pages[0]


def test_template_handler_update_render_arg(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the update_render_arg method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    key = "test_key"
    value = "test_value"

    assert key not in template_handler.render_args

    template_handler.update_render_arg(key, value)

    assert key in template_handler.render_args
    assert template_handler.render_args[key] == value


def test_template_handler_get_template(
    template_handler_dependencies,
    temp_project_path,
):  # pylint: disable=redefined-outer-name
    """Test the get_template method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    view_path = os.path.join(temp_project_path, "src/theme/views/")

    template_name = "hello_world.jinja"
    template_contents = "<div>Hello, World!</div>"
    template_path = os.path.join(view_path, template_name)

    with open(template_path, "w", encoding="utf-8") as template_file:
        template_file.write(template_contents)

    assert template_handler.get_template(template_name)
    assert template_handler.get_template(template_name).name == template_name
    assert hasattr(template_handler.get_template(template_name), "render")
    rendered_template = template_handler.get_template(template_name).render()
    assert isinstance(rendered_template, str)
    assert rendered_template == template_contents


def test_template_handler_write_home_template(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the write_home_template method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    if not os.path.exists(template_handler.build_dir):
        os.makedirs(template_handler.build_dir)

    template_handler.write_home_template()

    assert os.path.exists(f"{template_handler.build_dir}/index.html")
    with open(
        f"{template_handler.build_dir}/index.html", "r", encoding="utf-8"
    ) as index_file:
        index_contents = index_file.read()
    assert index_contents
    assert "<!DOCTYPE html>" in index_contents


def test_template_handler_write_linked_template_pages(
    template_handler_dependencies,
    settings_dict,
):  # pylint: disable=redefined-outer-name
    """Test the write_linked_template_pages method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    # Get the source paths for the linked page directories
    linked_page_paths = get_linked_page_relative_build_paths(
        settings_dict["template_paths"]
    )

    # Make sure the build directory exists
    if not os.path.exists(template_handler.build_dir):
        os.makedirs(template_handler.build_dir)

    template_handler.write_linked_template_pages()

    for path in linked_page_paths:
        assert os.path.exists(f"{template_handler.build_dir}/{path}/index.html")
        with open(
            f"{template_handler.build_dir}/{path}/index.html", "r", encoding="utf-8"
        ) as page_file:
            page_contents = page_file.read()
        assert page_contents
        assert "<!DOCTYPE html>" in page_contents


def test_template_handler_write_article_pages(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the write_article_pages method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    if not os.path.exists(template_handler.build_dir):
        os.makedirs(template_handler.build_dir)

    template_handler.write_article_pages()

    for md_page in template_handler.md_pages:
        build_path = os.path.join(
            template_handler.build_dir,
            md_page["url_segment"].strip("/"),
            md_page["name"].strip("/"),
        )
        assert os.path.exists(build_path)
        assert os.path.exists(f"{build_path}/index.html")
        with open(f"{build_path}/index.html", "r", encoding="utf-8") as page_file:
            page_contents = page_file.read()
        assert page_contents
        assert "<!DOCTYPE html>" in page_contents
        assert md_page["html"] in page_contents


def test_template_handler_get_md_layout_template_defaults_to_root_layout(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the get_md_layout_template method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    url_segment = "test_url_segment"

    assert template_handler.get_md_layout_template(url_segment)
    assert (
        template_handler.get_md_layout_template(url_segment) == "articles/layout.jinja"
    )


def test_template_handler_get_md_layout_template_returns_matching_layout(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the get_md_layout_template method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    test_article_path = os.path.join(
        template_handler.root_path, "src/theme/markdown/articles/test_dir/"
    )
    test_layout_path = os.path.join(
        template_handler.root_path, "src/theme/views/articles/test_dir/"
    )
    test_article_name = "test_article.md"

    # Create a test article md and layout template that should be matched to the article md
    os.mkdir(test_article_path)
    with open(
        os.path.join(test_article_path, test_article_name), "w", encoding="utf-8"
    ) as article_file:
        article_file.write("Test article content")
    os.mkdir(test_layout_path)
    with open(
        os.path.join(test_layout_path, "layout.jinja"), "w", encoding="utf-8"
    ) as layout_file:
        layout_file.write(r"<div>Test layout content: {{ article }}</div>")

    url_segment = "test_dir"
    layout = "articles/test_dir/layout.jinja"

    assert template_handler.get_md_layout_template(url_segment)
    assert template_handler.get_md_layout_template(url_segment) == layout


def test_template_handler_write(
    template_handler_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the write method of the TemplateHandler class."""
    settings, markdown_loader, json_loader = template_handler_dependencies
    template_handler = TemplateHandler(settings, markdown_loader, json_loader)

    if not os.path.exists(template_handler.build_dir):
        os.makedirs(template_handler.build_dir)

    template_handler.write()

    # Check that the home page was written
    assert os.path.exists(f"{template_handler.build_dir}/index.html")
    with open(
        f"{template_handler.build_dir}/index.html", "r", encoding="utf-8"
    ) as index_file:
        index_contents = index_file.read()
    assert index_contents
    assert "<!DOCTYPE html>" in index_contents
    # Check that the linked pages were written
    linked_page_paths = get_linked_page_relative_build_paths(settings["template_paths"])
    for path in linked_page_paths:
        assert os.path.exists(f"{template_handler.build_dir}/{path}/index.html")
        with open(
            f"{template_handler.build_dir}/{path}/index.html", "r", encoding="utf-8"
        ) as page_file:
            page_contents = page_file.read()
        assert page_contents
        assert "<!DOCTYPE html>" in page_contents
    # Check that the article pages were written
    for md_page in template_handler.md_pages:
        build_path = os.path.join(
            template_handler.build_dir,
            md_page["url_segment"].strip("/"),
            md_page["name"].strip("/"),
        )
        assert os.path.exists(build_path)
        assert os.path.exists(f"{build_path}/index.html")
        with open(f"{build_path}/index.html", "r", encoding="utf-8") as page_file:
            page_contents = page_file.read()
        assert page_contents
        assert "<!DOCTYPE html>" in page_contents
        assert md_page["html"] in page_contents


def get_linked_page_relative_build_paths(template_paths: list[str]):
    """Returns the expected relative paths to the linked template pages in the build directory"""
    # Get the source paths for the linked page directories
    linked_page_dirs: list[str] = []
    for path in template_paths:
        if "src/theme/views/pages/" in path:
            linked_page_dirs.append(path)
    # Get the source paths for the linked page template files
    linked_page_paths = []
    for path in linked_page_dirs:
        # get the file in the directory
        for file in os.listdir(path):
            if (
                file.endswith(".jinja")
                or file.endswith(".j2")
                or file.endswith(".jinja2")
            ):
                relative_path = (
                    path.split("src/theme/views/pages/")[-1].strip("/")
                    + "/"
                    + os.path.splitext(file)[0]
                )
                linked_page_paths.append(relative_path.strip("/"))

    return linked_page_paths
