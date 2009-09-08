import stango
import views
import models

index_file = 'index.html'
autoreload = ['pagedata/']

files = stango.files(
    ('', views.index),
    ('petri/', views.redirect, {'url': '/'}),
)

files += stango.files(
    ('jansson/', views.project, {'project': 'jansson'}),
    ('jansson/doc/', views.redirect, {'url': '1.0/'}),
)

files += stango.files_from_tar(
    'jansson/doc/1.0/',
    'pagedata/projects/jansson/doc-current.tar.bz2',
    strip=1,
 )

files += stango.files(
    ('stango/', views.project, {'project': 'stango'}),
)
