# Shodo Static Site Generator

This is a Python script I am putting together that builds a static site from markdown, Jinja2 templates, and static assets (CSS, JavaScript, images, etc). This currently only supports a single page website, but I am working to expand it soon!

## How it works

First, there is the main layout template located at `src/theme/views.layout.jinja` that can render partial sub-views, which can either be other Jinja2 templates located in `src/theme/views/partials`, or markdown files located in `src/theme/mardown`. 

#### Templates

This project uses Jinja2 as its templating engine, so it would be beneficial to visit the Jinja [docs](https://jinja.palletsprojects.com/en/3.1.x/). This project leverages Jinja to integrate with Python and build HTML from templates that have acces to functions and variables.

#### Markdown

Any markdown files added to the `/markdown` directory will be exposed to `layout.jinja` with a variable name identical to the markdown file name, minus the extension. So, the contents of `article.md` can be passed to the jinja template as `{{ article }}`, where it will be converted to HTML upon running the build script.

#### Dynamic data

For rendering dynamic data, Jinja Macros can be used for looping through a passed argument. Simply use the `macro` keyword in the partial template, like the following example:

```
{% macro loop_template(items) -%}
    <ul>
    {%- for item in items %}
        <li>{{ item }}</li>
    {%- endfor %}
    </ul>
{%- endmacro %}
```

Then, it can be included in the layout:

```
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

## Getting Started

Make sure you have `pipenv` installed

Pull down the repository, run `pipenv shell`

Start making changes to `src/theme/views/layout.jinja`

Run `Python build.py` from the main project directory when your ready to generate the site

Find your static site located in the `dist/` directory