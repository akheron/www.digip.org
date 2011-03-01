from datetime import datetime
import bisect
import os
import re

from stango.files import Files

__all__ = ['Blog']

url_ok = re.compile(r'[a-zA-Z0-9.~_-]')
def slugify(text):
    from unicodedata import normalize

    normalized = []
    for ch in text:
        norm = normalize('NFKD', ch)[0]
        if url_ok.match(norm):
            normalized.append(norm)
        else:
            if normalized and normalized[-1] != '-':
                # Don't make two consecutive dashes or append a dash
                # to the beginning
                normalized.append('-')

    return ''.join(normalized).rstrip('-').lower()


class BlogEntry(object):
    def __init__(self, filename, headers, content):
        self.filename = filename
        self.title = headers['title']
        if 'slug' in headers:
            self.slug = headers['slug']
        else:
            self.slug = slugify(self.title)
        self.author = headers.get('author', None)
        self.date = headers['date']
        self.tags = headers['tags']
        self.content = self.process_content(content)
        self.url = None

    def process_content(self, content):
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import HtmlFormatter

        sub = '<pre class="highlight '
        start = content.find(sub)
        while start != -1:
            lang_start = start + len(sub)
            lang_end = content.find('">', start)
            code_start = lang_end + len('">')
            code_end = content.find('</pre>', start)
            end = code_end + len('</pre>')

            code = content[code_start:code_end]
            lexer = get_lexer_by_name(content[lang_start:lang_end])
            formatter = HtmlFormatter(cssclass="pygments")
            highlighted = highlight(code, lexer, formatter)

            content = content[:start] + highlighted + content[end + 1:]
            start = content.find(sub)

        return content

    def __hash__(self):
        return hash(self.slug)

    def __lt__(self, other):
        return self.date < other.date


class Tag(object):
    def __init__(self, name):
        self.name = name
        self.entries = []
        self.url = None

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return 'Tag(%r)' % self.name

    def add_entry(self, entry):
        bisect.insort(self.entries, entry)


ALL_HEADERS = {'author', 'date', 'title', 'tags'}
REQUIRED_HEADERS = {'title'}

def parse_entry(path):
    headers = {}
    with open(path) as fobj:
        for lineno, line in enumerate(fobj):
            if not line.strip():
                break
            try:
                key, value = line.split(':', 1)
            except ValueError:
                raise ValueError('%s:%d: Invalid header' % (path, lineno + 1))

            headers[key.strip().lower()] = value.strip()

        # Rest is the entry text
        content = fobj.read()

    unknown_headers = set(headers.keys()) - ALL_HEADERS
    if unknown_headers:
        raise ValueError('%s: Unknown headers %s' %
                         (path, ', '.join(unknown_headers)))

    for key in REQUIRED_HEADERS:
        if key not in headers:
            raise ValueError('%s: Header %r is required' % (path, key))

    if 'tags' in headers:
        headers['tags'] = headers['tags'].split()
    else:
        headers['tags'] = []

    DATE_FORMATS = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    ]
    if 'date' in headers:
        # Excplicit date set by the user
        date = headers['date']
        for fmt in DATE_FORMATS:
            try:
                headers['date'] = datetime.strptime(date, fmt)
                break
            except ValueError:
                pass
        else:
            raise ValueError('%s: Unable to parse date %r' % (path, date))
    else:
        # Use file's mtime as the date
        headers['date'] = datetime.fromtimestamp(os.path.getmtime(path))

    # Assign empty value for other missing optional headers
    for key in ALL_HEADERS:
        headers.setdefault(key, '')

    return BlogEntry(path, headers, content)


def scan(dirpath):
    for filename in os.listdir(dirpath):
        path = os.path.join(dirpath, filename)
        if not os.path.isfile(path):
            continue

        yield parse_entry(path)


