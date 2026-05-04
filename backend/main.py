import requests
from fastapi import FastAPI

app = FastAPI()


# SEARCHING STATIONS FOR CITY
@app.get("/searchstat/{city_name}")
def search_stat(city_name: str):
    url = f"http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno/cercaStazione/{city_name}"
    response = requests.get(url)
    return response.json()


@app.get("/traininfo/{train_id}")
def train_info(train_id: str):
    url = f"http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno/cercaNumeroTreno/{train_id}"
    response = requests.get(url)
    return response.json()


#  — visualizzazione dei treni in partenza o in arrivo da una stazione scelta,
#  con: orario previsto, ritardo e stato
#
#  — dato un numero di treno, mostrare il suo percorso completo con le
#  fermate, gli orari e l'eventuale ritardo per ciascuna stazione
#
# EXTRAS:
#
# Notifica (anche solo visiva) se un treno ha un ritardo superiore a una soglia configurabile
#
# Sezione con le news in tempo reale (dall'endpoint news/0/it)
#
# Integrazione del meteo tramite l'endpoint datimeteo o API meteo esterna
#
# Trova automaticamente la stazione di partenza da un numero treno (cercaNumeroTrenoTrenoAutocomplete)
#
# Contatore treni circolanti in tempo reale (dall'endpoint statistiche/{timestamp})
#
# Supporto italiano/inglese usando l'endpoint language/{lingua}
#
# Salvataggio in localStorage delle ultime stazioni consultate
