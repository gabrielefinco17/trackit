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
