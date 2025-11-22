"""API functions to expose to templates."""

import re
from typing import Optional
from shodo_ssg.front_matter_processor import FrontMatterProcessor
from shodo_ssg.template_context import TemplateContext


class API:
    """Exposes API functions to templates"""

    def __init__(
        self, context: TemplateContext, front_matter_processor: FrontMatterProcessor
    ):
        self.context = context
        self.front_matter_processor = front_matter_processor

    def _format_md_page_data(self, md_page: dict) -> dict:
        """
        Format the markdown page data for rendering. This includes extracting
        the front matter and content from the markdown page. Used for rendering
        a list of articles/posts in a template with the shodo_get_articles function.
        """
        post = {}
        post["file_name"] = md_page["name"]
        post["directory"] = md_page["url_segment"]
        post["path"] = md_page["url_segment"] + md_page["name"]

        front_matter = md_page["front_matter"]

        if not isinstance(front_matter, dict):
            front_matter = {}

        post["title"] = front_matter.get("title", "")
        post["description"] = front_matter.get("description", "")
        post["summary"] = front_matter.get("summary", "")
        post["keywords"] = front_matter.get("keywords", [])
        post["author"] = front_matter.get("author", "")
        post["category"] = front_matter.get("category", "")
        post["tags"] = front_matter.get("tags", [])
        post["date"] = front_matter.get("date", "")
        post["draft"] = front_matter.get("draft", False)
        post["image"] = front_matter.get("image", "")
        post["image_alt"] = front_matter.get("image_alt", "")
        post["content"] = md_page["html"]
        post["modified"] = front_matter.get("modified", "")

        return post

    def shodo_get_articles(self, filters: Optional[dict] = None):
        """
        Returns a list of articles that are not marked as drafts to expose to the
        template. The articles are filtered based on the provided filters. The filters
        can include "category", "tags", "date", and "limit".
        """
        formatted_data = [
            self._format_md_page_data(md_page) for md_page in self.context.md_pages
        ]

        filtered_data = [post for post in formatted_data if not post["draft"]]
        if filters is None:
            filters = {}

        if "directory_starts_with" in filters:
            directory = filters["directory_starts_with"].strip("/")
            filtered_data = [
                post
                for post in filtered_data
                if post["directory"].strip("/").startswith(directory)
                and not post["draft"]
            ]

        if "directory_equals" in filters:
            directory = filters["directory_equals"].strip("/")
            filtered_data = [
                post
                for post in filtered_data
                if post["directory"].strip("/") == directory and not post["draft"]
            ]

        if "category" in filters:
            category = filters["category"]
            # If category is string, convert to list
            if isinstance(category, str):
                category = [category]
            filtered_data = [
                post
                for post in filtered_data
                if post["category"] in category and not post["draft"]
            ]
        if "tags" in filters:
            tags = filters["tags"]
            filtered_data = [
                post
                for post in filtered_data
                if set(post["tags"]).intersection(set(tags)) and not post["draft"]
            ]
        if "date" in filters:
            date = filters["date"]
            filtered_data = [
                post
                for post in filtered_data
                if post["date"] >= date and not post["draft"]
            ]

        # Apply limit, offset, and ordering if specified
        if "order_by" in filters:
            order_by = filters["order_by"]
            if order_by == "date":
                filtered_data = sorted(
                    filtered_data, key=lambda x: x["date"], reverse=True
                )
            elif order_by == "title":
                filtered_data = sorted(filtered_data, key=lambda x: x["title"])

        if "offset" in filters:
            offset = filters["offset"]
            filtered_data = filtered_data[offset:]

        if "limit" in filters:
            limit = filters["limit"]
            filtered_data = filtered_data[:limit]

        return filtered_data

    # TODO: Implement template function to query json data in the store directory
    def shodo_query_store(self, collection: str, filters: Optional[dict] = None):
        """
        Queries the json data loaded in render_args with the provided filters.
        The filters can include key-value pairs to match against the collection items.
        """

    def shodo_get_excerpt(self, content: str, length: int = 100):
        """
        Returns an excerpt from html content. Only content within the <p> tags
        is considered. The excerpt is truncated to the specified length.
        """
        # Extract the content within <p> tags
        content = self.front_matter_processor.clear_front_matter(
            file_path=None, content=content
        )
        pattern = r"<p>(.*?)</p>"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            # Join the matches and truncate to the specified length
            excerpt = " ".join(matches)
        else:
            # If no <p> tags are found, attempt to truncate a plain text string
            excerpt = re.sub(r"<.*?>", "", content)

        if excerpt:
            # Remove HTML tags
            excerpt = re.sub(r"<.*?>", "", excerpt)

        if len(excerpt) > length:
            # Find the last space before the length limit
            last_space = excerpt.rfind(" ", 0, length)
            if last_space != -1:
                excerpt = excerpt[:last_space] + "..."
            else:
                excerpt = excerpt[:length] + "..."

        return excerpt.strip()
