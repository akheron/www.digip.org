import os
import stango
import views
import models

index_file = 'index.html'
autoreload = ['pagedata/']

files = stango.files()

# Static files
files += stango.files.from_dir('', 'static', strip=1)

# Index
files += stango.files(
    ('', views.index),
)

# Jansson
files += stango.files(
    ('jansson/', views.project, {'project': 'jansson'}),
    ('jansson/doc/', views.redirect, {'url': '1.2/'}),
)
files += stango.files.from_tar(
    'jansson/doc/1.0/',
    'pagedata/projects/jansson/doc-1.0.tar.bz2',
    strip=1,
)
files += stango.files.from_tar(
    'jansson/doc/1.1/',
    'pagedata/projects/jansson/doc-1.1.tar.bz2',
    strip=1,
)
files += stango.files.from_tar(
    'jansson/doc/1.2/',
    'pagedata/projects/jansson/doc-1.2.tar.bz2',
    strip=1,
)

# Stango
files += stango.files(
    ('stango/', views.project, {'project': 'stango'}),
)

# Autotoolized Lua
files += stango.files(
    ('autotoolized-lua/', views.project, {'project': 'autotoolized-lua'}),
)


# Post-render hook
analytics_script = '''\
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-10422726-1");
pageTracker._trackPageview();
} catch(err) {}</script>
'''

def post_render_hook(path, data):
    name, ext = os.path.splitext(path)
    if ext != '.html':
        return data

    offset = data.find('</body>')
    if offset == -1:
        return data

    return data[:offset] + analytics_script + data[offset:]

