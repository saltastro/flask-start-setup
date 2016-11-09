# Authentication

Authentication with Flask-Login is included. If you don't need this, you should remove the folder `app/auth`, remove the login manager initialisation

```python
from flask.ext.login import LoginManager
...
login_manager = LoginManager()
...
def create_app(config_name):
    ...
    login_manager.init_app(app)
    ...
```

from the app's initialisation file `app/_init__.py`, remove the folder `app/templates/auth` and remove the Flask-Login dependency

```
Flask-Login==x.y.z
```

from the file `requirements.txt` in the root folder. (`x.y.z` denotes a version number.)

The file `app/auth/views.py` contains an example implementation of a user class, as well as the functions required for the login manager. While you have to replace these with whatever need in your project, they should give you an idea of how to work with the login manager. More details can be found in Chapter 8 of Miguel Grinberg's book *Flask Web Development* (O'Reilly).
