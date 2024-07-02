### Variable Prefixes for Markdown Content

In order to avoid any naming conflicts, The articles further nested in directories within "articles/partials/" will have a variable prefix that is the accumulated names of the preceding directories in dot notation (excluding '/partials' and higher). 

For example, a markdown file located in `markdown/partials/collections/quotes/my_quote.md`, will be exposed to all templates with the following variable using the jinja variable syntax:

```
{{ collections.quotes.my_quote }}
```

## Article Pages

In addition to partial variables that can be included in templates, entire new pages can also be automatically be generated from markdown files added to the 
`markdown/articles` directory, like [this example](/blog/first-blog). The path will match what is defined in the `markdown/articles` directory, and reusable layout wrapper templates can be defined in `views/articles` by adding a `layout.jinja` file under the desired directory that matches the path defined in `markdown/articles`. In the `layout.jinja` file, control where you would like your content to be dynamically inserted by passing in the reserved `{{ article }}` variable. Click on the example to learn more.


## CSS

You can create as many css files as you'd like, and no need to import them, because they will all be compiled
into a single css file during the build process.