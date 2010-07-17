import os
try:
    import json
    # Check that it's from stdlib
    if not all(hasattr(json, x) for x in ['load', 'loads', 'dump', 'dumps']):
        raise ImportError('Wrong json module (probably python-json)')
except ImportError:
    import simplejson as json

class Project(object):
    def __init__(self, slug):
        path = os.path.join('pagedata/projects', slug)

        fobj = open(os.path.join(path, 'project.json'))
        try:
            metadata = json.load(fobj)
        finally:
            fobj.close()

        self.slug = slug
        self.name = metadata['name']
        self.description = metadata['description']

        fobj = open(os.path.join(path, 'index.html'))
        try:
            self.index = fobj.read()
        finally:
            fobj.close()

    def __lt__(self, other):
        return self.name < other.name

projects = {}
for dir in os.walk('pagedata/projects').next()[1]:
    projects[dir] = Project(os.path.basename(dir))


class Index(object):
    def __init__(self, projects):
        self.projects = sorted(projects.values())

index = Index(projects)
