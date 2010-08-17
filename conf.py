from stango.files import *
import os
import views

index_file = 'index.html'
autoreload = ['pagedata/']

files = Files(
    # Index
    ('', views.index),

    # Static files
    files_from_dir('', 'static', strip=1),

    # Jansson
    ('jansson/', views.project, {'project': 'jansson'}),
    ('jansson/doc/', views.redirect, {'url': '1.3/'}),

    # Stango
    ('stango/', views.project, {'project': 'stango'}),

    # Autotoolized Lua
    ('autotoolized-lua/', views.project, {'project': 'autotoolized-lua'}),
)

# Jansson documentation
for version in ['1.0', '1.1', '1.2', '1.3']:
    files += files_from_tar(
        'jansson/doc/%s/' % version,
        'pagedata/projects/jansson/doc-%s.tar.bz2' % version,
        strip=1,
    )

# Post-view hook: Add Google Analytics script into all .html files.
# This cannot be done in the base template, as all HTML files are
# generated from templates (e.g. Jansson's documentation files).

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
'''.encode('utf-8')

def post_view_hook(context, data):
    # Don't add the analytics script when using the Stango test server
    if context.serving:
        return data

    name, ext = os.path.splitext(context.filespec.realpath)
    if ext != '.html':
        return data

    offset = data.find(b'</body>')
    if offset == -1:
        return data

    return data[:offset] + analytics_script + data[offset:]
