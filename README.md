# COVID19Feed2Json
Python API returning Italian Civil Protection Department and Ministry of Health <a href="https://github.com/pcm-dpc/COVID-19" target="_blank">official COVID19 data in Italy</a>.

## API END POINTS

#### https://covid19-it-api.herokuapp.com/
API doc

#### https://covid19-it-api.herokuapp.com/info
Return **JSON** info about the project

#### https://covid19-it-api.herokuapp.com/andamento
Return **JSON** daily data about infection spread.<br/>
Optional parameter:
- data (*type: String*, *example: 2020-02-25 18:00*)

#### https://covid19-it-api.herokuapp.com/regioni
Return **GeoJSON** daily data about Regional cases distribution.<br/>
Optional parameter:
- data (*type: String*, *example: 2020-02-25 18:00*)

#### https://covid19-it-api.herokuapp.com/province
Return **GeoJSON** data about Province level cases distribution.<br/> 
Optional parameter:
- data (*type: String*, *example: 2020-02-25 18:00*)

## Data Source
All information comes from <a target="_blank" href="http://www.protezionecivile.gov.it/">Sito del Dipartimento della Protezione Civile - Presidenza del Consiglio dei Ministri</a>

## Real life example
A Dashboard application showing the exposed data can be tested <a href="https://alessiodl.github.io/COVID19Dashboard/dist/index.html" target="_blank">here</a>

## Thanks...
...to my friends <a href="https://github.com/aborruso" target="_blank">Andrea Borruso</a> for his precious suggestions and encouragement, <a href="https://www.linkedin.com/in/pietroblu" target="_blank">Pietro Blu Giandonato</a> for the proposal and data collection in progress about hospitals and <a href="https://www.linkedin.com/in/susannatora/?originalSubdomain=it" target="_blank">Susanna Tora</a> for the integration of the population information in the underlying geographic datasets.
