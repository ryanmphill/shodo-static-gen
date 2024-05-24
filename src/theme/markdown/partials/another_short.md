## This is Another Short Article!

It was dynamically added to the page by passing a variable to the template with the same name as the markdown file! To include short bits of markdown in your template like this, simply add the markdown file to `markdown/partials`, and the variable will be exposed to all templates. You can render it in the template using the jinja variable syntax:

```
{{ name_of_markdown_file }}
```

## Article Pages

In addition to partial variables that can be included in templates, entire new pages can also be automatically be generated from markdown files added to the 
`markdown/articles` directory, like [this example](/blog/first-blog). The path will match what is defined in the `markdown/articles` directory, and reusable layout wrapper templates can be defined in `views/articles` by adding a `layout.jinja` file under the desired directory that matches the path defined in `markdown/articles`. In the `layout.jinja` file, control where you would like your content to be dynamically inserted by passing in the reserved `{{ article }}` variable. Click on the example to learn more.


## CSS

You can create as many css files as you'd like, and no need to import them, because they will all be compiled
into a single css file during the build process.