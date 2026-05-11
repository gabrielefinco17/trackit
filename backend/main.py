import threading
import time
from functools import lru_cache
from typing import List

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Trenitalia API Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = "http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno"

# ── NOMINATIM RATE-LIMIT TRACKER (thread-safe) ──────────────────────────────
_nominatim_last_call: float = 0.0
_nominatim_lock = threading.Lock()


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


# ── GEOCODING ────────────────────────────────────────────────────────────────

# Built-in cache of common Italian train station coordinates.
# This avoids hitting Nominatim for the most frequent stations.
_STATION_COORDS: dict[str, dict] = {
    "TORINO PORTA NUOVA": {"lat": 45.0617, "lon": 7.6781},
    "TORINO PORTA SUSA": {"lat": 45.0722, "lon": 7.6667},
    "TORINO LINGOTTO": {"lat": 45.0431, "lon": 7.6536},
    "MILANO CENTRALE": {"lat": 45.4861, "lon": 9.2044},
    "MILANO PORTA GARIBALDI": {"lat": 45.4847, "lon": 9.1878},
    "MILANO ROGOREDO": {"lat": 45.4333, "lon": 9.2381},
    "MILANO LAMBRATE": {"lat": 45.4856, "lon": 9.2358},
    "MILANO CADORNA": {"lat": 45.4689, "lon": 9.1742},
    "VENEZIA SANTA LUCIA": {"lat": 45.4414, "lon": 12.3208},
    "VENEZIA MESTRE": {"lat": 45.4822, "lon": 12.2306},
    "VERONA PORTA NUOVA": {"lat": 45.4286, "lon": 10.9828},
    "PADOVA": {"lat": 45.4175, "lon": 11.8803},
    "VICENZA": {"lat": 45.5478, "lon": 11.5453},
    "TREVISO CENTRALE": {"lat": 45.6603, "lon": 12.2417},
    "TRIESTE CENTRALE": {"lat": 45.6567, "lon": 13.7689},
    "UDINE": {"lat": 46.0569, "lon": 13.2406},
    "BOLOGNA CENTRALE": {"lat": 44.5058, "lon": 11.3428},
    "BOLOGNA C.LE/AV": {"lat": 44.5058, "lon": 11.3428},
    "FIRENZE SANTA MARIA NOVELLA": {"lat": 43.7764, "lon": 11.2481},
    "FIRENZE CAMPO DI MARTE": {"lat": 43.7842, "lon": 11.2733},
    "FIRENZE RIFREDI": {"lat": 43.7925, "lon": 11.2392},
    "PRATO CENTRALE": {"lat": 43.8797, "lon": 11.0972},
    "PISA CENTRALE": {"lat": 43.7100, "lon": 10.3994},
    "LIVORNO CENTRALE": {"lat": 43.5522, "lon": 10.3089},
    "ROMA TERMINI": {"lat": 41.9011, "lon": 12.5019},
    "ROMA TIBURTINA": {"lat": 41.9106, "lon": 12.5292},
    "ROMA OSTIENSE": {"lat": 41.8719, "lon": 12.4856},
    "ROMA TRASTEVERE": {"lat": 41.8725, "lon": 12.4658},
    "ROMA TUSCOLANA": {"lat": 41.8822, "lon": 12.5178},
    "NAPOLI CENTRALE": {"lat": 40.8531, "lon": 14.2722},
    "NAPOLI AFRAGOLA": {"lat": 40.9233, "lon": 14.3381},
    "NAPOLI PIAZZA GARIBALDI": {"lat": 40.8531, "lon": 14.2722},
    "SALERNO": {"lat": 40.6744, "lon": 14.7711},
    "CASERTA": {"lat": 41.0789, "lon": 14.3331},
    "BARI CENTRALE": {"lat": 41.1178, "lon": 16.8711},
    "BRINDISI": {"lat": 40.6269, "lon": 17.9422},
    "LECCE": {"lat": 40.3531, "lon": 18.1692},
    "TARANTO": {"lat": 40.4647, "lon": 17.2372},
    "FOGGIA": {"lat": 41.4619, "lon": 15.5408},
    "REGGIO CALABRIA CENTRALE": {"lat": 38.1050, "lon": 15.6369},
    "CATANZARO LIDO": {"lat": 38.8375, "lon": 16.5925},
    "COSENZA": {"lat": 39.2994, "lon": 16.2500},
    "PALERMO CENTRALE": {"lat": 38.1083, "lon": 13.3628},
    "CATANIA CENTRALE": {"lat": 37.5072, "lon": 15.0997},
    "MESSINA CENTRALE": {"lat": 38.1892, "lon": 15.5572},
    "SIRACUSA": {"lat": 37.0747, "lon": 15.2800},
    "CAGLIARI": {"lat": 39.2158, "lon": 9.1131},
    "SASSARI": {"lat": 40.7261, "lon": 8.5622},
    "GENOVA PIAZZA PRINCIPE": {"lat": 44.4144, "lon": 8.9206},
    "GENOVA BRIGNOLE": {"lat": 44.4072, "lon": 8.9453},
    "LA SPEZIA CENTRALE": {"lat": 44.1025, "lon": 9.8267},
    "PERUGIA": {"lat": 43.0986, "lon": 12.3931},
    "ANCONA": {"lat": 43.6072, "lon": 13.5050},
    "PESCARA CENTRALE": {"lat": 42.4617, "lon": 14.2058},
    "L'AQUILA": {"lat": 42.3533, "lon": 13.3958},
    "CAMPOBASSO": {"lat": 41.5608, "lon": 14.6728},
    "POTENZA CENTRALE": {"lat": 40.6383, "lon": 15.8064},
    "TRENTO": {"lat": 46.0719, "lon": 11.1192},
    "BOLZANO/BOZEN": {"lat": 46.4972, "lon": 11.3575},
    "AOSTA": {"lat": 45.7350, "lon": 7.3233},
    "REGGIO EMILIA AV MEDIOPADANA": {"lat": 44.7197, "lon": 10.6567},
    "REGGIO EMILIA": {"lat": 44.6986, "lon": 10.6311},
    "MODENA": {"lat": 44.6444, "lon": 10.9167},
    "PARMA": {"lat": 44.8017, "lon": 10.3317},
    "PIACENZA": {"lat": 45.0486, "lon": 9.7053},
    "RAVENNA": {"lat": 44.4175, "lon": 12.2044},
    "RIMINI": {"lat": 44.0603, "lon": 12.5694},
    "FERRARA": {"lat": 44.8431, "lon": 11.6022},
    "CESENA": {"lat": 44.1428, "lon": 12.2406},
    "FORLÌ": {"lat": 44.2231, "lon": 12.0531},
    "BRESCIA": {"lat": 45.5328, "lon": 10.2128},
    "BERGAMO": {"lat": 45.6900, "lon": 9.6781},
    "COMO SAN GIOVANNI": {"lat": 45.8081, "lon": 9.0839},
    "MANTOVA": {"lat": 45.1614, "lon": 10.7964},
    "CREMONA": {"lat": 45.1372, "lon": 10.0228},
    "MONZA": {"lat": 45.5822, "lon": 9.2742},
    "FALCONARA MARITTIMA": {"lat": 43.6244, "lon": 13.3986},
    "FABRIANO": {"lat": 43.3333, "lon": 12.9050},
    "JESI": {"lat": 43.5236, "lon": 13.2444},
    "FOLIGNO": {"lat": 42.9489, "lon": 12.7133},
    "SPOLETO": {"lat": 42.7319, "lon": 12.7375},
    "TERNI": {"lat": 42.5614, "lon": 12.6431},
    "FOSSATO DI VICO GUBBIO": {"lat": 43.2942, "lon": 12.7622},
    "AREZZO": {"lat": 43.4619, "lon": 11.8806},
    "SIENA": {"lat": 43.3228, "lon": 11.3258},
    "GROSSETO": {"lat": 42.7714, "lon": 11.1097},
    "CIVITAVECCHIA": {"lat": 42.0925, "lon": 11.7961},
    "LATINA": {"lat": 41.4683, "lon": 12.9053},
    "FROSINONE": {"lat": 41.6439, "lon": 13.3575},
    "VITERBO PORTA ROMANA": {"lat": 42.4108, "lon": 12.1056},
    "ORVIETO": {"lat": 42.7192, "lon": 12.1089},
    "TIVOLI": {"lat": 41.9631, "lon": 12.7972},
    "FORMIA": {"lat": 41.2536, "lon": 13.6078},
    "BENEVENTO": {"lat": 41.1292, "lon": 14.7808},
    "AVELLINO": {"lat": 40.9144, "lon": 14.7897},
    "BATTIPAGLIA": {"lat": 40.6069, "lon": 14.9856},
    "SAPRI": {"lat": 40.0739, "lon": 15.6267},
    "LAMEZIA TERME CENTRALE": {"lat": 38.9636, "lon": 16.3081},
    "VILLA SAN GIOVANNI": {"lat": 38.2175, "lon": 15.6369},
    "CROTONE": {"lat": 39.0886, "lon": 17.1247},
    "AGRIGENTO CENTRALE": {"lat": 37.3172, "lon": 13.5886},
    "TRAPANI": {"lat": 38.0183, "lon": 12.5150},
    "RAGUSA": {"lat": 36.9236, "lon": 14.7208},
    "ENNA": {"lat": 37.5647, "lon": 14.2783},
    "CALTANISSETTA CENTRALE": {"lat": 37.4886, "lon": 14.0631},
    "OLBIA": {"lat": 40.9247, "lon": 9.5014},
    "NUORO": {"lat": 40.3211, "lon": 9.3317},
    "ORISTANO": {"lat": 39.9019, "lon": 8.5922},
    "NOVARA": {"lat": 45.4431, "lon": 8.6169},
    "ALESSANDRIA": {"lat": 44.9094, "lon": 8.6128},
    "ASTI": {"lat": 44.8992, "lon": 8.2050},
    "CUNEO": {"lat": 44.3878, "lon": 7.5369},
    "VERCELLI": {"lat": 45.3219, "lon": 8.4228},
    "SAVONA": {"lat": 44.3094, "lon": 8.4903},
    "IMPERIA": {"lat": 43.8869, "lon": 8.0397},
    "SANREMO": {"lat": 43.8158, "lon": 7.7769},
    "VENTIMIGLIA": {"lat": 43.7908, "lon": 7.6072},
}


