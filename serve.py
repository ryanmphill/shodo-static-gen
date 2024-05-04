# This script is similar to running `python3 -m http.server --bind 127.0.0.1 3000 -d dist`
# from the command line, but automatically runs the build script prior to starting up
# the web server
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from build import build_assets

# Define the directory to serve
directory_to_serve = 'dist'
port = 8000

def start_server():
    # Target static files
    os.chdir(directory_to_serve)
    # Create the server
    with HTTPServer(('', port), SimpleHTTPRequestHandler) as httpd:
        print("\033[96m" + f"Serving HTTP on 127.0.0.1 port 8000 (http://127.0.0.1:{port}/)..." + "\033[95m")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt: # ^C to stop server, triggering __exit__ method
            print("\n" + "\033[96m" + "Gracefully shutting down..." + "\033[0m")

if __name__ == "__main__":
    build_assets()
    start_server()
