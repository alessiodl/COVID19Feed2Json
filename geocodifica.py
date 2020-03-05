def geocodeRegione(regione):
    reg = regione.strip()
    coordinates = ""
    if reg == 'Lombardia':
        coordinates = [9.227828979492188,45.57463894211682]
    elif reg == 'Veneto':
        coordinates = [11.854319842000052,45.65492501300008]
    elif reg == 'Emilia-Romagna':
        coordinates = [11.039213647000054,44.52591084900007]
    elif reg == 'Liguria':
        coordinates = [9.427370000000053,44.415350258000046]
    elif reg == 'Sicilia':
        coordinates = [14.000000000000057,37.50000000000006]
    elif reg == 'Marche':
        coordinates = [13.137824067000054,43.34820017700008]
    elif reg == 'Lazio':
        coordinates = [12.772626321000075,41.97568188900004]
    elif reg == 'Campania':
        coordinates = [14.840115810000043,40.85973483500004]
    elif reg == 'Piemonte':
        coordinates = [7.92049247500006,45.05730108000006]
    elif reg == 'Toscana':
        coordinates = [11.126187689000062,43.45082948600003]
    elif reg == 'Abruzzo':
        coordinates = [13.855048784000076,42.22755568500003]
    elif reg == 'Puglia':
        coordinates = [16.618785484000057,40.98504106300004]
    elif reg == 'Molise':
        coordinates = [14.6337890625,41.6154423246811]
    elif reg == 'Basilicata':
        coordinates = [16.083984375,40.51379915504413]
    elif reg == 'Umbria':
        coordinates = [12.436523437499998,43.13306116240612]
    elif reg == 'Sardegna':
        coordinates = [9.0128926,40.1208752]
    elif reg == 'Friuli Venezia Giulia':
        coordinates = [12.5594548,46.1129993]
    elif reg == 'Provincia autonoma di Trento':
        coordinates = [10.6469911,46.1015475]
    elif reg == 'Calabria':
        coordinates = [16.446533203125,38.976492485539396]
    elif reg == "Valle d'Aosta":
        coordinates = [6.8099952,45.7259823]
    elif reg == 'Provincia autonoma di Bolzano':
        coordinates = [11.37359619140625,46.538082005463075]
    else:
        # punto in mezzo al mare adriatico 
        # serve per evidenziare un problema col nome di una regione
        # nel parser
        coordinates = [15.479736328125,42.83569550641452]

    return coordinates
