import operator
import os
import models
from stango.shortcuts import render_template

def index():
    return render_template('index.html', index=models.index)

def project(project):
    return render_template('project.html', index=models.index, project=project)

def redirect(url):
    return render_template('redirect.html', url=url)
