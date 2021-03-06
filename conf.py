from stango.files import Files, files_from_dir

import os
import sys

sys.path.insert(0, 'lib')
from lib.blog import Blog
from lib.pygments_extension import PygmentsExtension

index_file = 'index.html'
autoreload = ['blog/', 'static/']
jinja_extensions = [PygmentsExtension]

blog = Blog(
    'blog/', 'blog',
    default_author='Petri Lehtinen',
    entry_suffix='.html',
)

news_entries = 5


# Views
def render_template(name, ctx={}):
    return lambda context: context.render_template(name, **ctx)


def project(name):
    tag = blog.tags.get(name)
    if tag:
        ctx = {
            'news': list(reversed(tag.entries))[:news_entries],
        }
    else:
        ctx = {}

    return render_template('%s/index.html' % name, ctx)


def redirect(context, url):
    return context.render_template('redirect.html', url=url)


files = Files(
    # Index
    ('', render_template('index.html')),

    # About
    ('about/', render_template('about.html')),

    # Static files
    files_from_dir('', 'static', strip=1),

    # Blog
    blog.files,

    # Jansson
    ('jansson/', project('jansson')),

    # Sala
    ('sala/', project('sala')),

    # Stango
    ('stango/', project('stango')),

    # Autotoolized Lua
    ('autotoolized-lua/', project('autotoolized-lua')),

    # cube.js
    ('cubejs/demo/index.html', render_template('cubejs/demo/index.html')),
    ('cubejs/demo/demo.html', render_template('cubejs/demo/demo.html')),
)

# Post-render hook: Add Google Analytics script into all .html files.
# This cannot be done in the base template, as all HTML files are
# not generated from templates.
#
# Asynchronous Google Analytics snippet from
# http://mathiasbynens.be/notes/async-analytics-snippet

analytics_script = '''\
<script>
  var _gaq = [['_setAccount', 'UA-10422726-1'], ['_trackPageview']];
  (function(d, t) {
  var g = d.createElement(t), s = d.getElementsByTagName(t)[0];
  g.async = true; g.src = '//www.google-analytics.com/ga.js'; s.parentNode.insertBefore(g, s);
  })(document, 'script');
</script>
'''.encode('utf-8')


def post_render_hook(context, data):
    # Don't add the analytics script when using the Stango test server
    if context.mode == 'serving':
        return data

    name, ext = os.path.splitext(context.realpath)
    if ext != '.html':
        return data

    offset = data.find(b'</body>')
    if offset == -1:
        return data

    return data[:offset] + analytics_script + data[offset:]
