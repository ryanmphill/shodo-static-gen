"""
This module is responsible for handling the template environment as well as
rendering the Jinja2 templates as html
"""

import logging
import os
import re
from typing import Optional
from jinja2 import (
    Environment,
    FileSystemLoader,
)

from shodo_ssg.data_loader import JSONLoader, MarkdownLoader, SettingsDict


class TemplateHandler:
    """
    Handles the loading and rendering of templates using Jinja2.
    """

    def __init__(
        self,
        settings: SettingsDict,
        markdown_loader: MarkdownLoader,
        json_loader: JSONLoader,
    ):
        """
        Initialize the TemplateHandler with the paths to the template directories.
        """
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=settings["template_paths"])
        )
        self.build_dir = settings["build_dir"]
        self.root_path = settings["root_path"]
        self.markdown_loader = markdown_loader
        self.json_loader = json_loader
        self._render_args = None
        self._md_pages = None

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
                front_matter = self.get_front_matter(os.path.abspath(md_page["path"]))
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

    def get_template(self, template_name):
        """
        Retrieves a template by name
        """
        return self.template_env.get_template(template_name)

    def _log_info(self, page_name, destination):
        """
        Prints a status update of the writing operation
        """
        logging.info(
            "\033[94mWriting html from %s to %s...\033[0m", page_name, destination
        )

    def _get_doc_head(
        self,
        styles_link="/static/styles/main.css",
        favicon_link='<link rel="icon" type="image/x-icon" href="/favicon.ico">',
        front_matter: Optional[dict] = None,
    ):
        """
        Generate the HTML head section for a document, including opening body tag.
        """
        global_metadata: dict = self.render_args.get("metadata", {})
        if front_matter is None:
            front_matter = {}

        # Merge global metadata with front matter, with front_matter taking precedence
        head_content = self._merge_head_data(front_matter, global_metadata)

        # Extract the "lang", "body_id", and "body_class" properties and
        # remove them from the dictionary
        lang = head_content.pop("lang", "en")
        body_id = head_content.pop("body_id", None)
        body_class = head_content.pop("body_class", None)

        # Format the properties of the head content as HTML tags
        head_content_tags = self._format_head_data_as_html(head_content)

        # Remove empty tags "" from the dictionary
        head_content_tags = {k: v for k, v in head_content_tags.items() if v != ""}
        # Join the tags into a single string
        head_content_html = "\n".join(head_content_tags.values())

        head_html = f"""
        <!DOCTYPE html>
        <html lang="{lang}">
        <head>
            {head_content_html}
            {favicon_link}
            <link href="{styles_link}" rel="stylesheet" />
        </head>
        <body
        """
        if body_id:
            head_html += f' id="{body_id}"'
        if body_class:
            head_html += f' class="{body_class}"'
        head_html += ">"
        head_html = head_html.strip() + "\n"

        return head_html

    def _format_head_data_as_html(self, head_content: dict) -> dict:
        """
        Format the properties of the head content as HTML tags.
        """
        # Format the properties of the head content as HTML tags
        formatted_head_content = {
            "charset": f'<meta charset="{head_content["charset"]}">',
            "viewport": '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            "title": f'<title>{head_content["title"]}</title>',
            "description": (
                f'<meta name="description" content="{head_content["description"]}">'
                if head_content["description"]
                else ""
            ),
            "keywords": (
                f'<meta name="keywords" content="{",".join(head_content["keywords"])}">'
                if isinstance(head_content["keywords"], list)
                else (
                    f'<meta name="keywords" content="{head_content["keywords"]}">'
                    if head_content["keywords"]
                    else ""
                )
            ),
            "author": (
                f'<meta name="author" content="{head_content["author"]}">'
                if head_content["author"]
                else ""
            ),
            "theme_color": (
                f'<meta name="theme-color" content="{head_content["theme_color"]}">'
                if head_content["theme_color"]
                else ""
            ),
            "og_image": (
                f'<meta property="og:image" content="{head_content["og_image"]}">'
                if head_content["og_image"]
                else ""
            ),
            "og_image_alt": (
                f'<meta property="og:image:alt" content="{head_content["og_image_alt"]}">'
                if head_content["og_image_alt"]
                else ""
            ),
            "og_title": (
                f'<meta property="og:title" content="{head_content["og_title"]}">'
                if head_content["og_title"]
                else ""
            ),
            "og_description": (
                f'<meta property="og:description" content="{head_content["og_description"]}">'
                if head_content["og_description"]
                else ""
            ),
            "og_url": (
                f'<meta property="og:url" content="{head_content["og_url"]}">'
                if head_content["og_url"]
                else ""
            ),
            "og_type": (
                f'<meta property="og:type" content="{head_content["og_type"]}">'
                if head_content["og_type"]
                else ""
            ),
            "og_site_name": (
                f'<meta property="og:site_name" content="{head_content["og_site_name"]}">'
                if head_content["og_site_name"]
                else ""
            ),
            "og_locale": (
                f'<meta property="og:locale" content="{head_content["og_locale"]}">'
                if head_content["og_locale"]
                else ""
            ),
            "canonical": (
                f'<link rel="canonical" href="{head_content["canonical"]}">'
                if head_content["canonical"]
                else ""
            ),
            "google_font_link": (
                f"""
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="{head_content["google_font_link"]}" rel="stylesheet">
                """
                if head_content["google_font_link"]
                else ""
            ),
            "preconnects": (
                "\n".join(
                    [
                        f'<link rel="preconnect" href="{link}">'
                        for link in head_content["preconnects"]
                    ]
                )
                if isinstance(head_content["preconnects"], list)
                else (
                    f'<link rel="preconnect" href="{head_content["preconnects"]}">'
                    if head_content["preconnects"]
                    else ""
                )
            ),
            "stylesheets": (
                "\n".join(
                    [
                        f'<link rel="stylesheet" href="{sheet}">'
                        for sheet in head_content["stylesheets"]
                    ]
                )
                if isinstance(head_content["stylesheets"], list)
                else (
                    f'<link rel="stylesheet" href="{head_content["stylesheets"]}">'
                    if head_content["stylesheets"]
                    else ""
                )
            ),
            "robots": (
                f'<meta name="robots" content="{head_content["robots"]}">'
                if head_content["robots"]
                else ""
            ),
            "head_extra": (
                "\n".join(head_content["head_extra"])
                if isinstance(head_content["head_extra"], list)
                else (
                    f'{head_content["head_extra"]}'
                    if head_content["head_extra"]
                    else ""
                )
            ),
        }
        return formatted_head_content

    def _merge_head_data(self, front_matter: dict, global_metadata: dict):
        """
        Format the head data for the HTML document. This includes merging
        global metadata with front matter and generating the HTML head section.
        """
        # Merge global metadata with front matter, with front_matter taking precedence
        metadata = {
            "title": front_matter.get(
                "title", global_metadata.get("title", "Shodo SSG")
            ),
            "lang": front_matter.get("lang", global_metadata.get("lang", "en")),
            "charset": front_matter.get(
                "charset", global_metadata.get("charset", "UTF-8")
            ),
            "description": front_matter.get(
                "description", global_metadata.get("description", "")
            ),
            "keywords": front_matter.get(
                "keywords", global_metadata.get("keywords", "")
            ),
            "author": front_matter.get("author", global_metadata.get("author", "")),
            "theme_color": front_matter.get(
                "theme_color", global_metadata.get("theme_color", "")
            ),
            "og_image": front_matter.get(
                "og_image", global_metadata.get("og_image", "")
            ),
            "og_image_alt": front_matter.get(
                "og_image_alt", global_metadata.get("og_image_alt", "")
            ),
            "og_title": front_matter.get(
                "og_title", global_metadata.get("og_title", "")
            ),
            "og_description": front_matter.get(
                "og_description", global_metadata.get("og_description", "")
            ),
            "og_url": front_matter.get("og_url", global_metadata.get("og_url", "")),
            "og_type": front_matter.get("og_type", global_metadata.get("og_type", "")),
            "og_site_name": front_matter.get(
                "og_site_name", global_metadata.get("og_site_name", "")
            ),
            "og_locale": front_matter.get(
                "og_locale", global_metadata.get("og_locale", "")
            ),
            "canonical": front_matter.get(
                "canonical", global_metadata.get("canonical", "")
            ),
            "google_font_link": front_matter.get(
                "google_font_link", global_metadata.get("google_font_link", "")
            ),
            "preconnects": front_matter.get(
                "preconnects", global_metadata.get("preconnects", [])
            ),
            "stylesheets": front_matter.get(
                "stylesheets", global_metadata.get("stylesheets", [])
            ),
            "robots": front_matter.get("robots", global_metadata.get("robots", "")),
            "head_extra": front_matter.get(
                "head_extra", global_metadata.get("head_extra", "")
            ),
            "body_id": front_matter.get("body_id", global_metadata.get("body_id", "")),
            "body_class": front_matter.get(
                "body_class", global_metadata.get("body_class", "")
            ),
        }
        return metadata

    def _get_doc_tail(self, script_link="/static/scripts/main.js"):
        """
        Generate the HTML end section for a document, including script tag
        for main.js and a closing body tag.
        """
        return f"""
                <script type="module" src="{script_link}"></script>
            </body>
        </html>
        """.strip()

    def _write_html_from_template(
        self, template_name, destination_dir, front_matter: Optional[dict] = None
    ):
        """
        Render a template with the provided arguments and write the output to a file.
        """
        self._log_info(template_name, destination_dir)
        template = self.get_template(template_name)
        template_path = os.path.abspath(template.filename)
        if front_matter is None:
            front_matter = self.get_front_matter(template_path)
        with open(destination_dir, "w", encoding="utf-8") as output_file:
            output_file.write(
                self._get_doc_head(front_matter=front_matter)
                + template.render(self.render_args)
                + "\n"
                + self._get_doc_tail()
            )

        self.clear_front_matter(destination_dir)

    def write_home_template(self):
        """
        Write the index.html file using the provided render arguments.
        """
        return self._write_html_from_template(
            "home.jinja", f"{self.build_dir}/index.html"
        )

    def write_linked_template_pages(self, nested_dirs=""):
        """
        Write HTML pages linked from the index page using the provided render arguments.
        """
        src_path = os.path.join(self.root_path, "src/theme/views/pages/")
        pages_src_dir = "/" + os.path.join(src_path, nested_dirs).strip("/") + "/"
        if os.path.exists(pages_src_dir) and os.listdir(pages_src_dir):
            for path in os.listdir(pages_src_dir):
                if (
                    path.endswith(".jinja")
                    or path.endswith(".j2")
                    or path.endswith(".jinja2")
                ):
                    template_name = os.path.join(nested_dirs, path)
                    page_name = nested_dirs + os.path.splitext(path)[0]
                    if not os.path.exists(f"{self.build_dir}/{page_name}"):
                        os.makedirs(f"{self.build_dir}/{page_name}")
                    self._write_html_from_template(
                        template_name, f"{self.build_dir}/{page_name}/index.html"
                    )
                path_from_root = os.path.join(self.root_path, pages_src_dir + path)
                # If directory, recursively create a nested route
                if os.path.isdir(path_from_root):
                    nested_path = nested_dirs + path + "/"
                    self.write_linked_template_pages(nested_path)

    def write_article_pages(self):
        """
        Writes html pages for each markdown file in the `articles` directory
        """
        for md_page in self.md_pages:
            # Get the layout for this template
            layout_template = self.get_md_layout_template(md_page["url_segment"])
            # Get the path
            build_path = os.path.join(
                self.build_dir,
                md_page["url_segment"].strip("/"),
                md_page["name"].strip("/"),
            )

            self.update_render_arg("article", md_page["html"])

            front_matter = md_page["front_matter"]

            if front_matter:
                # Don't write the template if 'draft' is set in front matter
                is_draft = front_matter.get("draft", False)
                if isinstance(is_draft, str) and (
                    is_draft.lower() == "true" or is_draft == "1"
                ):
                    continue

            if not os.path.exists(build_path):
                os.makedirs(build_path)

            self._write_html_from_template(layout_template, f"{build_path}/index.html")

    def get_md_layout_template(self, url_segment: str):
        """
        Retrieves the layout template that maps to the specified
        article path. If no layout is defined in the template directory
        with the same name, the layout template closest in the tree will
        be used.
        """
        if not url_segment:
            return "articles/layout.jinja"
        template_path = os.path.join("articles", url_segment.strip("/"), "layout.jinja")
        src_view_path = "/" + os.path.join(self.root_path, "src/theme/views/").strip(
            "/"
        )
        if os.path.exists(f"{src_view_path}/{template_path}"):
            return template_path
        segments = url_segment.strip("/").split("/")
        segments.pop()
        return self.get_md_layout_template("/".join(segments))

    def get_front_matter(self, file_path):
        """
        Retrieves the front matter from either a markdown or jinja file. The front matter is
        the metadata that is used to populate the render arguments. It is a JSON object that
        is enclosed by `@frontmatter` at the beginning of the object and `@endfrontmatter` at
        the end of the front matter.
        """
        content = ""
        if (
            file_path.endswith(".jinja")
            or file_path.endswith(".j2")
            or file_path.endswith(".jinja2")
        ):
            # If the file is a jinja template, we need to render it so
            # that front matter from included templates is also included
            # in the front matter
            template_name = os.path.basename(file_path)
            template = self.get_template(template_name)
            content = template.render(self.render_args)
        else:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                content = content.lstrip()

        pattern = r"@frontmatter\s*(.*?)\s*@endfrontmatter"
        pattern = re.compile(pattern, re.DOTALL)
        front_matters = pattern.findall(content)
        if front_matters:
            # If the front matter is a list, merge them into a single dict,
            # with the last one taking precedence
            if isinstance(front_matters, list) and len(front_matters) >= 1:
                combined_front_matter = {}
                for fm in front_matters:
                    fm = fm.replace("@frontmatter", "").replace("@endfrontmatter", "")
                    fm = fm.strip()
                    # If parsable json, return as dict
                    if fm.startswith("{") and fm.endswith("}"):
                        fm = self.json_loader.json_to_dict(fm)
                        if isinstance(fm, dict):
                            combined_front_matter.update(fm)

                # If the front matter is a dictionary, return it
                if isinstance(combined_front_matter, dict):
                    return combined_front_matter

        return None

    def clear_front_matter(
        self, file_path: Optional[str] = None, content: Optional[str] = None
    ):
        """
        Strips the front matter from the rendered html file. The front matter is a JSON object
        that is enclosed by the tags `@frontmatter` and `@endfrontmatter`. In the html files
        that were generated from markdown files, the front matter tags are also enclosed in
        '<p>' tags. This function removes the front matter and the enclosing '<p>' tags if they
        exist. If a file path is provided, the function will write the content back to the file
        after removing the front matter. If no content is provided instead of a file path, the
        function will return the content with the front matter removed.
        """
        front_matters = None

        if content is None and file_path is not None:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

        if "<p>@frontmatter" in content:
            pattern = r"(<p>@frontmatter\s*.*?\s*@endfrontmatter</p>)"
            pattern = re.compile(pattern, re.DOTALL)
            front_matters = pattern.findall(content)
            if front_matters:
                for fm in front_matters:
                    fm = fm.strip()
                    content = content.replace(fm, "")

        if "@frontmatter" in content:
            pattern = r"(@frontmatter\s*.*?\s*@endfrontmatter)"
            pattern = re.compile(pattern, re.DOTALL)
            front_matters = pattern.findall(content)
            if front_matters:
                for fm in front_matters:
                    fm = fm.strip()
                    content = content.replace(fm, "")
        if front_matters and file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

        return content

    def _format_md_page_data(self, md_page: dict) -> dict:
        """
        Format the markdown page data for rendering. This includes extracting
        the front matter and content from the markdown page. Used for rendering
        a list of articles/posts in a template with the shodo_get_articles function.
        """
        post = {}
        post["file_name"] = md_page["name"]
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

    def write(self):
        """
        Writes the root index.html and any linked html pages using the provided render arguments.
        """
        self.write_article_pages()
        self.write_home_template()
        self.write_linked_template_pages()
