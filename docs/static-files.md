# Static files

Static files should be put in the directory `app/static` (which is Flask's default). Static files have two problems:

1. They should be bundled together, to avoid unnecessarily many HTTP requests.
2. More importantly, they are cached by browsers, and you must ensure that an updated version will actually be loaded by the browser.

This framework addresses both issues by using the Flask-Assets library, which creates bundles and attaches a GET parameter based on the bundles hash. To make use of this, you first have to define your bundles in the root-level file `webassets.yaml`. Here is an example:

```yaml
js-all:
    filters: rjsmin
    output: cache/all.%(version)s.js
    contents:
        - js/a.js
        - js/b.js
        - js/c/d.js

css-all:
    filters: yui_css
    output: cache/all.%(version)s.css
    contents:
        - css/main/a.css
        - css/main/b.css
```

Note the dashes before the file paths - these are indeed required! Also note the '%(version)s' - this is a placeholder to be replaced with the first characters of the bundle's hash.

Then you can include any of the defined bundles in a Jinja2 template by using the `assets` tag. For example,

```
{% block scripts %}
{{ super() }}
{% assets 'js-all' %}
<script src="{{ ASSET_URL }}"></script>
{% endassets %}
{% endblock %}
```

The generated bundles are put in the directory `app/static/cache`. When running the server in test or development mode, the original, individual files rather than the bundles will be included.

The deploy script automatically generates the bundles on the production server, rather than relying on them being created on the fly when a page is requested. This implies that you *don't* have to give the web user write access to the bundle directory. That user still needs write access to the directory `app/static/.webassets_cache`, though, and the deploy script takes care of that.

Some care must be taken when it comes to unit tests. If the Flask-Assets environment is defined as a global variable, running more than one unit test may result in multiple registration of the same bundle, which results in an error of the form

```
webassets.env.RegisterError: Another bundle is already registered as ...
```

This framework circumvents the issue by removing all existing bundles before attempting to load bundles in the app's `__init__.py` file.
