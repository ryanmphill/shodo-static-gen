 <p align="right">
 <img alt="Netlify Status" src="https://api.netlify.com/api/v1/badges/1ed945fb-7aa0-4ebd-89c0-45450ead70aa/deploy-status">
 <img alt="GitHub Pipenv locked Python version" src="https://img.shields.io/github/pipenv/locked/python-version/ryanmphill/shodo-static-gen">
 <img alt="GitHub License" src="https://img.shields.io/github/license/ryanmphill/shodo-static-gen?color=purple">
 <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/ryanmphill/shodo-static-gen/python-package.yml?label=Tests">
</p>

# Shodo Static Site Generator

Shodo is a framework for rapidly building a static site from markdown files, json, and Jinja templates. Simply make changes to your site in the `src` directory, run the build command, and access the build in the `dist` directory. [Easily deploy to Netlify](#deploy-to-netlify) in just a few clicks.

## Why Shodo?
There is no shortage of options out there for building websites and apps, but they can quickly feel overcomplicated when all you need is a simple website with a few reusable components. The goal of Shodo is to make publishing content to the web as simple and elegant as possible for developers, whether it's a personal blog, a portfolio, documentation, or a professional marketing site. 

## Getting Started

### Installing the package

1. Create a new project directory and start a virtual environment using your preferred method

2. Install the `shodo_ssg` package by running one of the following commands:

**Via pip**:
```bash
pip install git+https://github.com/ryanmphill/shodo-static-gen.git@main#egg=shodo_ssg
```

**Via pipenv**:
```bash
pipenv install git+https://github.com/ryanmphill/shodo-static-gen.git@main#egg=shodo_ssg
```

**Via Poetry**:
```bash
poetry add git+https://github.com/ryanmphill/shodo-static-gen.git@main#egg=shodo_ssg
```

**Via uv**:
```bash
uv pip install "shodo_ssg @ git+https://github.com/ryanmphill/shodo-static-gen.git@main"
```

3. Once the package is installed, you can scaffold a new project using the command

```bash
start-shodo-project <name of project directory>
```

To create the project in the current directory, run

```bash
start-shodo-project .
```

4. Build the starter site and serve it to localhost by running the following command from the root directory of the project:

```bash
python3 serve.py
```

You should now be able to view the site on localhost and can start by making changes to `home.jinja`. When you simply want to build the static site, run the following command from the root directory:

```bash
python3 site_builder.py
```

and you can find your static site located in the `dist/` directory

## How it works

First, there is the main home page template located at `src/theme/views/home.jinja` that can render partial sub-views, which can either be other Jinja2 templates located in `src/theme/views/partials`, or markdown files located in `src/theme/markdown`.

#### Templates

This project uses Jinja2 as its templating engine, so it would be beneficial to visit the Jinja [docs](https://jinja.palletsprojects.com/en/3.1.x/). This project leverages Jinja to integrate with Python and build HTML from templates that have access to functions and variables.

#### Pages

Any template added to the `pages/` directory will be written as an index.html file in its own subfolder within the `dist` directory. When linking between pages, simply write a backslash followed by the page name, exluding any file extensions. So if you wanted to link to `pages/linked-page.jinja` from `home.jinja`, the anchor tag would be

```html
<a href="/linked-page">Click Here!</a>
```

###### Nested Pages

You can create nested pages by adding a subdirectory within `pages/` with the name of the route. For routes with multiple pages, the index page of that route will need to be on the same level as the route subdirectory with the same name followed by the `.jinja` extension. For example:
```
__pages/
____about.jinja (template for '/about')
____nested.jinja (index template for '/nested')
____nested/
______nested-page.jinja (template for '/nested/nested-page')
```
#### Markdown

##### Partial markdown content to include in templates

Any markdown files added to the `/markdown/partials` directory will be exposed to Jinja templates with a variable name identical to the markdown file name, minus the extension. So, the contents of `summary.md` can be passed to the Jinja template as `{{ summary }}`, where it will be converted to HTML upon running the build script.

###### Prefixed variables for nested markdown directories

In order to avoid any naming conflicts, The articles further nested in directories within "articles/partials/" will have a variable prefix that is the accumulated names of the preceding directories in dot notation (excluding '/partials' and higher). 

For example, a markdown file located in `markdown/partials/collections/quotes/my_quote.md`, will be exposed to all templates with the following variable using the jinja variable syntax:

```
{{ collections.quotes.my_quote }}
```

##### Generating full pages from markdown

In addition to partial variables that can be included in templates, entire new pages can also be automatically be generated from markdown files added to the 
`markdown/articles` directory. The url path to the page will match what is defined in the `markdown/articles` directory.

Articles from the `markdown/articles` directory are rendered with a reusable template defined in `views/articles/` Just add a `layout.jinja` file under a subdirectory that matches the subdirectory tree used in `markdown/articles`, or simply define a `layout.jinja` at the root of `views/articles` if you want to use a single layout template for all articles. In the `layout.jinja` file, control where you would like your content to be dynamically inserted by passing in the reserved `{{ article }}` variable. More below.

The site builder will always match up the layout template that is closest in the tree, so `markdown/articles/blog/updates/new-post.md` would be matched with `views/articles/blog/layout.jinja` if no layout is defined for the `updates` directory.

```
__markdown/
____articles/
______blog/
________updates/
__________new-post.md
```

```
__views/
____articles/
______layout.jinja (default root layout for all markdown 'articles')
______blog/
________layout.jinja (Maps to markdown/articles/blog, overwrites root layout)
________updates/
__________layout.jinja (Maps to markdown/articles/blog/updates, overwrites other previous layouts in tree)
```

###### layout.jinja

The `layout.jinja` is just a normal jinja template, but the `{{ article }}` variable has been reserved for passing in the content from each file in `markdown/articles`. Simply define whatever repeated layout you would like to wrap the `{{ article }}` content, such as a header and footer.

Here is an example layout template:

```jinja
<div class="container">
    <header class="page-header">
        <h1 class="page-header__title">This is the root article layout</h1>
    </header>
    <main>
        {{ article }}
    </main>
    <footer>Thanks for reading</footer>
</div>
```

#### Loop through content

For dynamically rendering lists of content, Jinja Macros can be used to build components for looping through a passed argument. Simply use the `macro` keyword in the partial template, like the following example:

```jinja
{% macro loop_template(items) -%}
    <ul>
    {%- for item in items %}
        <li>{{ item }}</li>
    {%- endfor %}
    </ul>
{%- endmacro %}
```

Then, it can be included in the main template:

```jinja
{% from 'loop_template.jinja' import loop_template as loop_template %}
    {{ loop_template(['Content', 'to', 'loop', 'through']) }}
```

Then after running the build, the HTML should look like the following:

```html
<ul>
    <li>Content</li>
    <li>to</li>
    <li>loop</li>
    <li>through</li>
</ul>
```

#### JSON data in the `/store` directory

For easy configuration and keeping repeated values in one place, any property defined in a `.json` file within the `/store` directory will be passed to Jinja templates with an identical variable to the property name. Each nested object can be accessed using dot notation in the templates.

For example, to access the `title` value from `/store/config.json`:

```json
{
    "metadata": {
        "title": "Shodo - A Static Site Generator",
        "description": "Shodo is a static site generator that uses Markdown and JSON files to generate a static site.",
        "author": "Shodo"
    }
}
```

in the template, you would use the following syntax:

```
{{ metadata.title }}
```

#### build_settings.json

This is where all source paths and project settings are defined.

NOTE: _Any path included in `root_template_paths` will have all of its children directories recursively added to the search path for Jinja2, so only top level paths should be included in the settings. In most cases, `"root_template_paths": [ "src/theme/views/" ]` should suffice, but it would be possible to add another path to `src/theme/assets/images` for example if you wanted to use the templates for working with an SVG but still wanted to maintain separation of concerns._

## Deploy to Netlify
1. Allow Netlify to install the project dependencies

If you are using pipenv, Netflify will install dependencies directly from the `pipfile`. Otherwise, you will need to generate a `requirements.txt` file via `pip freeze > requirements.txt`, `poetry export --format=requirements.txt > requirements.txt`, `uv pip compile pyproject.toml -o requirements.txt`, or similar to allow the dependencies to be installed via pip.

### pipenv

If using pipenv, your `pipfile` dependency should look something like this:

```py
[packages]
shodo_ssg = {ref = "<specific-commit-hash-or-branch-goes-here>", git = "https://github.com/ryanmphill/shodo-static-gen.git"}
```

If you haven't already, generate the lock file via pipenv lock, then go ahead and verify the package is installable with the command pipenv sync.

If you installed the project via `pipenv install`, this was already done and you can move on to the next step

### pip

If using pip, after generating your `requirements.txt`, the file should look similar to this:

```py
Jinja2==3.1.5
markdown2==2.5.2
MarkupSafe==3.0.2
shodo_ssg @ git+https://github.com/ryanmphill/shodo-static-gen.git@<commit-hash>
```

2. Create a new repository on GitHub and push the Shodo project up to it
3. Now, we have everything we will need to build and deploy the static site on Netlify. We will have to make a few specifications since Netlify won't be able to autodetect everything about the build configuration
4. Choose "Add new site" on Netlify, and select the repository with your site
5. For the `build command`, specify `python site_builder.py`
6. Luckily, Netlify supports Python and will be able to automatically install dependencies from either the pipfile or requirements.txt. The only extra step we need to take is to change the default python version from 3.8 to 3.9. To do this, go to the environment variables section and add `PYTHON_VERSION` for the variable name, and `3.9` for the value.
7. Now click to deploy the site. After around a minute, verify that the build was successful, and you should be able to view the deployed site!

Reference: [Netlify Python Documentation](https://docs.netlify.com/configure-builds/manage-dependencies/#python)

## Project Conventions

#### Jinja templates

For all jinja templates, use the `.jinja` file extension. Other extensions such as `.j2` or `.jinja2` are not fully supported at this time.

###### Syntax Highlighting
If you're using VSCode, the [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) extension is recommended for full syntax highlighting out of the box using the `.jinja` extension. Other extensions will work, although you might need to configure the settings to look for the `.jinja` extension.

#### For Contributors
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project uses the [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) and follows the [current style guide](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)

##### Pulling down the repository and installing locally

1. Start up a virtual environment and install the dependencies using your preferred method after pulling down the repository

2. Once your virtual environment is activated, in the root of the project directory run `pip install -e .` (Don't forget the `.`)

3. Upon successful install, navigate to an entirely separate directory and run 

```bash
start-shodo-project <name of new project directory>
```

Upon success, a new starter project template should have been set up in the specified directory

Start editing by making changes to `src/theme/views/home.jinja`

5. Run `Python site_builder.py` from the main project directory when your ready to generate the site

Find your static site located in the `dist/` directory

For development, run `Python serve.py` from the root project directory. This will build the site in the `dist` directory with the latest changes from `src` and serve it on localhost.
