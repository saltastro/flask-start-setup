# Forms

This framework doesn't ship with any form library. However, the following notes might be of help if you need to create forms for your site.

* Using Flask-WTF is a good idea. It can be installed with `pip install Flask-WTF`.
* Flask-Bootstrap comes with a template function `quick_form` for easily generating a form in Jinja2 template. However, more often than not you are better off rolling your own html.
* By default, Flask WTF uses CSRF, and that's a good thing. But in some cases, it's unnecessary. For example, imagine a page showing a plot of the exchange rate of the Rand for a user-supplied date range. When you load the page, last week should be inserted as the date range into the date input field, and the corresponding plot should be shown. As there is no CSRF token when you load the page by a GET request, this wouldn't be possible with CSRF enabled. To disable it, pass `csrf_enabled=False` to the form constructor.
* If you want to do whatever the form is for (such as showing the plot of exchange rates in the note above) irrespective of whether the user has hit the submit button, you can use Flask-WTF's `validate` (rather than `validate_on_submit`) method for form validation.
* When creating WTForm input elements in a Jinja2 template, you may use the `class_` argument to set the element's class attribute. This is particularly useful if you want to add, say, a datepicker.

The following example illustrates these points.

```python
import datetime

from flask import render_template
from flask_wtf import Form
from wtforms.fields import DateField, SubmitField
from wtforms.validators import DataRequired


class DateRangeForm(Form):
    """A form for entering a date range.

    Default values can be supplied for both the start and date of the range. These will be used if the field value
    isn't set from the GET or POST request parameters.

    CSRF is disabled for this form.

    Params:
    -------
    default_start_date: date
        Default to use as start date.
    default_end_date: date
        Default to use as end date.
    """

    start_date = DateField('Start', validators=[DataRequired()])
    end_date = DateField('End', validators=[DataRequired()])
    submit = SubmitField('Query')

    def __init__(self, default_start_date=None, default_end_date=None):
        Form.__init__(self, csrf_enabled=False)

        # change empty fields to default values
        if not self.start_date.data and default_start_date:
            self.start_date.data = default_start_date
        if not self.end_date.data and default_end_date:
            self.end_date.data = default_end_date

    def html(self):
        return render_template('date_range_form.html', form=self)


@route('/exchange-rate', methods=['GET', 'POST'])
def exchange_rate():
    """Display the exchange rate for a user-supplied date range.

    The content is created if the form is valid, irrespective of whether a GET or POST request is made. Otherwise only
    the form is included.
    """

     form = DateRangeForm(datetime.date.today() - datetime.timedelta(days=7), datetime.date.today())
    if form.validate():
        start_date = form.start_date.data
        end_date = form.end_date.data
        query_results = '<div>Here be the exchange rate from {start_date} to {end_date}.</div>' \
            .format(start_date=start_date, end_date=end_date)
    else:
        query_results = ''
    return '<DOCTYPE html>\n' \
           '<html>\n' \
           '<body>' + form.html() + query_results + '</body>\n' \
           '</html>'
```

The required template (called `date_range_form.html` in the code above) could look as follows.

```html
<form method="POST" class="form-group">
    {{ form.hidden_tag() }}
    {{ form.start_date.label() }} {{ form.start_date(class_='datepicker') }}
    {% if form.start_date.errors %}
        {% for e in form.start_date.errors %}
            <span class="error">{{ e }}</span>
        {% endfor %}
    {% endif %}
    {{ form.end_date.label() }} {{ form.end_date(class_='datepicker') }}
    {% if form.end_date.errors %}
        {% for e in form.end_date.errors %}
            <span class="error">{{ e }}</span>
        {% endfor %}
    {% endif %}
    {{ form.submit() }}
</form>
```
