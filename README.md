datalab
==============================

Exploración y visualización de datos de la convocatoria de Datalab

# Bienvenido a mi proceso de Datalab
Mi solución tiene 3 componentes:

1. Limpieza de Datos - Descrita en este repositorio.
2. Una API que expone la respuesta de "Lugares cercanos" almacenada en https://github.com/ricalanis/datalab-api  y publicada en http://datalabapi.herokuapp.com
3. Una pequeña aplicación almacenada en https://github.com/ricalanis/datalab-app y publicada en: http://104.196.40.88/


## Limpieza de Datos.
El proceso se centró en descargar y limpiar las columnas de manera manual.
Este proceso está detallado en esta libreta: 
https://github.com/ricalanis/datalab/blob/master/notebooks/1-0.1-rdat-exploracionexcel-LimpiezaDatos.ipynb
El proceso de limpieza automatizado está embebido al Makefile de esta carpeta que referencia [datalab/src/data at master · ricalanis/datalab · GitHub](https://github.com/ricalanis/datalab/tree/master/src/data)
Al final de este proceso, se almacenan los datos en mlab.com
En esta carpeta, el histograma de observaciones de coordenadas de longitud y de latitud: https://github.com/ricalanis/datalab/blob/master/reports/figures/

## API de datos.
La consulta de la cercanía se apoyó en dos herramientas:
- Consultas geo de MongoDB
- API de Google Maps de translados
La api expone un solo endpoint:
get_near_points, con los parameters:
- longitude
- latitude
- mode: Puede tomar el valuar de "euclidean", "walking", "driving". Las direcciones de walking y driving son tomadas de la API de google apps.
- head: Numero de celdas a mostrar. Para este caso, 3.

Un ejemplo de una llamada:
http://datalabapi.herokuapp.com/get_near_points?longitude=-104.45126666666668&latitude=21.034533333333336&mode=walking&head=3

## MVP de Visualización
Se utilizó un template de AngularJS para generar un mapa dinámico que consume la información expuesta en la API.
http://104.196.40.88/
Al dar click en cualquier parte del mapa se generan rutas: Cada solicitud hecha a la API se puede verificar en la consola del explorador.
