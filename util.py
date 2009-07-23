from docutils.core import publish_parts

def rst(filename):
    with open(filename) as fobj:
        parts = publish_parts(source=fobj.read(), writer_name='html')
    return parts['title'], parts['body']
