import stango
import views
import models

index_file = 'index.html'
autoreload = ['pagedata/']

files = stango.files(
    ('', views.index),
    ('petri/', views.redirect, {'url': '/'}),
)

for project in models.projects.values():
    files += stango.files(
        ('%s/' % project.slug, views.project, {'project': project}),
    )
