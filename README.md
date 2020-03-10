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

## Source
All information comes from <a target="_blank" href="http://www.protezionecivile.gov.it/">Sito del Dipartimento della Protezione Civile - Presidenza del Consiglio dei Ministri</a>

## Thanks...
...to my friend <a href="https://github.com/aborruso">Andrea Borruso</a> for his precious suggestions and encouragement
