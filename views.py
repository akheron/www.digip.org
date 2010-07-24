import operator
import os
import models

def index(context):
    return context.render_template('index.html', index=models.index)

def project(context, project):
    return context.render_template('project.html',
                                   index=models.index,
                                   project=models.projects[project])

def redirect(context, url):
    return context.render_template('redirect.html', url=url)
