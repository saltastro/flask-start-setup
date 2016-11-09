# Using Bokeh

By default, this framework will launch a Bokeh server on your deployment server, which allows you to add interactive Bokeh plots to your site. If you don't need this you should:

* Remove the `bokeh_server` directory.
* Update `supervisor.conf`.
* Update `nginx.conf`.
* Optionally, update `fabfile.py`

If you don't need Bokeh at all, you should also:

* Remove the Bokeh related content from the head block in `app/templates/base.html`.
* Remove the file `app/bokeh_util.py`.
* Remove the Bokeh requirement from the file `requirements.txt`.

By default the Bokeh server is listening on port 5100, but you may change the port by setting the `DEPLOY_BOKEH_SERVER_PORT` environment variable.
```

## Static Bokeh plots

In order to include a static Bokeh plot on a page, you may just use Bokeh's `components` function to generate the required html. Here is a simple example of how a route with a plot might could look like.

```python
@main.route('/sine')
def sine_plot():
    p = Figure(title='Sine')

    x = np.linspace(-10, 10, 200)
    y = np.sin(x)

    p.line(x=x, y=y)

    script, div = components(p)

    return render_template('plot.html', script=script, div=div)
```

The template `app/templates/plot.html` might look as follows.

```
{% extends 'base.html' %}

{% block page_content %}
<div>
    {{ script | safe }}
    {{ div | safe }}
</div>
{% endblock %}
```

## Interactive Bokeh plots

Bokeh supports interactivity by adding JavaScript to your plot or by hosting your plot on a Bokeh server. You can use both on the data quality site.

In order to add JavaScript to your plot, you may define a callback with CustomJS and pass this callback to a widget constructor. See [http://bokeh.pydata.org/en/latest/docs/user_guide/interaction/callbacks.html](http://bokeh.pydata.org/en/latest/docs/user_guide/interaction/callbacks.html) for examples.

While adding JavaScript in this way is straightforward, it is limited. For example, you cannot perform a new database query. Also, it is arguably much easier to define your callbacks in Python, enjoying full IDE support, rather than to have write a string containing JavaScript code.

These shortcomings fall away if you use a Bokeh server for hosting your plot, as then you you can add (Python) callbacks to your widgets which can update your plot's source data. An example of this is shown below.

**Plots served by the Bokeh server are not password-protected.** If you require authentication, you have to add this to the nginx configuration.

You need to put the file with your plot in the folder `bokeh_server`. All files in this folder (but not in its subfolders) is assumed to contain a plot to be hosted. So you should avoid putting helper files in this folder (although you are perfectly fine to put them in subfolders).

In order to include an interactive plot on a page, you have to use Bokeh's `autoload_server` function to get the necessary html. So a plot function might look as follows.

```python
@data_quality(name='interactive_downtime_plot', caption='Telescope downtime.')
def content():
    up = urlparse(request.url)
    scheme = up.scheme
    host = up.netloc
    port = up.port
    if port:
        host = host[:-(len(str(port)) + 1)]
    bokeh_server_url = '{scheme}://{host}:5100'.format(scheme=scheme, host=host)
    script = autoload_server(model=None, app_path='/telescope_downtime', url=bokeh_server_url)
    return '<div>' + script + '</div>'
```

The plot for this would have to be defined in a file `bokeh_server/telescope_downtime.py`. Note the port number 5100; this is not the default port (5006) of a Bokeh server.

## Example: an interactive plot with a two-dimensional Gaussian distribution

Assume you want to display a two-dimensional Gaussian distribution centred on the the origin and let the user choose a standard deviation as well as a cutoff value for the distance from the origin. When the user changes the standard deviation, the current set of random points is replaced with a new points. Points beyond the cutoff should have a lower opacity.

Then you could create a file `bokeh_server/gaussian.py with the following Python code.

```python
import math
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Range1d
from bokeh.models.widgets import Slider
from bokeh.plotting import ColumnDataSource, Figure

# --------------------------------------------------------
#
# An interactive plot showing normally distributed points.
#
# --------------------------------------------------------

# number of points shown in the plot
NUM_POINTS = 100

standard_deviation_slider = Slider(title='standard deviation', value=2, start=0, end=4)
cutoff_slider = Slider(title='maximum radius', value=4, start=0, end=8)

source = ColumnDataSource()


def update_source_data(new_points):
    """Update the source data.

    If new_points is True, random points will be generated. A normal distribution is used, and its standard deviation
    is the value of the standard deviation slider.

    The opacity of the points is chosen according to whether their distance from the origin is greater than the value
    of the cutoff slider.

    Params:
    -------
    new_points: bool
        Whether to generate new points.
    """

    standard_deviation = standard_deviation_slider.value
    cutoff = cutoff_slider.value

    # generate new points if requested

    if new_points:
        if standard_deviation > 0:
            x = np.random.normal(0, standard_deviation, NUM_POINTS)
            y = np.random.normal(0, standard_deviation, NUM_POINTS)
        else:
            x = np.zeros(NUM_POINTS)
            y = np.zeros(NUM_POINTS)
        source.data['x'] = x
        source.data['y'] = y

    # update the opacity

    def radius(u, v):
        """The distance from the origin."""

        return math.sqrt(u ** 2 + v ** 2)

    x = source.data['x']
    y = source.data['y']
    alpha = [1 if radius(x[i], y[i]) <= cutoff else 0.1 for i in range(NUM_POINTS)]

    source.data['alpha'] = alpha


# initialize the plot data
update_source_data(True)

# make the plot responsive to slider changes
standard_deviation_slider.on_change('value', lambda attr, old_value, new_value: update_source_data(True))
cutoff_slider.on_change('value', lambda attr, old_value, new_value: update_source_data(False))

# create the figure

p = Figure(title='Normal Distribution')

p.scatter(source=source, x='x', y='y', color='green', alpha='alpha', radius=0.1)

p.x_range = Range1d(start=-8, end=8)
p.y_range = Range1d(start=-8, end=8)

content = column(standard_deviation_slider, cutoff_slider, p)

# register the figure

curdoc().add_root(content)
curdoc().title = 'Normal Distribution'
```

Then a Flask route with this plot could be realised as follows.

```python
from urllib.parse import urlparse

from bokeh.embed import autoload_server
from flask import request


@main.route('/gaussian')
def gaussian():
    up = urlparse(request.url)
    scheme = up.scheme
    host = up.netloc
    port = up.port
    if port:
        host = host[:-(len(str(port)) + 1)]
    bokeh_server_url = '{scheme}://{host}:5100'.format(scheme=scheme, host=host)
    script = autoload_server(model=None, app_path='/gaussian', url=bokeh_server_url)
    return '<div>' + script + '</div>'
```

## Testing interactive Bokeh plots

In order to test an interactive plot (in a filer `bokeh_serve/gaussian.py`, say), go to the `bokeh_server` folder and start a Bokeh server with the plot file.

```bash
source venv/bin/activate
cd bokeh_server
bokeh serve gaussian.py
```

You can then view the plot by pointing a browser at `http://localhost:5006/gaussian`.
