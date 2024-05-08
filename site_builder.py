"""This module builds a static site in the /dist directory from jinja2
templates and all static assets
"""

from dataclasses import dataclass
from json import load
from abc import ABC, abstractmethod
import os
import shutil
from io import TextIOWrapper
from markdown2 import markdown  # Will convert markdown file to html
from jinja2 import (
    Environment,
    FileSystemLoader,
)  # Take layout.jinja, inject markdown into it and create final output html


class TemplateHandler:
    """
    Handles the loading and rendering of templates using Jinja2.
    """

    def __init__(self, template_paths: list[str]):
        """
        Initialize the TemplateHandler with the paths to the template directories.
        """
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=template_paths)
        )

    def get_template(self, template_name):
        """
        Retrieves a template by name
        """
        return self.template_env.get_template(template_name)

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
        template = self.get_template(template_name)
        with open(
            destination_dir, "w", encoding="utf-8"
        ) as output_file:  # use 'w' to open for writing, not reading
            output_file.write(
                self._get_doc_head(render_args["site_title"])
                + template.render(render_args)
                + "\n"
                + self._get_doc_tail()
            )

    def write_index_html(self, render_args: dict):
        """
        Write the index.html file using the provided render arguments.
        """
        return self._write_html_from_template(
            "layout.jinja", "dist/index.html", render_args
        )

    def write_linked_html_pages(self, render_args: dict):
        """
        Write HTML pages linked from the index page using the provided render arguments.
        """
        pages_src_dir = "src/theme/views/pages/"
        if os.path.exists(pages_src_dir) and os.listdir(pages_src_dir):
            for file in os.listdir(pages_src_dir):
                if (
                    file.endswith(".jinja")
                    or file.endswith(".j2")
                    or file.endswith(".jinja2")
                ):
                    page_name = os.path.splitext(file)[0]
                    os.makedirs(f"dist/{page_name}")
                    self._write_html_from_template(
                        file, f"dist/{page_name}/index.html", render_args
                    )


class DataLoader(ABC):
    """
    Abstract base class for loading data from files.
    """

    def __init__(self, src_path):
        """
        Initializes the DataLoader with a specified path to the data, which
        could include Markdown files or JSON
        """
        self.src_path = src_path

    def list_files(self):
        """
        List all files in the path specified during class initialization
        """
        files = []
        for file in os.listdir(self.src_path):
            files.append(file)
        return files

    @abstractmethod
    def load_render_args(self):
        """
        Load data from the specified file path.
        This method must be implemented by subclasses.
        """


class MarkdownLoader(DataLoader):
    """
    Handles the loading of markdown files as well as their conversion to html
    strings. Extends DataLoader
    """

    def list_files(self):
        """
        Lists all markdown files in the path specified during class initialization
        """
        md_files = []
        for file in os.listdir(self.src_path):
            if file.endswith(".md"):
                md_files.append(file)
        return md_files

    def _convert_to_html(self, markdown_file: TextIOWrapper) -> str:
        """
        Takes an open markdown file and converts it to an html string
        """
        return markdown(
            markdown_file.read(), extras=["fenced-code-blocks", "code-friendly"]
        )

    def load_render_args(self):
        """
        Load html converted from markdown files as a dictionary of render arguments,
        where the key is the name of the markdown file, and the value is the converted
        html string to be inserted in the templates.
        """
        converted_html = {}
        for md_file in self.list_files():
            md_file_path = os.path.join(self.src_path, md_file)
            md_var_name = os.path.splitext(md_file)[0]
            with open(md_file_path, "r", encoding="utf-8") as markdown_file:
                converted_html[md_var_name] = self._convert_to_html(markdown_file)
        return converted_html


class JSONLoader(DataLoader):
    """
    Handles the loading of JSON key value pairs to be inserted into
    templates as dictionary render arguments
    """

    def load_render_args(self):
        """
        Load JSON from the specified file path as a Python dict, where the key is the
        variable name in the template files, and the value is the data to be inserted.
        """
        with open(self.src_path, "r", encoding="utf-8") as config_file:
            config = load(config_file)

        if isinstance(config, dict):
            return config

        return {}


class BaseFileWriter:
    """
    Base class for single file writing operations
    """

    def __init__(self, src_path: str, destination_path: str):
        self.src_path = src_path
        self.destination_path = destination_path

    def log_info(self):
        """
        Prints a status message that the file writing operation is taking place
        """
        print(
            "\033[94m"
            + f"Copying file {self.src_path} to {self.destination_path}..."
            + "\033[0m"
        )

    def write(self):
        """
        Copies a file from the source path to the destination path.
        """
        shutil.copyfile(self.src_path, self.destination_path)


class AssetWriter(BaseFileWriter):
    """
    Writes an entire directory of assets to the specified destination path
    """

    def log_info(self):
        """
        Prints a status message that the file writing operation is taking place
        """
        print(
            "\033[94m"
            + f"Copying contents from directory {self.src_path} to {self.destination_path}..."
            + "\033[0m"
        )

    def write(self):
        """
        Copies a directory of assets to the destination directory.
        """
        shutil.copytree(self.src_path, self.destination_path)


