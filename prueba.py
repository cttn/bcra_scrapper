import pandas as pd
def _list_dfs(lista):
    ldfs = []
    for i in lista:
        df = pd.DataFrame.from_dict(i)
        df.index=i['fecha']
        df.drop('fecha',1,inplace=True)
        #df.drop('',axis=1,inplace=True)
        df.index.name='fecha'
        df = df.applymap(lambda x: str(x).replace('.',''))
        df = df.applymap(lambda x: str(x).replace(',','.'))
        df.apply(pd.to_numeric,errors='coerse')
        df = df.astype(float,raise_on_error=False)
        ldfs.append(df)
    return pd.concat(ldfs,axis=1)

