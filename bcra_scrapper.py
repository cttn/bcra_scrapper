import urllib
import sys
from bs4 import BeautifulSoup
from datetime import datetime as dt
import numpy as np
import pandas as pd


class BCRA:

    consulta={'indicadores': {'url_base':'http://www.bcra.gob.ar/SistemasFinancierosYdePagos/Entidades_financieras_indicadores_economicos.asp?bco=',
                               'secciones': ['capital','activos','eficiencia','rentabilidad','liquidez'],
                               'orden': [3,4,5,6,7]#Orden en el que aparece cada seccion en la lista de tablas
                              }, 
               'estructura':  {'url_base':'http://www.bcra.gob.ar/SistemasFinancierosYdePagos/Entidades_financieras_informacion_estructura.asp?Tit=4&bco=',
                               'secciones':['info_adicional','acred_bancaria'],
                               'orden':[4,5]
                              },
               'balance':     {'url_base':'http://www.bcra.gob.ar/SistemasFinancierosYdePagos/Entidades_financieras_estados_contables.asp?bco=',
                               'secciones': ['Balance'],
                               'orden':[3]
                              }
               }
    nombres={'Macro'      :'00285',
             'Frances'    :'00017',
             'RIO'        :'00072',
             'Galicia'    :'00007',
             'Patagonia'  :'00034',
             'Citibank'   :'00016',
             'HSBC'       :'00150',
             'Supervielle':'00027',
             'Comafi'     :'00299',
             'Columbia'   :'00389',
             'Hipotecario':'00044',
             'Mariva'     :'00254',
             'Julio'      :'00305',
             'Meridian'   :'00281',
             'Credicoop'  :'00191',
             'Paribas'    :'00266',
             'ICBC'       :'00015'}

    def __init__(self,nombre,fechas_datetime=True,debug=False):
        #tipo='estructura'
        if not debug:
            self.nombre=nombre
            self.datos={}
            for tipo, value in self.consulta.items():
                _url=self.consulta[tipo]['url_base']+self.nombres[nombre]
                _soup = self._obtener_html(_url)
                _tablas = self._obtener_tablas(_soup)
                _lista = self._to_dict_list(_tablas,tipo,fechas_datetime)
                self.datos[tipo] = self._list_dfs(_lista)
        else:
            self.url=self.consulta['estructura']['url_base']+self.nombres[nombre]
            self.soup = self._obtener_html(self.url)
            self.tablas = self._obtener_tablas(self.soup)
            #self.tablas=tablas
         
    def _list_dfs(self,lista):
        """Acá hay un problema. Sólo queda la primer seccion y se pierden las otras en el 'try'"""
        ldfs = []
        for i in lista:
            df = pd.DataFrame.from_dict(i)
            df.index=i['fecha']
            df.drop('fecha',1,inplace=True)
            try:
                df.drop('',axis=1,inplace=True)
            except:
                #print("Problema con ")
                pass
            df.index.name='fecha'
#            try:
            df = df.applymap(lambda x: str(x).replace('.',''))
            df = df.applymap(lambda x: str(x).replace(',','.'))
            df.apply(pd.to_numeric,errors='coerse')
            df = df.astype(float,raise_on_error=False)
            ldfs.append(df)
        return pd.concat(ldfs,axis=1)
#            except:
#                print("Fallo descarga para " + self.nombre)
#                sys.exit

        
    def _to_dict_list(self,tablas,tipo,fechas_datetime=True):
        """Retorna una lista de diccionarios. Para cada tabla de la lista 'tablas'"""
        datos=[]
        for i in self.consulta[tipo]['secciones']:
            tabla=tablas[self._ubicar(i,tipo)]
            datos.append(self._to_dict(tabla,fechas_datetime))
        return datos

    def _num_fechas(self,texto):
        """Convierte el formato leido de las fechas a otro formato,
        numerico"""
        conver=[('Ene','01'),('Feb','02'),('Mar','03'),
                ('Abr','04'),('May','05'),('Jun','06'),
                ('Jul','07'),('Ago','08'),('Set','09'),
                ('Oct','10'),('Nov','11'),('Dic','12')]
        for duo in conver:
            if duo[0] in texto:
                return texto.replace(duo[0],duo[1])
        return texto

    def _inv_fechas(self,texto):
        """Invierte el orden de las fechas"""
        if len(texto)==7:
            ntexto = str(texto[3:7])+str(texto[2])+str(texto[0:2])
            #print(texto)
            #print(ntexto+'\n')
            return ntexto
        else:
            return texto

    def _dt_fechas(self,listado,fechas_datetime=True):
        if fechas_datetime:
            nlist=[dt.strptime(self._num_fechas(i),"%m-%Y") for i in listado]
        else:
            nlist=[self._inv_fechas(self._num_fechas(i)) for i in listado]
        return nlist

    def _to_dict(self,tabla,fechas_datetime=True):
        """Convierte tabla html a dict"""
        head=tabla[0][0]
        tabla[0][0]='fecha'
        tabla_dict={}
        for i in tabla:
            tabla_dict[str(" ".join(i[0].split()))]=list(i[1:])
        #tabla_dict['fecha']=tabla_dict.pop('fecha')
        tabla_dict['fecha']=self._dt_fechas(tabla_dict['fecha'],fechas_datetime)
        return tabla_dict

    def _ubicar(self,texto,tipo):
        num = self.consulta[tipo]['secciones'].index(texto)
        return self.consulta[tipo]['orden'][num]

    def _obtener_tablas(self,soup):
        """A partir de un Objeto de BeautifulSoup, devuelve una lista
        con todas las tablas html del objeto"""
        tablas = soup.findAll("table")
        body = []
        for table in tablas:
            body.append([[td.text.replace('\n','').replace('\xa0','').replace('\r','').replace('\t','').strip() for td in row.select('td')]
                     for row in table.findAll('tr')])
        return body
    
    def _obtener_html(self,url):
        """A partir de una url, devuelve un objeto de BeautifulSoup de la web"""
        raw_page = urllib.request.urlopen(url)
        soup = BeautifulSoup(raw_page, "lxml")
        return soup






