""" 
This module is responsible for handling the template environment as well as 
rendering the Jinja2 templates as html
"""

import os
from jinja2 import (
    Environment,
    FileSystemLoader,
)


class TemplateHandler:
    """
    Handles the loading and rendering of templates using Jinja2.
    """

    def __init__(self, template_paths: list[str], build_dir="dist"):
        """
        Initialize the TemplateHandler with the paths to the template directories.
        """
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=template_paths)
        )
        self.build_dir = build_dir

    def get_template(self, template_name):
        """
        Retrieves a template by name
        """
        return self.template_env.get_template(template_name)

    def _log_info(self, page_name, destination):
        """
        Prints a status update of the writing operation
        """
        print(
            "\033[94m"
            + f"Writing html from {page_name} to {destination}..."
            + "\033[0m"
        )

    def _get_doc_head(
        self,
        site_title,
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
            <title>{ site_title }</title>
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

    def _write_html_from_template(
        self, template_name, destination_dir, render_args: dict
    ):
        """
        Render a template with the provided arguments and write the output to a file.
        """
        self._log_info(template_name, destination_dir)
        template = self.get_template(template_name)
        with open(destination_dir, "w", encoding="utf-8") as output_file:
            output_file.write(
                self._get_doc_head(render_args["site_title"])
                + template.render(render_args)
                + "\n"
                + self._get_doc_tail()
            )

    def write_home_template(self, render_args: dict):
        """
        Write the index.html file using the provided render arguments.
        """
        return self._write_html_from_template(
            "home.jinja", f"{self.build_dir}/index.html", render_args
        )

    def write_linked_template_pages(self, render_args: dict, nested_dirs=""):
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
                        template_name,
                        f"{self.build_dir}/{page_name}/index.html",
                        render_args,
                    )
                path_from_root = os.path.join(
                    os.environ.get("ROOT_PATH"), pages_src_dir + path
                )
                # If directory, recursively create a nested route
                if os.path.isdir(path_from_root):
                    nested_path = nested_dirs + path + "/"
                    self.write_linked_template_pages(render_args, nested_path)

    def write_article_pages(self, md_pages: list[dict[str, str]], render_args: dict):
        """
        Writes html pages for each markdown file in the `articles` directory
        """
        for md_page in md_pages:
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
            render_args["article"] = md_page["html"]
            self._write_html_from_template(
                layout_template, f"{build_path}/index.html", render_args
            )

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

    def write(self, render_args: dict, md_pages: list[dict]):
        """
        Writes the root index.html and any linked html pages using the provided render arguments.
        """
        self.write_home_template(render_args)
        self.write_linked_template_pages(render_args)
        self.write_article_pages(md_pages, render_args)
