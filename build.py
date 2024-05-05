from markdown2 import markdown # Will convert markdown file to html
from jinja2 import Environment, FileSystemLoader # Take layout.jinja, inject markdown into it and create final output html
from json import load
import os
import shutil

# Bring in layout and all other templates with Jinja
# Load directly from the file in the relavent directories
def build_assets():
    template_paths = ['src/theme/views/', 'src/theme/views/partials/', 'src/theme/views/pages/']
    template_env = Environment(loader=FileSystemLoader(searchpath=template_paths))
    root_template = template_env.get_template('layout.jinja')

    # Set the render arguments
    render_args = {}

    # Read the markdown file as html
    print('\033[94m' + 'Reading markdown files...')

    # Identify the markdown files
    md_src_dir = 'src/theme/markdown/'
    md_files = []

    for file in os.listdir(md_src_dir):
        if file.endswith('.md'):
            md_files.append(file)

    for md_file in md_files:
        md_file_path = os.path.join(md_src_dir, md_file)
        md_var_name = os.path.splitext(md_file)[0]
        with open(md_file_path) as markdown_file:
            render_args[md_var_name] = markdown(markdown_file.read(), 
                            extras=['fenced-code-blocks', 'code-friendly'])

    # Load configuration
    print('\033[94m' + 'Loading configuration...')
    with open('src/config.json') as config_file:
        config: dict = load(config_file)

    for key in config.keys():
        render_args[key] = config[key]

    # Compile HTML in /dist directory

    # Clear destination directory if exists and create new empty directory
    destination_dir = 'dist/'

    if os.path.exists(destination_dir):
        # If /dist it exists, clear it
        shutil.rmtree(destination_dir)

    os.makedirs(destination_dir)

    # Check for existance of favicon in the root dir and copy to dist
    favicon_link = ''
    if os.path.exists('src/favicon.ico'):
        shutil.copyfile('src/favicon.ico', 'dist/favicon.ico')
        favicon_link = '<link rel="icon" type="image/x-icon" href="/favicon.ico">'
    
    # Create Document Head
    def create_doc_head(styles_link, favicon_link): 
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{ render_args['site_title'] }</title>
            {favicon_link}
            <link href="{styles_link}" rel="stylesheet" />
        </head>
        <body>
        """.strip() + "\n"

    # Create Document Tail
    def create_doc_tail(script_link): 
        return f"""
            <script type="module" src="{script_link}"></script>
        </body>
    </html>
    """.strip()

    doc_head = create_doc_head("/static/styles/main.css", favicon_link)
    doc_tail = create_doc_tail("/static/scripts/main.js")

    # Write static index HTML file from dynamic templates
    print('\033[94m' + 'Writing to dist/index.html...')
    with open('dist/index.html', 'w') as output_file: # use 'w' to open for writing, not reading
        output_file.write(
            doc_head +
            root_template.render(
                render_args
            )
            + "\n" + doc_tail
        )

    # Write static linked HTML pages from dynamic templates
    pages_src_dir = 'src/theme/views/pages/'
    if os.path.exists(pages_src_dir) and os.listdir(pages_src_dir):
        os.makedirs('dist/pages/')
        for file in os.listdir(pages_src_dir):
            if file.endswith('.jinja') or file.endswith('.j2') or file.endswith('.jinja2'):
                template = template_env.get_template(file)
                page_name = os.path.splitext(file)[0]
                os.makedirs(f"dist/pages/{page_name}")
                with open(f"dist/pages/{page_name}/index.html", 'w') as output_file: # use 'w' to open for writing, not reading
                    output_file.write(
                        doc_head +
                        template.render(
                            render_args
                        )
                        + "\n" + doc_tail
                    )

    # Copy static assets
    print('\033[94m' + 'Compiling static assets to dist/static/...')

    # Copy scripts
    print('\033[94m' + 'Copying scripts to dist/static/scripts...')
    src_static_scripts_dir = 'src/theme/static/scripts'
    dist_static_scripts_dir = 'dist/static/scripts'

    # Copy the static directory from src to dist
    shutil.copytree(src_static_scripts_dir, dist_static_scripts_dir)

    # Copy assets
    print('\033[94m' + 'Copying assets to dist/static/assets...')
    src_static_assets_dir = 'src/theme/static/assets'
    dist_static_assets_dir = 'dist/static/assets'

    # Copy the static directory from src to dist
    shutil.copytree(src_static_assets_dir, dist_static_assets_dir)

    # Copy all stylesheets into one file
    print('\033[94m' + 'Combining all stylesheets into dist/static/styles/main.css...')
    os.makedirs('dist/static/styles/')
    # Identify CSS files
    css_src_dir = 'src/theme/static/styles/'
    css_files = []

    for file in os.listdir(css_src_dir):
        if file.endswith('.css'):
            css_files.append(file)

    # Combine CSS files
    combined_css_file = 'dist/static/styles/main.css'

    with open(combined_css_file, 'w') as outfile:
        for index, css_file in enumerate(css_files):
            css_file_path = os.path.join(css_src_dir, css_file)
            with open(css_file_path, 'r') as infile:
                outfile.write(infile.read())
            # Add a newline character after each file's content, skipping last iteration
            if index < len(css_files) - 1:
                outfile.write("\n\n")

    print('\033[92m' + 'Site build successfully completed!' + '\033[0m')

if __name__ == "__main__":
    build_assets()
