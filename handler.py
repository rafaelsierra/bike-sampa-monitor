# -*- coding: utf-8 -*-
import webapp2
import jinja2
import os
import datetime
from google.appengine.api import memcache
from model import Estacao

jinjao = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        html = memcache.get('home-html')
        if html:
            self.response.write(html)
            return

        hoje = datetime.date.today()
        estacoes = Estacao.query(Estacao.data == hoje).order(Estacao.numero)

        template_values = {
            'estacoes': estacoes.fetch(),
            'last_update': memcache.get('last-update')
        }
        template = jinjao.get_template('index.html')
        html = template.render(template_values)
        memcache.set('home-html', html)
        self.response.write(html)


class UpdateData(webapp2.RequestHandler):
    def get(self):
        Estacao.update_data()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('done')          

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/update', UpdateData),
], debug=True)