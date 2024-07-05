"""
This module script is similar to running `python3 -m http.server --bind 127.0.0.1 3000 -d dist`
from the command line, but automatically runs the build script prior to starting up
the web server
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import sys
from shodo_ssg import SettingsLoader, build_static_site

def start_server(path_from_root: str, port=3000):
    """
    Starts a development web server using Python's http.server
    """

    settings = SettingsLoader(path_from_root)
    directory_to_serve = settings.data["build_dir"]

    class Handler(SimpleHTTPRequestHandler):
        """
        Extends Python's SimpleHTTPRequestHandler to overide the default directory
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory_to_serve, **kwargs)

    handler = Handler

    # Create the server
    with ThreadingHTTPServer(("", port), handler) as httpd:
        print(
            "\033[96m"
            + f"Serving HTTP on 127.0.0.1 port {port} ( http://127.0.0.1:{port}/ )..."
            + "\033[95m"
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:  # ^C to stop server, triggering __exit__ method
            print("\n" + "\033[96m" + "Gracefully shutting down..." + "\033[0m")
            sys.exit(0)  # Exit the program with a successful status code


if __name__ == "__main__":
    # Set the ROOT_PATH variable to the directory of this file
    root_path = os.path.dirname(os.path.abspath(__file__))
    build_static_site(root_path)
    start_server(root_path)
