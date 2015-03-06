# -*- coding: utf-8 -*-
import webapp2
import jinja2
import os
import datetime

from model import Estacao

jinjao = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        hoje = datetime.date.today()
        estacoes = Estacao.query(Estacao.data == hoje).order(Estacao.numero)
        
        template_values = {
            'estacoes': estacoes.fetch(),
        }
        template = jinjao.get_template('index.html')
        self.response.write(template.render(template_values))


class UpdateData(webapp2.RequestHandler):
    def get(self):
        Estacao.update_data()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('done')          

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/update', UpdateData),
], debug=True)