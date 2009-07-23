import stango
import views
import models

index_file = 'index.html'

files = stango.files(('', views.index))
for project in models.projects.values():
    files += stango.files(
        ('%s/' % project.slug, views.project, {'project': project}),
        ('%s/releases/' % project.slug, views.releases, {'project': project})
    )
