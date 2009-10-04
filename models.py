import os
import simplejson

class Project(object):
    def __init__(self, slug):
        path = os.path.join('pagedata/projects', slug)
        with open(os.path.join(path, 'project.json')) as fobj:
            metadata = simplejson.load(fobj)

        self.slug = slug
        self.name = metadata['name']
        self.description = metadata['description']

        with open(os.path.join(path, 'index.html')) as fobj:
            self.index = fobj.read()

    def __lt__(self, other):
        return self.name < other.name

projects = {}
for dir in next(os.walk('pagedata/projects'))[1]:
    projects[dir] = Project(os.path.basename(dir))


class Index(object):
    def __init__(self, projects):
        self.projects = sorted(projects.values())

index = Index(projects)
