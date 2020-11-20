from bcra_scrapper import BCRA
from matplotlib import cm
import pandas as pd


def comparar_columna(datos,columna,tipo=None, unidad=None):
    """Compara una misma columna de datos para diferentes bancos.
    Devuelve un dataframe con la comparacion.
    tipo:indicadores, estructura, balance"""
    if tipo is None:
        tipo='indicadores'
    if unidad is None:
        unidad = 1

    comp=[]
    cols=[]
    for key, val in datos.items():
        try:
            comp.append(datos[key][tipo][columna])
            cols.append(key)
        except:
            print("WARN: No se encontró la columna '"+str(columna)+"' en '"+str(tipo)+"' de '" + str(key)+"'")
    #nombre=datos[key][tipo].iloc[:,col].name
    df=pd.concat(comp,axis=1)
    df.columns = cols
    df.apply(pd.to_numeric,errors='coerce')
    return columna,df.astype(float,raise_on_error=False)/unidad


def obtener_datos(lista=None,dtfmt=False):
    """Busca en la web de BCRA los datos de bancos. Los bancos 
    cuyos datos se requieren se ingresan a traves de una lista de siglas.
    Por defecto baja todo. Si dtfmt es verdadero, las fechas son convertidas
    a objetos datetime"""
    if lista is None:
        #lista=['bma','fran','bpat','brio','gali']
        lista=['Macro','Frances','RIO','Galicia', 'Patagonia', 'Supervielle', 'Hipotecario', 'Citibank', 'HSBC', \
               'Comafi', 'Columbia','Credicoop','ICBC']
        
    banco = {}
    for name in lista:
        banco[name]= BCRA(name,dtfmt).datos
    return banco

def graficar_comp(comp,save=False,tipo=None,xlim=None,ylim=None,anchor=None,title=None):
    if tipo is None:
        tipo='indicadores'
    if anchor is None:
        anchor=(0.77,1.02)
#    nom, col = comparar_columna(datos,col,tipo)
#    if title is None:
#        title=nom
    ax=comp.plot(kind='bar',title=title,figsize=(14,7),xlim=xlim,ylim=ylim,colormap=cm.nipy_spectral).legend(loc='upper center', 
            bbox_to_anchor=anchor,ncol=3, fancybox=True, shadow=True)
    if save:
        fig = ax.get_figure()
        fig.savefig(save)
