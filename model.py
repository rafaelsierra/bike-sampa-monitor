# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import logging
import datetime
from bs4 import BeautifulSoup as BS
from google.appengine.api import memcache

logger = logging.getLogger('models')
# latitude, longitude, icone, Nome, IdEstacao, StatusOnline, 
# StatusOperacao, VagasOcupadas, numBicicletas, Endereco

class Estacao(ndb.Model):
    local = ndb.GeoPtProperty()
    nome = ndb.TextProperty()
    endereco = ndb.TextProperty()
    numero = ndb.IntegerProperty()
    status = ndb.TextProperty()
    funcionando = ndb.BooleanProperty()
    bicicletas = ndb.IntegerProperty(default=0)
    vagas = ndb.IntegerProperty(default=0)

    interacoes = ndb.IntegerProperty(default=0)
    data = ndb.DateProperty(auto_now_add=True)

    @classmethod
    def update_data(cls):
        url = 'http://ww2.mobilicidade.com.br/bikesampa/mapaestacao.asp'
        result = urlfetch.fetch(url)
        logger = logging.getLogger('update_data')
        if result.status_code != 200:
            logger.error('Falha ao baixar pagina: {}'.format(result.status_code))
            return

        soup = BS(result.content)
        funcoes = []
        for script in soup.find_all('script'):
            if 'src' in script or not script.string:
                continue

            if not 'exibirEstacaMapa' in script.string:
                continue

            linhas = script.string.splitlines()
            for i, linha in enumerate(linhas):
                if linha.startswith('exibirEstacaMapa'):
                    funcoes.append(linhas[i:i+10])
            break
        
        if not funcoes:
            logger.error('Falha ao encontrar as chamadas de funcao')
            return
        hoje = datetime.date.today()
        helper = lambda s, b, e: s.strip()[b:e]

        for funcao in funcoes:
            lat = helper(funcao[0],18,-2)
            lon = helper(funcao[1],1,-2)
            nome = helper(funcao[3],1,-2)
            numero = int(helper(funcao[4],1,-2))
            online = helper(funcao[5], 1, -2)
            operacao = helper(funcao[6], 1, -2)
            bicicletas = int(helper(funcao[7], 1, -2))
            vagas = int(helper(funcao[8], 1, -2))
            endereco = helper(funcao[9], 1, -3)

            estacao = Estacao.query(cls.data==hoje, cls.numero==numero).get()
            if not estacao:
                estacao = Estacao(numero=numero, data=hoje)

            if estacao.bicicletas != bicicletas:
                estacao.interacoes += abs(estacao.bicicletas-bicicletas)
                estacao.bicicletas = bicicletas
            
            estacao.local = ndb.GeoPt("{}, {}".format(lat, lon))
            estacao.nome = nome
            estacao.vagas = vagas
            estacao.endereco = endereco
            status = 'N/A'
            operando = False
            if operacao in ('EI', 'EM'):
                status = u'Manutenção/Implantação'
            else:
                if online == 'A' and operacao == 'EO':
                    status = u'Operando'
                    operando = True
                else:
                    status = u'Offline'
            estacao.status = status
            estacao.funcionando = operando
            estacao.put()

        memcache.delete('home-html')