class CSSWriter(BaseFileWriter):
    """
    Handles writing all CSS files to the destination directory as a single CSS file
    """

    def log_info(self):
        """
        Prints a status message that the css file writing operation is taking place
        """
        print(
            "\033[94m"
            + f"Combining all stylesheets from {self.src_path} "
            + f"to {self.destination_path.rstrip('/')}/main.css..."
            + "\033[0m"
        )

    def write(self):
        """
        Combines all CSS files and writes to the destination directory
        """
        destination_path = self.destination_path.rstrip("/") + "/"
        os.makedirs(destination_path)
        css_files = []

        for file in os.listdir(self.src_path):
            if file.endswith(".css"):
                css_files.append(file)

        with open(f"{destination_path}main.css", "w", encoding="utf-8") as outfile:
            for index, css_file in enumerate(css_files):
                css_file_path = os.path.join(self.src_path, css_file)
                with open(css_file_path, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
                # Add a newline character after each file's content, skipping last iteration
                if index < len(css_files) - 1:
                    outfile.write("\n\n")


@dataclass
class Writer:
    """
    Holds logic for writing static site files to `/dist`,
    including favicon, scripts, styles, and images
    """

    favicon: BaseFileWriter
    scripts: AssetWriter
    images: AssetWriter
    styles: CSSWriter


@dataclass
class Loader:
    """
    Holds logic for loading data from markdown and JSON files and
    providing render arguments as a dictionary
    """

    markdown: MarkdownLoader
    json: JSONLoader


class StaticSiteGenerator:
    """
    Handles generating a static website in the `/dist` directory by combining components needed
    to render templates and static assets.
    """

    def __init__(
        self, template_handler: TemplateHandler, loader: Loader, writer: Writer
    ):
        """
        Initializes the StaticSiteGenerator with the necessary components
        for generating a static site.

        :param template_handler: An instance of TemplateHandler for managing templates.
        :param loader: An instance of Loader for loading markdown and JSON content.
        :param writer: An instance of Writer for writing static assets.
        """
        self.template_handler = template_handler
        self.loader = loader
        self.writer = writer

    def get_proj_abs_path(self):
        """
        Returns the absolute path of the project root directory
        """
        return os.path.dirname(os.path.abspath(__file__))

    def get_build_dir_path(self, build_dir="dist"):
        """
        Constructs the absolute path of the build directory from the project root
        """
        project_root = self.get_proj_abs_path()
        return os.path.join(project_root, build_dir)

    def clear_build_dir(self, build_dir="dist"):
        """
        Removes the current `dist` directory
        """
        build_dir_path = self.get_build_dir_path(build_dir)
        if os.path.exists(build_dir_path):
            # If /dist exists, clear it
            shutil.rmtree(build_dir_path)

    def refresh_and_create_new_build_dir(self, build_dir="dist"):
        """
        Clears build directory if exists and creates a new one
        """
        build_dir_path = self.get_build_dir_path(build_dir)
        self.clear_build_dir(build_dir_path)
        os.makedirs(build_dir_path)

    def build(self):
        """
        Builds the static site by combining templates, markdown content,
        JSON arguments, and static assets.

        This method performs the following steps:
        1. Reads markdown files and converts them to HTML.
        2. Loads JSON configuration and data.
        3. Clears the destination directory and creates a new one.
        4. Writes the favicon, index.html, and linked HTML pages.
        5. Copies scripts, assets, and combines all stylesheets into one file.
        """
        render_args = {}
        # Read the markdown file as html
        print("\033[94m" + "Reading markdown files...")
        render_args.update(self.loader.markdown.load_render_args())
        # Load configuration
        print("\033[94m" + "Loading JSON...")
        render_args.update(self.loader.json.load_render_args())

        # Clear destination directory if exists and create new empty directory
        self.refresh_and_create_new_build_dir()

        self.writer.favicon.write()
        # Write static index HTML file from dynamic templates
        print("\033[94m" + "Writing to dist/index.html...")
        self.template_handler.write_index_html(render_args)
        # Write static index HTML file from dynamic templates
        print("\033[94m" + "Writing html from src/theme/views/pages to /dist...")
        self.template_handler.write_linked_html_pages(render_args)
        # Copy static assets
        print("\033[94m" + "Writing static assets to dist/static/...")
        # Copy scripts
        print("\033[94m" + "Copying scripts...")
        self.writer.scripts.write()
        # Copy assets
        print("\033[94m" + "Copying images...")
        self.writer.images.write()
        # Copy all stylesheets into one file
        print(
            "\033[94m" + "Combining all stylesheets into dist/static/styles/main.css..."
        )
        self.writer.styles.write()
        print("\033[92m" + "Site build successfully completed!" + "\033[0m")


def build_static_site():
    """
    Builds a static site by initializing the necessary components and calling the build method.

    This function sets up the TemplateHandler, MarkdownLoader, JSONLoader, and various writers for
    favicon, scripts, images, and CSS. It then creates a StaticSiteGenerator instance and calls
    its build method to generate the static site.
    """
    template_handler = TemplateHandler(
        ["src/theme/views/", "src/theme/views/partials/", "src/theme/views/pages/"]
    )
    markdown_loader = MarkdownLoader("src/theme/markdown/")
    json_loader = JSONLoader("src/config.json")
    favicon_writer = BaseFileWriter("src/favicon.ico", "dist/favicon.ico")
    script_writer = AssetWriter("src/theme/static/scripts", "dist/static/scripts")
    image_writer = AssetWriter("src/theme/static/images", "dist/static/images")
    css_writer = CSSWriter("src/theme/static/styles/", "dist/static/styles/")

    loader = Loader(markdown_loader, json_loader)
    writer = Writer(favicon_writer, script_writer, image_writer, css_writer)

    site_generator = StaticSiteGenerator(template_handler, loader, writer)
    site_generator.build()


if __name__ == "__main__":
    build_static_site()
