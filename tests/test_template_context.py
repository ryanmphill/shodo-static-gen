"""Tests for the template_context module."""

from shodo_ssg.template_context import TemplateContext


def test_template_context_init(
    template_context_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the __init__ method of the TemplateHandler class."""
    markdown_loader, json_loader, front_matter_processor = template_context_dependencies
    template_context = TemplateContext(
        markdown_loader, json_loader, front_matter_processor
    )

    assert template_context.markdown_loader
    assert template_context.json_loader
    assert template_context.front_matter_processor


def test_template_context_render_args(
    template_context_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the render_args property of the TemplateHandler class."""
    markdown_loader, json_loader, front_matter_processor = template_context_dependencies
    template_context = TemplateContext(
        markdown_loader, json_loader, front_matter_processor
    )

    assert template_context.render_args
    assert isinstance(template_context.render_args, dict)
    assert "metadata" in template_context.render_args
    assert "title" in template_context.render_args["metadata"]
    assert "description" in template_context.render_args["metadata"]
    assert "author" in template_context.render_args["metadata"]
    assert "short" in template_context.render_args
    assert "collections" in template_context.render_args
    assert "another_short" in template_context.render_args["collections"]
    assert "list_of_words" in template_context.render_args
    assert "home_page_title" in template_context.render_args


def test_template_context_md_pages(
    template_context_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the md_pages property of the TemplateHandler class."""
    markdown_loader, json_loader, front_matter_processor = template_context_dependencies
    template_context = TemplateContext(
        markdown_loader, json_loader, front_matter_processor
    )

    assert template_context.md_pages
    assert isinstance(template_context.md_pages, list)
    assert template_context.md_pages[0]
    assert isinstance(template_context.md_pages[0], dict)
    assert "html" in template_context.md_pages[0]
    assert "url_segment" in template_context.md_pages[0]
    assert "name" in template_context.md_pages[0]


def test_template_context_update_render_arg(
    template_context_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the update_render_arg method of the TemplateHandler class."""
    markdown_loader, json_loader, front_matter_processor = template_context_dependencies
    template_context = TemplateContext(
        markdown_loader, json_loader, front_matter_processor
    )

    key = "test_key"
    value = "test_value"

    assert key not in template_context.render_args

    template_context.update_render_arg(key, value)

    assert key in template_context.render_args
    assert template_context.render_args[key] == value
