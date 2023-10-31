import pandas as pd
import numpy as np

def whitespace_remover(dataframe):
   
    # iterating over the columns
    for i in dataframe.columns:
         
        # checking datatype of each columns
        if dataframe[i].dtype == 'object':
             
            # applying strip function on column
            dataframe[i] = dataframe[i].map(str.strip)
        else:
             
            # if condn. is False then it will do nothing.
            pass
    return dataframe
def whitespace_remover_and_columns(dataframe):
   
    # iterating over the columns
    for i in dataframe.columns:
         
        # checking datatype of each columns
        if dataframe[i].dtype == 'object':
             
            # applying strip function on column
            dataframe[i] = dataframe[i].map(str.strip)
        else:
             
            # if condn. is False then it will do nothing.
            pass
    dataframe.rename(columns=lambda x: x.strip(), inplace=True)
    return dataframe




def transformar_columnas_datetime(df):
    for col in df.columns[3:]:
        if df[col].dtype == 'object':
            df[col] = pd.to_datetime(df[col])
    return df


"""
def transformar_columnas_datetime(df):
    for columna in df.columns:
        try:
            df[columna] = pd.to_datetime(df[columna])
        except ValueError:
            pass
    return df
"""


def tiempo_de_espera(orders, is_delivered=True):
    if is_delivered:
        orders = orders.query("order_status=='delivered'").copy()
    orders.loc[:, 'tiempo_de_espera'] = \
        (orders['order_delivered_customer_date'] -
         orders['order_purchase_timestamp']) / np.timedelta64(24, 'h')
    return orders

def tiempo_de_espera_previsto(orders, is_delivered=True):
    if is_delivered:
        orders = orders.query("order_status=='delivered'").copy()
    orders.loc[:, 'tiempo_de_espera_previsto'] = \
        (orders['order_estimated_delivery_date'] -
         orders['order_purchase_timestamp']) / np.timedelta64(24, 'h')
    return orders

#si la fecha de entrega real es posterior a la fecha de entrega estimada, devuelve el número de días entre las dos fechas; de lo contrario, devuelve 0
"""def real_vs_esperado(orders, is_delivered=True):
    if is_delivered:
        orders = orders.query("order_status=='delivered'").copy()
        
    if (orders['tiempo_de_espera']-orders['tiempo_de_espera_previsto'])>0:
            orders['real_vs_esperado'] = orders['tiempo_de_espera']-orders['tiempo_de_espera_previsto']
    else:
            orders['real_vs_esperado'] = 0
    return orders
"""
import numpy as np
def real_vs_esperado(orders, is_delivered=True):
    if is_delivered:
        orders = orders.query("order_status=='delivered'").copy()
        
    orders['real_vs_esperado'] = np.where(orders['tiempo_de_espera'] > orders['tiempo_de_espera_previsto'], 
                                           orders['tiempo_de_espera'] - orders['tiempo_de_espera_previsto'], 
                                           0)
    return orders

def puntaje_de_compra(df):
    def es_cinco_estrella(x):
        if x == 5:
            return 1
        else:
            return 0 
    df['es_cinco_estrellas'] = df['review_score'].apply(es_cinco_estrella)
    
    def es_una_estrella(x):
        if x == 1:
            return 1 
        else:
            return 0
    df['es_una_estrella'] = df['review_score'].apply(es_una_estrella)
    
    return df[['order_id','es_cinco_estrellas', 'es_una_estrella', 'review_score']]

def calcular_numero_productos(df):
    df1 = df.copy()
    order_items_df = df1['order_items'].copy()
    order_items_df = whitespace_remover(order_items_df)
    order_items_df.rename(columns=lambda x: x.strip(), inplace=True)
    return order_items_df.groupby('order_id').agg(num_de_produc = ('product_id','count')).reset_index()

def vendedores_unicos(df):
    df2 = df.copy()
    oitp4 = df2['order_items'].copy()
    oitp4 = whitespace_remover(oitp4)
    oitp4.rename(columns=lambda x: x.strip(), inplace=True)
    return oitp4.groupby('order_id').agg(vendedores_unicos = ('seller_id','nunique')).reset_index()

def calcular_precio_y_transporte(df):
    df2=df.copy()
    order_items_df2 = df2['order_items'].copy()
    order_items_df2 = whitespace_remover(order_items_df2)
    order_items_df2.rename(columns=lambda x: x.strip(), inplace=True)
    return order_items_df2.groupby('order_id').agg(precio = ('price','sum'), transporte=('freight_value','sum')).reset_index()



#Distancia entre cliente y vendedor en km 
# geolocation_lat_x	geolocation_lng_x comprador
# geolocation_lat_y	geolocation_lng_y vendedor

from math import radians, sin, cos, asin, sqrt
def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Computa distancia entre dos pares (lat, lng)
    Ver - (https://en.wikipedia.org/wiki/Haversine_formula)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


def calculate_distance(row):
    return haversine_distance(row['geolocation_lng_x'], row['geolocation_lat_x'], row['geolocation_lng_y'], row['geolocation_lat_y'])


def crear_columna(df):
    df2=df.copy()
    df2['distancia_entre_cliente_y_vendedor'] = df2.apply(calculate_distance, axis=1)
    return df2[['order_id', 'distancia_entre_cliente_y_vendedor']]
