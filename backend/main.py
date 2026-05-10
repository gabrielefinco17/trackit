import requests
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trenitalia API Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = "http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno"


def vt_get(path: str):
    try:
        r = requests.get(f"{BASE}/{path}", timeout=10)
        r.raise_for_status()
        # ViaggaTreno sometimes returns plain text
        try:
            return r.json()
        except Exception:
            return r.text
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── STAZIONI ────────────────────────────────────────────────────────────────

@app.get("/searchstat/{city_name}")
def search_stat(city_name: str):
    """Cerca stazioni per nome città (autocompletamento)."""
    return vt_get(f"cercaStazione/{city_name}")


# ── TRENO ────────────────────────────────────────────────────────────────────

@app.get("/traininfo/{train_id}")
def train_info(train_id: str):
    """Info base su un treno dato il numero."""
    return vt_get(f"cercaNumeroTreno/{train_id}")


@app.get("/trainautocomplete/{train_id}")
def train_autocomplete(train_id: str):
    """Autocomplete numero treno → restituisce stazione di partenza."""
    return vt_get(f"cercaNumeroTrenoTrenoAutocomplete/{train_id}")


@app.get("/andamentotreno/{station_id}/{train_id}/{timestamp}")
def andamento_treno(station_id: str, train_id: str, timestamp: int):
    """Percorso completo con fermate, orari e ritardi."""
    return vt_get(f"andamentoTreno/{station_id}/{train_id}/{timestamp}")


# ── PARTENZE / ARRIVI ────────────────────────────────────────────────────────

@app.get("/partenze/{station_id}/{datetime_str}")
def partenze(station_id: str, datetime_str: str):
    """Treni in partenza da una stazione (datetime: 'Mon Dec 09 2024 14:00:00')."""
    return vt_get(f"partenze/{station_id}/{datetime_str}")


@app.get("/arrivi/{station_id}/{datetime_str}")
def arrivi(station_id: str, datetime_str: str):
    """Treni in arrivo a una stazione."""
    return vt_get(f"arrivi/{station_id}/{datetime_str}")


# ── EXTRAS ───────────────────────────────────────────────────────────────────

@app.get("/news")
def news():
    """News in tempo reale da Trenitalia."""
    return vt_get("news/0/it")


@app.get("/statistiche")
def statistiche():
    """Contatore treni circolanti in tempo reale."""
    ts = int(time.time() * 1000)
    return vt_get(f"statistiche/{ts}")


@app.get("/meteo/{station_id}")
def meteo(station_id: str):
    """Meteo per stazione tramite endpoint Trenitalia."""
    return vt_get(f"datimeteo/{station_id}")


@app.get("/language/{lang}")
def language(lang: str):
    """Cambia lingua (it/en)."""
    return vt_get(f"language/{lang}")


@app.get("/dettaglioStazione/{station_id}/{train_number}")
def dettaglio_stazione(station_id: str, train_number: str):
    """Dettaglio fermata di un treno in una stazione."""
    return vt_get(f"dettaglioStazione/{station_id}/{train_number}")
