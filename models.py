import operator
import os
import simplejson
from util import rst

class NewsItem(object):
    def __init__(self, project, date, title, text):
        self.project = project
        self.date = date
        self.title = title
        self.text = text

    def __lt__(self, other):
        return self.date < other.date


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

        if os.path.isdir(os.path.join(path, 'news')):
            def _generate():
                for filename in os.listdir(os.path.join(path, 'news')):
                    date = os.path.splitext(filename)[0]
                    title, text = rst(os.path.join(path, 'news', filename))
                    yield NewsItem(self, date, title, text)
            self.all_news = sorted(_generate(), reverse=True)
        else:
            self.all_news = []

        self.news = self.all_news[:5]

    def __lt__(self, other):
        return self.name < other.name

projects = {}
for dir in next(os.walk('pagedata/projects'))[1]:
    projects[dir] = Project(os.path.basename(dir))


class Index(object):
    def __init__(self, projects):
        self.projects = sorted(projects.values())
        self.all_news = reduce(operator.add, (x.news for x in self.projects))
        self.all_news.sort(reverse=True)
        self.news = self.all_news[:5]

index = Index(projects)
