## This is the subheading for a short article written with markdown

This is the article body

You can write another paragraph here by double spacing.

You can also write out code blocks in the markdown file:

```python
def myfunction():
    return 'Hello'
```

It was dynamically added to the page by passing a variable to the template with the same name as the markdown file! To include short bits of markdown in your template like this, simply add the markdown file to `markdown/partials`, and the variable will be exposed to all templates. You can render it in the template using the jinja variable syntax:

```
{{ name_of_markdown_file }}
```