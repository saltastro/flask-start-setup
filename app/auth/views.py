from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import login_user, logout_user, UserMixin

from . import auth
from .. import login_manager
from .forms import LoginForm


class DummyUser(UserMixin):
    """A dummy user class.

    This class is for illustrative purposes only and shouldn't be used in production code.

    Params:
    -------
    username: str
        Username of the user.
    """

    def __init__(self, username):
        self.username = username

    def get_id(self):
        """Return the user id.

        The user id is the same as the username.

        Returns:
        --------
        unicode
            The user id.
        """

        return self.username

    def verify_password(self, password):
        """Verifies whether the given password is valid for this user. This is the case only if both the username and
        the password are 'test'.

        Params:
        -------
        password: str
            Password

        Returns:
        --------
        bool
            Whether the password is valid.
        """
        return self.username == 'test' and password == 'test'


@login_manager.user_loader
def load__user(id):
    """Load a user.

    The loaded user is the DummyUser with the given id as its username.

    Params:
    -------
    id: unicode

    Returns:
    --------
    DummyUser:
       The user with the given id.
    """

    return DummyUser(id)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Try to log in the user.

    If a valid username and password are supplied, the corresponding user is logged in. Otherwise the login form is
    displayed. In case of an invalid or missing username or password, an error message is included with the form.
    """

    form = LoginForm()
    if form.validate_on_submit():
        user = DummyUser(form.username.data)
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Incorrect username or password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    """Log the user out.

    After logging the user out, the home page is requested.
    """

    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
