# Adding plots (and other files)

*All* Python files in this directory will be served as Bokeh plots on the deployment server. While serving files not containing a Bokeh plot doesn't seem to cause much of a problem, avoid putting non-plot files in the directory.

Files in subdirectories are *not* served; so putting helper files in a subdirectory is perfectly fine.

Note that by default scripts in this directory cannot access other packages in this project which aren't included in this directory. If you need to import anything from these directories, you'll have to add them to the Python path using `sys.path.append`.
