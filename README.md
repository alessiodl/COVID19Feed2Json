# COVID19Feed2Json
Python API returning Italian Civil Protection Department and Ministry of Health official COVID19 data in Italy. It is based on daily web scraping activity.

## API END POINTS

#### https://covid19-it-api.herokuapp.com/info
Returns **JSON** info about the project

#### https://covid19-it-api.herokuapp.com/summary
Returns **JSON** daily data about total infected people, positive, deads, recovered.<br/>
Optional parameter:
- data (*type: String*, *example: 2020-02-25 18:00*)

#### https://covid19-it-api.herokuapp.com/state
Returns **JSON** daily data about the sanitary state of infected people.<br/>
Optional parameter:
- data (*type: String*, *example: 2020-02-25 18:00*)

#### https://covid19-it-api.herokuapp.com/distribution/regions
Returns **GeoJSON** daily data about the outbreaks in each Region.<br/>
Optional parameter:
- data (*type: String*, *example: 2020-02-25 18:00*)

#### https://covid19-it-api.herokuapp.com/distribution/regions/last
Returns **GeoJSON** data about the last updated outbreaks in each Region.<br/> 
Optional parameter:
- data (*type: String*, *example: 2020-02-25 18:00*)

#### https://covid19-it-api.herokuapp.com/distribution/regions/overview
Returns more complete **GeoJSON** data about the last updated outbreaks in each Region.<br/> 
Optional parameter:
- data (*type: String*, *example: 2020-02-25 18:00*)

## Source
All information comes from <a target="_blank" href="http://www.protezionecivile.gov.it/">Sito del Dipartimento della Protezione Civile - Presidenza del Consiglio dei Ministri</a>

## Thanks...
...to my friend <a href="https://github.com/aborruso">Andrea Borruso</a> for his precious suggestions and encouragement
