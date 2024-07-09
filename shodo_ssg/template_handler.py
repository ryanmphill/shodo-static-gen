""" 
This module is responsible for handling the template environment as well as 
rendering the Jinja2 templates as html
"""

import logging
import os
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

        return self._md_pages.copy()

    def update_render_arg(self, key, value):
        """
        Update a render argument with the provided key-value pair. Used for
        setting and updating render arguments that are reused for dynamic content,
        such as article pages.
        """
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
    ):
        """
        Generate the HTML head section for a document, including opening body tag.
        """
        return (
            f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{ self.render_args["metadata"]["title"] }</title>
            {favicon_link}
            <link href="{styles_link}" rel="stylesheet" />
        </head>
        <body>
        """.strip()
            + "\n"
        )

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

    def _write_html_from_template(self, template_name, destination_dir):
        """
        Render a template with the provided arguments and write the output to a file.
        """
        self._log_info(template_name, destination_dir)
        template = self.get_template(template_name)
        with open(destination_dir, "w", encoding="utf-8") as output_file:
            output_file.write(
                self._get_doc_head()
                + template.render(self.render_args)
                + "\n"
                + self._get_doc_tail()
            )

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
        pages_src_dir = "src/theme/views/pages/" + nested_dirs
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
                self.build_dir.strip("/"),
                md_page["url_segment"].strip("/"),
                md_page["name"].strip("/"),
            )
            if not os.path.exists(build_path):
                os.makedirs(build_path)
            self.update_render_arg("article", md_page["html"])
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
        if os.path.exists(f"src/theme/views/{template_path}"):
            return template_path
        segments = url_segment.strip("/").split("/")
        segments.pop()
        return self.get_md_layout_template("/".join(segments))

    def write(self):
        """
        Writes the root index.html and any linked html pages using the provided render arguments.
        """
        self.write_home_template()
        self.write_linked_template_pages()
        self.write_article_pages()
