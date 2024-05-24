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
        with open(
            destination_dir, "w", encoding="utf-8"
        ) as output_file:  # use 'w' to open for writing, not reading
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
                    os.path.dirname(os.path.abspath(__file__)), pages_src_dir + path
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


class DataLoader(ABC):
    """
    Abstract base class for loading data from files.
    """

    def __init__(self, src_path: str):
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
        # Append all files if src_path is directory
        if os.path.isdir(self.src_path):
            for file in os.listdir(self.src_path):
                files.append(file)
        # Append single file if src_path is file
        if os.path.isfile(self.src_path):
            files.append(self.src_path)
        return files

    @abstractmethod
    def load_args(self):
        """
        Load data from the specified file path.
        This method must be implemented by subclasses.
        """


class MarkdownLoader(DataLoader):
    """
    Handles the loading of markdown files as well as their conversion to html
    strings. Extends DataLoader
    """

    def list_files(self, sub_dir="partials") -> list[tuple[str]]:
        """
        Lists all markdown files in the root path specified during class initialization. Returns
        list of tuple pairs packed with the directory path followed by the file name.
        """
        md_files = []
        md_dirs = self._get_nested_markdown_dirs(os.path.join(self.src_path, sub_dir))
        for md_dir_path in md_dirs:
            for file in os.listdir(md_dir_path):
                if file.endswith(".md"):
                    md_files.append((md_dir_path, file))
        return md_files

    def _log_info(self):
        """
        Prints a status message that markdown files are being read and loaded
        """
        print("\033[94m" + "Reading markdown files..." + "\033[0m")

    def _convert_to_html(self, markdown_file: TextIOWrapper) -> str:
        """
        Takes an open markdown file and converts it to an html string
        """
        return markdown(
            markdown_file.read(), extras=["fenced-code-blocks", "code-friendly"]
        )

    def load_args(self):
        """
        Load html converted from markdown files as a dictionary of render arguments,
        where the key is the name of the markdown file, and the value is the converted
        html string to be inserted in the templates.
        """
        self._log_info()
        converted_html = {}
        for md_dir_path, md_file in self.list_files():
            md_file_path = os.path.join(md_dir_path, md_file)
            md_var_name = os.path.splitext(md_file)[0]
            with open(md_file_path, "r", encoding="utf-8") as markdown_file:
                converted_html[md_var_name] = self._convert_to_html(markdown_file)
        return converted_html

    def load_pages(self) -> list[dict[str, str]]:
        """
        Load html for markdown articles and prepare data for each to be loaded
        as a separate page. Returns list of dictionaries with the following
        key/value pairs:
            `"html"`: The full converted html string,
            `"url_segment"`: The path to the markdown file from the markdown/articles directory,
                            used for matching a layout template to the `.md` file
            `"name"`: The name of the file, minus the extension
        """
        markdown_pages = []
        for md_dir_path, md_file in self.list_files("articles"):
            page = {}
            md_file_path = os.path.join(md_dir_path, md_file)
            with open(md_file_path, "r", encoding="utf-8") as markdown_file:
                page["html"] = self._convert_to_html(markdown_file)
            page["url_segment"] = md_dir_path.replace("src/theme/markdown/articles", "")
            page["name"] = os.path.splitext(md_file)[0]
            markdown_pages.append(page)
        return markdown_pages

    def _get_nested_markdown_dirs(
        self, markdown_path="src/theme/markdown/partials", markdown_dirs=None
    ) -> list[str]:
        """
        Retrieves all children directories of a parent markdown directory as a list
        """
        markdown_path = markdown_path.rstrip("/") + "/"

        if markdown_dirs is None:
            markdown_dirs = []

        markdown_dirs.append(markdown_path)
        for path in os.listdir(markdown_path):
            path_from_root = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), markdown_path + path
            )
            # For each directory, recursively append all a nested directories
            if os.path.isdir(path_from_root):
                markdown_dirs = self._get_nested_markdown_dirs(
                    markdown_path + path, markdown_dirs
                )
        # When no subdirectories remain, return list of markdown directories
        return markdown_dirs


class JSONLoader(DataLoader):
    """
    Handles the loading of JSON key value pairs to be inserted into
    templates as dictionary render arguments
    """

    def _log_info(self):
        """
        Prints a status message that JSON is being loaded
        """
        print("\033[94m" + "Loading JSON..." + "\033[0m")

    def load_args(self, verbose=True):
        """
        Load JSON from the specified file path as a Python dict, where the key is the
        variable name in the template files, and the value is the data to be inserted.
        """
        if verbose:
            self._log_info()
        with open(self.src_path, "r", encoding="utf-8") as config_file:
            config = load(config_file)

        if isinstance(config, dict):
            return config

        return {}


