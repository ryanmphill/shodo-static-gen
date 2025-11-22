"""
Template context management for static site generation.
"""

import os
from shodo_ssg.data_loader import JSONLoader, MarkdownLoader
from shodo_ssg.front_matter_processor import FrontMatterProcessor


class TemplateContext:
    """Holds context data for template rendering"""

    def __init__(
        self,
        markdown_loader: MarkdownLoader,
        json_loader: JSONLoader,
        front_matter_processor: FrontMatterProcessor,
    ):
        self._render_args = None
        self._md_pages = None
        self.markdown_loader = markdown_loader
        self.json_loader = json_loader
        self.front_matter_processor = front_matter_processor

    @property
    def render_args(self):
        """
        Getter for the render arguments
        """
        if self._render_args is None:
            # Set the render arguments upon class instantiation
            self._render_args = self.markdown_loader.load_args()
            self._render_args.update(self.json_loader.load_args())

        return self._render_args.copy()

    @property
    def md_pages(self):
        """
        Getter for the markdown pages
        """
        if self._md_pages is None:
            # Set the markdown pages upon class instantiation
            self._md_pages = self.markdown_loader.load_pages()

            for md_page in self._md_pages:
                front_matter = self._get_front_matter_from_md(
                    os.path.abspath(md_page["path"])
                )
                if not front_matter:
                    front_matter = {}
                # Add the front matter to the md_page
                md_page["front_matter"] = front_matter

        return self._md_pages.copy()

    def update_render_arg(self, key, value):
        """
        Update a render argument with the provided key-value pair. Used for
        setting and updating render arguments that are reused for dynamic content,
        such as article pages.
        """
        if self._render_args is None:
            self._render_args = self.render_args
        self._render_args[key] = value

    def _get_front_matter_from_md(self, file_path: str):
        """
        Retrieves the front matter from a markdown file. The front matter is
        the metadata that is used to populate the render arguments. It is a JSON object that
        is enclosed by `@frontmatter` at the beginning of the object and `@endfrontmatter` at
        the end of the front matter.
        """
        content = ""
        if file_path.endswith(".md"):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                content = content.lstrip()

        front_matter = self.front_matter_processor.get_front_matter(content)
        return front_matter
