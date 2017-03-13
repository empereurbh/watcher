import core
import dominate
from cherrypy import expose
from dominate.tags import *
from header import Header
from head import Head
import json
import os


class ImportLibrary():

    @expose
    def default(self):
        doc = dominate.document(title='Watcher')
        doc.attributes['lang'] = 'en'

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/import_library.css?v=02.22')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}import_library.css?v=02.22'.format(core.CONFIG['Server']['theme']))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/import_library/main.js?v=03.03')

        with doc:
            Header.insert_header(current=None)
            with div(id='content'):
                h1('Import Library')
                with div(id='scan_dir'):
                    with div(id='directory_info'):
                        span('Library directory: ')
                        input(id='directory', type='text', placeholder=' /movies', style='width:20em')
                        with div(id='browse'):
                            i(cls='fa fa-ellipsis-h')
                        br()
                        span('Minimum file size to import: ')
                        input(id='minsize', type='number', value='500')
                        span('MB.')
                        br()
                        i(cls='fa fa-check-square checkbox', id='recursive', value='True')
                        span('Scan recursively.')
                        with div():
                            with span(id='start_scan'):
                                i(cls='fa fa-binoculars', id='start_scan')
                                span('Start scan')

                    with div(id='browser', cls='hidden'):
                        div(os.getcwd(), id='current_dir')
                        with ul(id='file_list'):
                            ImportLibrary.file_list(core.PROG_PATH)
                        with div(id='browser_actions'):
                            i(id='select_dir', cls='fa fa-check-circle')
                            i(id='close_browser', cls='fa fa-times-circle')

                with div(id='wait'):
                    span('Scanning library for new movies.')
                    br()
                    span('This may take several minutes.')

                with div(id='wait_importing', cls='hidden'):
                    span('Importing selected movies.')
                    br()
                    span('This may take several minutes.')

            div(id='overlay')
            div(id='thinker')
        return doc.render()

    @staticmethod
    def file_list(directory):
        subdirs = [i for i in os.listdir(directory) if os.path.isdir(os.path.join(directory, i))]

        subdirs.insert(0, '..')

        html = ''

        for i in subdirs:
            html += unicode(li(i))

        return html

    @staticmethod
    def render_review(review_movies, incomplete_movies):
        with div(id='list_files') as div_list:
            if not review_movies and not incomplete_movies:
                with span('No movies found.', id='not_found'):
                    br()
                    with a(href=u'{}/import_library'.format(core.URL_BASE)):
                        i(cls='fa fa-caret-left')
                        span('Return')
            else:
                if review_movies:
                    with div(id='review'):
                        span('The following files have been found.', cls='title')
                        br()
                        span('Review and un-check any unwanted files.', cls='title')
                        with table(cls='files'):
                            with tr():
                                th('Import')
                                th('File Path')
                                th('Title')
                                th('IMDB ID')
                                th('Source')
                                th('Size')
                            for path, movie in review_movies.iteritems():
                                source = movie['resolution']
                                with tr():
                                    td(json.dumps(movie), cls='hidden data')
                                    with td():
                                        i(cls='fa fa-check-square checkbox', value='True')
                                    td(path, cls='short_name')
                                    td(movie['title'])
                                    td(movie['imdbid'])
                                    with td():
                                        with select(cls='input_resolution'):
                                            for src in core.RESOLUTIONS:
                                                if src == source:
                                                    option(src, value=src, selected='selected')
                                                else:
                                                    option(src, value=src)
                                    td(u'{} MB'.format(movie['size'] / 1024**2))
                if incomplete_movies:
                    with div(id='incomplete'):
                        span('The following movies are missing key data.', cls='title')
                        br()
                        span('Please fill out or correct IMDB ID and source, or uncheck to ignore.', cls='title')
                        with table(cls='files'):
                            with tr():
                                th('Import')
                                th('File Path')
                                th('Title')
                                th('IMDB ID')
                                th('Source')
                                th('Size')
                            for path, movie in incomplete_movies.iteritems():
                                source = movie.get('resolution', 'BluRay-1080P')
                                with tr():
                                    td(json.dumps(movie), cls='hidden data')
                                    with td():
                                        i(cls='fa fa-check-square checkbox', value='True')
                                    td(path, cls='short_name')
                                    td(movie.get('title'))
                                    with td():
                                        input(type='text', placeholder='tt0123456', cls='input_imdbid', value=movie['imdbid'] or '')
                                    with td():
                                        with select(cls='input_resolution'):
                                            for src in core.RESOLUTIONS:
                                                if src == source:
                                                    option(src, value=src, selected='selected')
                                                else:
                                                    option(src, value=src)
                                    td(u'{} MB'.format(movie['size'] / 1024**2))
                with span(id='import'):
                    i(cls='fa fa-check-circle')
                    span('Import')
        return unicode(div_list)

    @staticmethod
    def render_complete(successful, failed):
        with div(id='results') as div_results:

            if failed:
                span('The following movies failed to import.')
                with table(id='failed'):
                    with tr():
                        th('File Path')
                        th('Error')
                    for movie in failed:
                        with tr():
                            td(movie['filepath'])
                            td(movie['error'])
            if successful:
                span('Successfully imported the following movies.')
                with table(id='success'):
                    with tr():
                        th('Title')
                        th('IMDB ID')
                    for movie in successful:
                        with tr():
                            td(u'{} ({})'.format(movie['title'], movie['year']))
                            td(movie['imdbid'])

            with a(id='finished', href=u'{}/status'.format(core.URL_BASE)):
                i(cls='fa fa-thumbs-o-up')
                span('Cool')
        return unicode(div_results)

# pylama:ignore=W0401
