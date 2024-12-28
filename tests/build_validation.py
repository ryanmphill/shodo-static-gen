"""Utility functions for testing the build directory"""

import os


def get_linked_page_relative_build_paths(template_paths: list[str]):
    """Returns the expected relative paths to the linked template pages in the build directory"""
    # Get the source paths for the linked page directories
    linked_page_dirs: list[str] = []
    for path in template_paths:
        if "src/theme/views/pages/" in path:
            linked_page_dirs.append(path)
    # Get the source paths for the linked page template files
    linked_page_paths = []
    for path in linked_page_dirs:
        # get the file in the directory
        for file in os.listdir(path):
            if (
                file.endswith(".jinja")
                or file.endswith(".j2")
                or file.endswith(".jinja2")
            ):
                relative_path = (
                    path.split("src/theme/views/pages/")[-1].strip("/")
                    + "/"
                    + os.path.splitext(file)[0]
                )
                linked_page_paths.append(relative_path.strip("/"))

    return linked_page_paths


def linked_template_pages_exist_in_build_dir(build_dir_path, template_paths: list[str]):
    """Returns True if all linked template pages exist in the build directory"""
    linked_page_paths = get_linked_page_relative_build_paths(template_paths)
    for path in linked_page_paths:
        if not os.path.exists(os.path.join(build_dir_path, path)):
            return False
    return True


def markdown_pages_exist_in_build_dir(build_dir_path, md_pages: list[dict]):
    """Returns True if all markdown pages exist in the build directory"""
    for md_page in md_pages:
        page_build_path = os.path.join(
            build_dir_path,
            md_page["url_segment"].strip("/"),
            md_page["name"].strip("/"),
        )
        if not os.path.exists(page_build_path):
            return False
    return True


def scripts_exist_in_build_dir(build_dir_path, scripts_path_segment="static/scripts"):
    """Returns True if all scripts exist in the build directory"""
    scripts_build_path = os.path.join(build_dir_path, scripts_path_segment)
    if not os.path.exists(scripts_build_path):
        return False
    return True


def css_exist_in_build_dir(build_dir_path, styles_path_segment="static/styles"):
    """Returns True if all css exist in the build directory"""
    css_build_path = os.path.join(build_dir_path, styles_path_segment)
    if not os.path.exists(css_build_path):
        return False
    return True


def images_exist_in_build_dir(build_dir_path, images_path_segment="static/images"):
    """Returns True if all images exist in the build directory"""
    images_build_path = os.path.join(build_dir_path, images_path_segment)
    if not os.path.exists(images_build_path):
        return False
    return True


def favicon_exists_in_build_dir(build_dir_path, favicon_path_segment="favicon.ico"):
    """Returns True if the favicon exists in the build directory"""
    favicon_build_path = os.path.join(build_dir_path, favicon_path_segment)
    if not os.path.exists(favicon_build_path):
        return False
    return True