class Blog(object):
    def __init__(self, prefix, datadir,
                 entry_suffix='.html',
                 entries_per_page=5,
                 feed_entries=30,
                 default_author='',
                 date_format='%Y-%m-%d',
                 tag_pattern=r'^[a-zA-Z0-9.~_-]+$',
                 extra_context={}):
        self.prefix = prefix
        self.abs_prefix = '/' + prefix
        self.datadir = datadir
        self.tag_pattern = re.compile(tag_pattern)
        self.extra_context = extra_context

        # Preferences
        self.entry_suffix = entry_suffix
        self.entries_per_page = entries_per_page
        self.feed_entries = feed_entries

        self.tags = {}
        self.archive = {}

        self.entries = sorted(
            scan(self.datadir),
            key=lambda x: [x.date, x.filename],
            reverse=True
        )

        self.total_pages = len(self.entries) // self.entries_per_page
        if len(self.entries) % self.entries_per_page != 0:
            self.total_pages += 1

        for entry in self.entries:
            for tag_name in entry.tags:
                if not self.tag_pattern.match(tag_name):
                    raise ValueError('%s: Invalid tag: %s' % (entry.slug, tag))

                self.tags.setdefault(tag_name, Tag(tag_name)).add_entry(entry)

            entry.tags = [self.tags[tag_name] for tag_name in entry.tags]

            year = entry.date.year
            month = entry.date.month
            try:
                self.archive[year][month].insert(0, entry)
            except KeyError:
                try:
                    self.archive[year][month] = [entry]
                except KeyError:
                    self.archive[year] = {month: [entry]}

            if not entry.author and default_author:
                entry.author = default_author

            entry.date_str = entry.date.strftime(date_format)

            entry.url = '%s%d/%02d/%s%s' % \
                (self.abs_prefix, year, month, entry.slug, self.entry_suffix)

        for tag in self.tags.values():
            tag.url = '%stags/%s/' % (self.abs_prefix, tag.name)

    @property
    def files(self):
        result = Files(
            ('', self.blog_index),
            (
                'feed.atom',
                self.atom,
                {'feed_id': 'feed.atom', 'entries': self.entries}
            ),
            ('archive/', self.archive_index),
        )

        for page in range(2, self.total_pages):
            first_entry = (page - 1) * self.entries_per_page
            result.append(('page/%s' % page, self.blog_index,
                           {'page': page, 'first_entry': first_entry}))

        for entry in self.entries:
            year = entry.date.year
            month = entry.date.month
            url = '%d/%02d/%s%s' % (year, month, entry.slug, self.entry_suffix)
            result.append((url, self.view_entry, {'entry': entry}))

        for tag in self.tags.values():
            result += [
                ('tags/%s/' % tag.name, self.view_tag, {'tag': tag}),
            ]

        for year in self.archive:
            for month in self.archive[year]:
                result.append(('%d/%02d/' % (year, month), self.view_archive,
                               {'year': year, 'month': month}))

        # Prepend path prefix to all filespecs
        if self.prefix:
            return result.add_prefix(self.prefix)
        else:
            return result


    ### Views ###

    def _template_context(self, **kwargs):
        result = {}
        result['archive'] = self.archive
        result['tags'] = sorted(self.tags.values(), key=lambda x: x.name)
        result.update(kwargs)
        result.update(self.extra_context)
        return result

    def blog_index(self, context):
        ctx = self._template_context(entries=self.entries)
        return context.render_template('blog/index.html', **ctx)

    def archive_index(self, context):
        ctx = self._template_context()
        return context.render_template('blog/archive_index.html', **ctx)

    def view_entry(self, context, entry):
        ctx = self._template_context(entry=entry)
        return context.render_template('blog/entry.html', **ctx)

    def view_tag(self, context, tag):
        ctx = self._template_context(tag=tag)
        return context.render_template('blog/tag.html', **ctx)

    def view_archive(self, context, year, month):
        ctx = self._template_context(
            year=year,
            month=month,
            entries=self.archive[year][month],
        )
        return context.render_template('blog/archive.html', **ctx)

    def atom(self, context, feed_id, entries, feed_name=None):
        return context.render_template(
            'blog/feed.atom',
            entries=entries[:self.feed_entries],
            feed_id='/' + self.prefix + feed_id,
            feed_name=feed_name,
        )
