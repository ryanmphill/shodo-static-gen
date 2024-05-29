# Shodo Static Site Generator

This is a Python script I am putting together that builds a static site from markdown, Jinja2 templates, and static assets (CSS, JavaScript, images, etc). Edit your site in the `src` directory, and access the build in the `dist` directory!

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
__________layout.jinja (Maps to markdown/../updates, overwrites other previous layouts in tree)
```

###### layout.jinja

The `layout.jinja` is just a normal jinja template, but the `{{ article }}` variable has been reserved as a `children` variable for passing in the content from each page. Simply define whatever repeated layout you would like to wrap the `{{ article }}` content, such as a header and footer.

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

#### Dynamic data

For rendering dynamic data, Jinja Macros can be used for looping through a passed argument. Simply use the `macro` keyword in the partial template, like the following example:

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

#### config.json

Any property defined in `config.json` will automatically expose a variable with the same name to all jinja templates that has the cooresponding value of the `config.json` property.

#### build_settings.json

This is where all source paths and project settings are defined.

NOTE: _Any path included in `root_template_paths` will have all of its children directories recursively added to the search path for Jinja2, so only top level paths should be included in the settings. In most cases, `"root_template_paths": [ "src/theme/views/" ]` should suffice, but it would be possible to add another path to `src/theme/assets/images` for example if you wanted to use the templates for working with an SVG but still wanted to maintain separation of concerns._

## Getting Started

Make sure you have `pipenv` installed

Pull down the repository, run `pipenv shell`

Start making changes to `src/theme/views/home.jinja`

Run `Python site_builder.py` from the main project directory when your ready to generate the site

Find your static site located in the `dist/` directory

For development, run `Python serve.py` from the root project directory. This will build the site in the `dist` directory with the latest changes from `src` and serve it on localhost!

## Project Conventions

#### Jinja templates

For all jinja templates, use the `.jinja` file extension. Other extensions such as `.j2` or `.jinja2` are not fully supported at this time.

###### Syntax Highlighting
If you're using VSCode, the [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) extension is recommended for full syntax highlighting out of the box using the `.jinja` extension. Other extensions will work, although you might need to configure the settings to look for the `.jinja` extension.

#### For Contributors
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project uses the [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) and follows the [current style guide](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)