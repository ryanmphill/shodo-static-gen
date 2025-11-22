"""Tests for the front_matter_processor module."""

from shodo_ssg.front_matter_processor import FrontMatterProcessor


def test_front_matter_processor_init(
    front_matter_processor_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the __init__ method of the TemplateHandler class."""
    json_loader = front_matter_processor_dependencies
    front_matter_processor = FrontMatterProcessor(json_loader)

    assert front_matter_processor.json_loader


def test_front_matter_processor_get_front_matter_returns_front_matter_from_file(
    front_matter_processor_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the get_front_matter method of the TemplateHandler class."""
    json_loader = front_matter_processor_dependencies
    front_matter_processor = FrontMatterProcessor(json_loader)

    content = "@frontmatter\n"
    content += '{"title": "Test Article",\n"description": "This is a test article."}\n'
    content += "@endfrontmatter\n"
    content += "This is the content of the test article.\n"

    front_matter = front_matter_processor.get_front_matter(content)

    assert front_matter
    assert isinstance(front_matter, dict)
    assert "title" in front_matter
    assert "description" in front_matter
    assert front_matter["title"] == "Test Article"
    assert front_matter["description"] == "This is a test article."
    for key in front_matter:
        assert front_matter[key] != "This is the content of the test article."


def test_front_matter_processor_clear_front_matter_returns_content_without_front_matter(
    front_matter_processor_dependencies,
):  # pylint: disable=redefined-outer-name
    """Test the clear_front_matter method of the TemplateHandler class."""
    json_loader = front_matter_processor_dependencies
    front_matter_processor = FrontMatterProcessor(json_loader)

    content = """
    @frontmatter
    {"title": "Test Article", "description": "This is a test article."}
    @endfrontmatter
    This is the content of the test article.
    <p>@frontmatter
    {"title": "Another Article", "description": "This is another test article."}
    @endfrontmatter</p>
    This is the content of another test article.
    """

    expected_content = """
    This is the content of the test article.
    This is the content of another test article.
    """

    result = front_matter_processor.clear_front_matter(file_path=None, content=content)

    # Remove all whitespace
    result = "".join(result.split())
    expected_content = "".join(expected_content.split())

    assert result == expected_content
