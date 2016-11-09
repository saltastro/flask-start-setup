# Templates

The `templates` folder contains a base template (`base.html`), a home page (`index.html`) and an authentication form (`auth/login.html`). All of these should be customised to suit your needs.

While all of the templates use Flask-Bootstrap, there is of course no need for that. If you don't want to use Bootstrap, you should remove the line

```html
{% extends "bootstrap/base.html" %}
```

from `base.html`, the line

```html
{% import "bootstrap/wtf.html" as wtf %}
```

from `auth/login.html` (and update the rest of that template accordingly), the Bootstrap initialisation

```python
from flask_bootstrap import Bootstrap
...
bootstrap = Bootstrap()
...
def create_app(config_name):
    ...
    bootstrap.init_app(app)
    ...
```

from the app's init file (`app/__init__.py`), and the Flask-Bootstrap dependency

```
Flask-Bootstrap==w.x.y.z
```

from the file `requirements.txt` in the root folder. (`w.x.y.z` denotes a version number.)
