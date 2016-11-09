# Running the server and tests

Once you have installed everything, run the following commands for launching the server or running the tests.

| Command | Purpose |
| --- | --- |
| `flask run` | Launch the server |
| `./run_tests.sh` | Run the tests |

These commands should be executed in the root directory of the site.

In order to run the server, two environment variables need to be set:

| Environment variable | Description | Value |
| FLASK_APP | Path to the Flask app file | `site_app` |
| FLASK_CONFIG | Configuration to use (`development`, `testing` or `production`) | 

So in order to launch the site with the development configuration you would execute

```bash
export FLASK_APP=site_app.py
export FLASK_CONFIG=development
flask run
```

Obviously it would be a bit tedious to have to type the export commands over and over again. You may avoid this by adding them to the activation script of the virtual environment, `venv/bin/activate`

```bash
# set Flask variables
export FLASK_APP=site_app.py
export FLASK_CONFIG=development
```

and unsetting them in the script's deactivate function

```bash
# unset Flask variables
if [ ! "$1" = "nondestructive" ] ; then
    unset FLASK_APP
    unset FLASK_CONFIG
fi
```
