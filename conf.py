from stango.files import *

import os
import sys

sys.path.insert(0, 'lib')
from lib.blog import Blog

index_file = 'index.html'
autoreload = ['blog/', 'static/']

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
            'news': reversed(tag.entries[:news_entries]),
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
    ('jansson/doc/', redirect, {'url': '2.0/'}),

    # Stango
    ('stango/', project('stango')),

    # Autotoolized Lua
    ('autotoolized-lua/', project('autotoolized-lua')),
)

# Jansson documentation
for version in ['1.0', '1.1', '1.2', '1.3', '2.0']:
    files += files_from_tar(
        'jansson/doc/%s/' % version,
        'jansson/doc-%s.tar.bz2' % version,
        strip=1,
    )

# Post-view hook: Add Google Analytics script into all .html files.
# This cannot be done in the base template, as all HTML files are
# generated from templates (e.g. Jansson's documentation files).
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
