# Error handling

The main blueprint includes some barebones error handlers in `app/main/errors.py`, which you have to customise. You might also want to add additional error handlers in this file, such as for file not found or authentication errors.

It is a good idea to log internal server errors and raised exceptions using logger described in the section on logging. The `errors.py` file does this in the `exception_raised` function.