class SettingsLoader(JSONLoader):
    """
    Handles the loading of build settings, including source paths and the
    destination build directory
    """

    def __init__(self):
        """
        Extends the JSONLoader with the absolute path to the build settings
        as an argument.
        """
        super().__init__(
            src_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "build_settings.json"
            )
        )
        self._data = None

    @property
    def data(self):
        """
        The loaded arguments from the build settings json config file
        """
        if self._data is None:
            self._data = self.load_args(False)
            self._data["template_paths"] = self.get_all_template_paths(
                self._data["root_template_paths"]
            )
        return self._data

    def _log_info(self):
        """
        Prints a status message that JSON settings are being loaded
        """
        print("\033[94m" + "Loading settings and configuration..." + "\033[0m")

    def get_build_dir(self):
        """
        Returns the build directory from the build_settings.json with
        any trailing slashes removed
        """
        build_dir = self.data["build_dir"]
        if isinstance(build_dir, str):
            build_dir = build_dir.rstrip("/")
        else:
            build_dir = ""

        return build_dir

    def get_nested_template_dirs(
        self, template_path="src/theme/views/", template_dirs=None
    ):
        """
        Retrieves all children directories of a parent template directory as a list
        """
        template_path = template_path.rstrip("/") + "/"

        if template_dirs is None:
            template_dirs = []

        template_dirs.append(template_path)
        for path in os.listdir(template_path):
            path_from_root = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), template_path + path
            )
            # For each directory, recursively append all a nested directories
            if os.path.isdir(path_from_root):
                template_dirs = self.get_nested_template_dirs(
                    template_path + path, template_dirs
                )
        # When no subdirectories remain, return list of template directories
        return template_dirs

    def get_all_template_paths(self, root_template_paths: list[str]):
        """
        Retrieves a list of all nested template paths for each defined root template path
        """
        template_paths = []
        for path in root_template_paths:
            template_paths.extend(self.get_nested_template_dirs(path))

        return template_paths


class AssetWriter:
    """
    Base class for writing and compiling static assets that are to be included in the final build
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
            + f"Copying contents from {self.src_path} to {self.destination_path}..."
            + "\033[0m"
        )

    def write(self):
        """
        Copies contents of either a single file OR an entire directory from the
        provided source path to the destination path.
        """
        self.log_info()
        if os.path.isfile(self.src_path):
            shutil.copyfile(self.src_path, self.destination_path)
        if os.path.isdir(self.src_path):
            shutil.copytree(self.src_path, self.destination_path)


class CSSWriter(AssetWriter):
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
        self.log_info()
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
class AssetHandler:
    """
    Holds logic for writing static site files to the build directory,
    including favicon, scripts, styles, and images
    """

    favicon: AssetWriter
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
        self,
        template_handler: TemplateHandler,
        loader: Loader,
        asset_handler: AssetHandler,
    ):
        """
        Initializes the StaticSiteGenerator with the necessary components
        for generating a static site.

        :param template_handler: An instance of TemplateHandler for managing templates.
        :param loader: An instance of Loader for loading markdown and JSON content.
        :param asset_handler: An instance of AssetHandler for writing static assets.
        """
        self.template_handler = template_handler
        self.loader = loader
        self.asset_handler = asset_handler
        self.build_dir = template_handler.build_dir

    def get_proj_abs_path(self):
        """
        Returns the absolute path of the project root directory
        """
        return os.path.dirname(os.path.abspath(__file__))

    def get_build_dir_path(self):
        """
        Constructs the absolute path of the build directory from the project root
        """
        project_root = self.get_proj_abs_path()
        return os.path.join(project_root, self.build_dir)

    def clear_build_dir(self):
        """
        Removes the current build directory
        """
        build_dir_path = self.get_build_dir_path()
        if os.path.exists(build_dir_path):
            # If build directory exists, clear it
            shutil.rmtree(build_dir_path)

    def refresh_and_create_new_build_dir(self):
        """
        Clears build directory if exists and creates a new one
        """
        build_dir_path = self.get_build_dir_path()
        self.clear_build_dir()
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
        # Load render arguments
        render_args = {}
        render_args.update(self.loader.markdown.load_args())
        render_args.update(self.loader.json.load_args())

        # Load markdown pages
        md_pages = self.loader.markdown.load_pages()

        # Clear destination directory if exists and create new empty directory
        self.refresh_and_create_new_build_dir()

        self.asset_handler.favicon.write()
        self.template_handler.write(render_args, md_pages)
        self.asset_handler.scripts.write()
        self.asset_handler.images.write()
        self.asset_handler.styles.write()
        print("\033[92m" + "Site build successfully completed!" + "\033[0m")


def build_static_site():
    """
    Builds a static site by initializing the necessary components and calling the build method.

    This function sets up the TemplateHandler, MarkdownLoader, JSONLoader, and various writers for
    favicon, scripts, images, and CSS. It then creates a StaticSiteGenerator instance and calls
    its build method to generate the static site.
    """
    settings_loader = SettingsLoader()
    args = settings_loader.data
    build_dir = settings_loader.get_build_dir()

    template_handler = TemplateHandler(args["template_paths"], build_dir)
    markdown_loader = MarkdownLoader(args["markdown_path"])
    json_loader = JSONLoader(args["json_config_path"])
    favicon_writer = AssetWriter(args["favicon_path"], f"{build_dir}/favicon.ico")
    script_writer = AssetWriter(args["scripts_path"], f"{build_dir}/static/scripts")
    image_writer = AssetWriter(args["images_path"], f"{build_dir}/static/images")
    css_writer = CSSWriter(args["styles_path"], f"{build_dir}/static/styles")

    loader = Loader(markdown_loader, json_loader)
    asset_handler = AssetHandler(
        favicon_writer, script_writer, image_writer, css_writer
    )

    site_generator = StaticSiteGenerator(template_handler, loader, asset_handler)
    site_generator.build()


if __name__ == "__main__":
    build_static_site()