def _normalize_station_name(name: str) -> str:
    """Normalize station name for cache lookup."""
    return name.strip().upper()


@lru_cache(maxsize=512)
def _geocode_nominatim(station_name: str) -> dict | None:
    """
    Risolve il nome di una stazione in coordinate lat/lon tramite Nominatim.
    Thread-safe with proper serialization via _nominatim_lock.
    """
    global _nominatim_last_call

    with _nominatim_lock:
        # Throttle: wait until at least 1.1s have passed since last call
        elapsed = time.time() - _nominatim_last_call
        if elapsed < 1.1:
            time.sleep(1.1 - elapsed)

        try:
            r = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": f"{station_name} stazione ferroviaria italia",
                    "format": "json",
                    "limit": 1,
                },
                headers={"User-Agent": "TrackIt/1.0"},
                timeout=10,
            )
            _nominatim_last_call = time.time()
            r.raise_for_status()
            results = r.json()
            if results:
                return {
                    "lat": float(results[0]["lat"]),
                    "lon": float(results[0]["lon"]),
                }
            return None
        except Exception:
            _nominatim_last_call = time.time()
            return None


def _geocode_station(station_name: str) -> dict | None:
    """
    Resolve a station name to coordinates.
    First checks the built-in cache, then falls back to Nominatim.
    """
    normalized = _normalize_station_name(station_name)

    # Check built-in cache first
    if normalized in _STATION_COORDS:
        return _STATION_COORDS[normalized]

    # Fallback to Nominatim
    return _geocode_nominatim(normalized)


@app.get("/geocode/{station_name}")
def geocode(station_name: str):
    """
    Risolve il nome di una stazione in coordinate geografiche (lat/lon).
    Returns null (200) if the station cannot be geocoded.
    """
    return _geocode_station(station_name)


class BatchGeocodeRequest(BaseModel):
    stations: List[str]


@app.post("/geocode/batch")
def geocode_batch(req: BatchGeocodeRequest):
    """
    Batch geocode: accepts a list of station names, returns a dict of
    {station_name: {lat, lon} | null} for each.
    """
    results = {}
    for name in req.stations:
        results[name] = _geocode_station(name)
    return results
