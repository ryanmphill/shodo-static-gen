"""
Tests for the API class
"""

from unittest.mock import Mock
import pytest
from shodo_ssg.api import API
from shodo_ssg.template_context import TemplateContext
from shodo_ssg.front_matter_processor import FrontMatterProcessor


# pylint: disable=too-many-public-methods
class TestAPI:
    """Test suite for API class"""

    @pytest.fixture
    def front_matter_processor(self, front_matter_processor_dependencies):
        """Fixture to provide a FrontMatterProcessor instance"""
        json_loader = front_matter_processor_dependencies
        return FrontMatterProcessor(json_loader)

    @pytest.fixture
    def template_context(self):
        """Fixture to provide a TemplateContext instance with sample data"""
        context = Mock()

        # Add sample markdown pages
        context.md_pages = [
            {
                "name": "first-post",
                "url_segment": "/blog/",
                "html": "<p>First post content</p>",
                "front_matter": {
                    "title": "First Post",
                    "description": "First post description",
                    "summary": "First post summary",
                    "keywords": ["python", "ssg"],
                    "author": "John Doe",
                    "category": "technology",
                    "tags": ["python", "web"],
                    "date": "2025-01-15",
                    "draft": False,
                    "image": "/images/first.jpg",
                    "image_alt": "First post image",
                },
            },
            {
                "name": "second-post",
                "url_segment": "/blog/tutorials/",
                "html": "<p>Second post content</p>",
                "front_matter": {
                    "title": "Second Post",
                    "description": "Second post description",
                    "summary": "Second post summary",
                    "keywords": ["tutorial"],
                    "author": "Jane Smith",
                    "category": "tutorials",
                    "tags": ["tutorial", "web"],
                    "date": "2025-02-20",
                    "draft": False,
                },
            },
            {
                "name": "draft-post",
                "url_segment": "/blog/",
                "html": "<p>Draft content</p>",
                "front_matter": {
                    "title": "Draft Post",
                    "draft": True,
                    "date": "2025-03-01",
                },
            },
            {
                "name": "newsletter-post",
                "url_segment": "/newsletter/",
                "html": "<p>Newsletter content</p>",
                "front_matter": {
                    "title": "Newsletter Issue 1",
                    "category": "newsletter",
                    "tags": ["news"],
                    "date": "2025-01-01",
                    "draft": False,
                },
            },
        ]

        # Add sample store data
        context.render_args = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"},
                {"id": 3, "name": "Charlie", "role": "user"},
            ],
            "products": [
                {"id": 101, "name": "Widget", "price": 9.99},
                {"id": 102, "name": "Gadget", "price": 19.99},
            ],
        }

        return context

    @pytest.fixture
    def api(self, template_context: TemplateContext, front_matter_processor):
        """Fixture to provide an API instance"""
        return API(template_context, front_matter_processor)

    # Tests for _format_md_page_data
    def test_format_md_page_data_complete(
        self, api: API, template_context: TemplateContext
    ):
        """Test _format_md_page_data with complete front matter"""
        md_page = template_context.md_pages[0]
        # pylint: disable=protected-access
        result = api._format_md_page_data(md_page)

        assert result["file_name"] == "first-post"
        assert result["directory"] == "/blog/"
        assert result["path"] == "/blog/first-post"
        assert result["title"] == "First Post"
        assert result["description"] == "First post description"
        assert result["summary"] == "First post summary"
        assert result["keywords"] == ["python", "ssg"]
        assert result["author"] == "John Doe"
        assert result["category"] == "technology"
        assert result["tags"] == ["python", "web"]
        assert result["date"] == "2025-01-15"
        assert result["draft"] is False
        assert result["image"] == "/images/first.jpg"
        assert result["image_alt"] == "First post image"
        assert result["content"] == "<p>First post content</p>"

    def test_format_md_page_data_minimal(self, api: API):
        """Test _format_md_page_data with minimal front matter"""
        md_page = {
            "name": "minimal-post",
            "url_segment": "/posts/",
            "html": "<p>Minimal content</p>",
            "front_matter": {},
        }
        # pylint: disable=protected-access
        result = api._format_md_page_data(md_page)

        assert result["file_name"] == "minimal-post"
        assert result["directory"] == "/posts/"
        assert result["path"] == "/posts/minimal-post"
        assert result["title"] == ""
        assert result["description"] == ""
        assert result["summary"] == ""
        assert result["keywords"] == []
        assert result["author"] == ""
        assert result["category"] == ""
        assert result["tags"] == []
        assert result["date"] == ""
        assert result["draft"] is False
        assert result["image"] == ""
        assert result["image_alt"] == ""
        assert result["content"] == "<p>Minimal content</p>"

    def test_format_md_page_data_no_front_matter(self, api: API):
        """Test _format_md_page_data when front_matter is None"""
        md_page = {
            "name": "no-front-matter",
            "url_segment": "/posts/",
            "html": "<p>Content</p>",
            "front_matter": None,
        }
        # pylint: disable=protected-access
        result = api._format_md_page_data(md_page)

        assert result["title"] == ""
        assert result["draft"] is False

    # Tests for shodo_get_articles
    def test_shodo_get_articles_no_filters(self, api: API):
        """Test shodo_get_articles returns all non-draft articles"""
        result = api.shodo_get_articles()

        assert len(result) == 3  # Should exclude the draft
        assert all(not post["draft"] for post in result)
        assert any(post["title"] == "First Post" for post in result)
        assert any(post["title"] == "Second Post" for post in result)
        assert any(post["title"] == "Newsletter Issue 1" for post in result)
        assert not any(post["title"] == "Draft Post" for post in result)

    def test_shodo_get_articles_filter_by_directory_starts_with(self, api: API):
        """Test filtering articles by directory_starts_with"""
        filters = {"directory_starts_with": "/blog"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 2
        assert all(post["directory"].startswith("/blog") for post in result)
        assert any(post["title"] == "First Post" for post in result)
        assert any(post["title"] == "Second Post" for post in result)

    def test_shodo_get_articles_filter_by_directory_equals(self, api: API):
        """Test filtering articles by directory_equals"""
        filters = {"directory_equals": "/blog/"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 1
        assert result[0]["title"] == "First Post"
        assert result[0]["directory"] == "/blog/"

    def test_shodo_get_articles_filter_by_category_string(self, api: API):
        """Test filtering articles by category as string"""
        filters = {"category": "technology"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 1
        assert result[0]["title"] == "First Post"
        assert result[0]["category"] == "technology"

    def test_shodo_get_articles_filter_by_category_list(self, api: API):
        """Test filtering articles by category as list"""
        filters = {"category": ["technology", "tutorials"]}
        result = api.shodo_get_articles(filters)

        assert len(result) == 2
        categories = [post["category"] for post in result]
        assert "technology" in categories
        assert "tutorials" in categories

    def test_shodo_get_articles_filter_by_tags(self, api: API):
        """Test filtering articles by tags"""
        filters = {"tags": ["web"]}
        result = api.shodo_get_articles(filters)

        assert len(result) == 2
        assert all(any(tag in post["tags"] for tag in ["web"]) for post in result)

    def test_shodo_get_articles_filter_by_date(self, api: API):
        """Test filtering articles by date"""
        filters = {"date": "2025-02-01"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 1
        assert result[0]["title"] == "Second Post"
        assert result[0]["date"] >= "2025-02-01"

    def test_shodo_get_articles_order_by_date(self, api: API):
        """Test ordering articles by date (descending)"""
        filters = {"order_by": "date"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 3
        assert result[0]["date"] == "2025-02-20"  # Most recent first
        assert result[1]["date"] == "2025-01-15"
        assert result[2]["date"] == "2025-01-01"

    def test_shodo_get_articles_order_by_title(self, api: API):
        """Test ordering articles by title (ascending)"""
        filters = {"order_by": "title"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 3
        titles = [post["title"] for post in result]
        assert titles == sorted(titles)

    def test_shodo_get_articles_with_limit(self, api: API):
        """Test limiting number of returned articles"""
        filters = {"limit": 2, "order_by": "date"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 2
        assert result[0]["date"] == "2025-02-20"
        assert result[1]["date"] == "2025-01-15"

    def test_shodo_get_articles_with_offset(self, api: API):
        """Test offsetting returned articles"""
        filters = {"offset": 1, "order_by": "date"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 2
        assert result[0]["date"] == "2025-01-15"
        assert result[1]["date"] == "2025-01-01"

    def test_shodo_get_articles_with_offset_and_limit(self, api: API):
        """Test combining offset and limit"""
        filters = {"offset": 1, "limit": 1, "order_by": "date"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 1
        assert result[0]["date"] == "2025-01-15"

    def test_shodo_get_articles_multiple_filters(self, api: API):
        """Test combining multiple filters"""
        filters = {
            "directory_starts_with": "/blog",
            "tags": ["web"],
            "order_by": "date",
            "limit": 1,
        }
        result = api.shodo_get_articles(filters)

        assert len(result) == 1
        assert result[0]["title"] == "Second Post"

    def test_shodo_get_articles_no_matches(self, api: API):
        """Test when filters match no articles"""
        filters = {"category": "nonexistent"}
        result = api.shodo_get_articles(filters)

        assert len(result) == 0

    # TODO: Add tests for shodo_query_store

    # Tests for shodo_get_excerpt
    def test_shodo_get_excerpt_single_paragraph(self, api: API):
        """Test getting excerpt from single paragraph"""
        content = "<p>This is a test paragraph with some content.</p>"
        result = api.shodo_get_excerpt(content, length=20)

        assert result == "This is a test..."

    def test_shodo_get_excerpt_multiple_paragraphs(self, api: API):
        """Test getting excerpt from multiple paragraphs"""
        content = """
        <p>First paragraph with some text.</p>
        <p>Second paragraph with more text.</p>
        <p>Third paragraph.</p>
        """
        result = api.shodo_get_excerpt(content, length=50)

        assert "First paragraph" in result
        assert "Second paragraph" in result
        assert result.endswith("...")

    def test_shodo_get_excerpt_with_html_tags(self, api: API):
        """Test that HTML tags are removed from excerpt"""
        content = "<p>This has <strong>bold</strong> and <em>italic</em> text.</p>"
        result = api.shodo_get_excerpt(content, length=50)

        assert "<strong>" not in result
        assert "<em>" not in result
        assert "bold" in result
        assert "italic" in result

    def test_shodo_get_excerpt_no_paragraph_tags(self, api: API):
        """Test excerpt from content without paragraph tags"""
        content = "<div>This is content in a div tag.</div>"
        result = api.shodo_get_excerpt(content, length=16)

        assert result == "This is content..."

    def test_shodo_get_excerpt_exact_length(self, api: API):
        """Test excerpt when content is exactly at length limit"""
        content = "<p>Exactly twenty chars</p>"
        result = api.shodo_get_excerpt(content, length=23)

        assert result == "Exactly twenty chars"
        assert not result.endswith("...")

    def test_shodo_get_excerpt_shorter_than_limit(self, api: API):
        """Test excerpt when content is shorter than limit"""
        content = "<p>Short text</p>"
        result = api.shodo_get_excerpt(content, length=100)

        assert result == "Short text"
        assert not result.endswith("...")

    def test_shodo_get_excerpt_default_length(self, api: API):
        """Test excerpt with default length parameter"""
        content = "<p>" + "x" * 150 + "</p>"
        result = api.shodo_get_excerpt(content)

        assert len(result) <= 103  # 100 + "..."
        assert result.endswith("...")

    def test_shodo_get_excerpt_truncate_at_word_boundary(self, api: API):
        """Test that excerpt truncates at word boundaries"""
        content = "<p>This is a longer sentence that should be truncated properly.</p>"
        result = api.shodo_get_excerpt(content, length=25)

        assert result.endswith("...")
        assert not result.endswith(" ...")  # Should not have trailing space

    def test_shodo_get_excerpt_with_front_matter(self, api: API):
        """Test that front matter is removed from excerpt"""
        content = """
        @frontmatter
        {
            "head_extra": "<p>This should not be included in the excerpt!</p>"
        }
        @endfrontmatter
        <p>This is the actual content.</p>
        """
        result = api.shodo_get_excerpt(content, length=50)

        assert "title:" not in result
        assert "Test Post" not in result
        assert "This is the actual content." in result

    def test_shodo_get_excerpt_empty_content(self, api: API):
        """Test excerpt from empty content"""
        content = ""
        result = api.shodo_get_excerpt(content, length=100)

        assert result == ""

    def test_shodo_get_excerpt_whitespace_only(self, api: API):
        """Test excerpt from whitespace-only content"""
        content = "   \n\n   "
        result = api.shodo_get_excerpt(content, length=100)

        assert result == ""

    def test_shodo_get_excerpt_nested_html(self, api: API):
        """Test excerpt with nested HTML structures"""
        content = """
        <div>
            <p>First paragraph in div.</p>
            <section>
                <p>Second paragraph in section.</p>
            </section>
        </div>
        """
        result = api.shodo_get_excerpt(content, length=50)

        assert "<div>" not in result
        assert "<section>" not in result
        assert "First paragraph" in result
        assert "Second paragraph" in result
