# Backend – Trenitalia API Proxy

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Il server gira su **http://localhost:8000**.
Documentazione interattiva: http://localhost:8000/docs

## Endpoint

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/searchstat/{city}` | Autocompletamento stazioni |
| GET | `/traininfo/{train_id}` | Info base treno |
| GET | `/trainautocomplete/{train_id}` | Stazione di partenza da numero treno |
| GET | `/andamentotreno/{station_id}/{train_id}/{ts}` | Percorso completo con ritardi |
| GET | `/partenze/{station_id}/{datetime}` | Treni in partenza |
| GET | `/arrivi/{station_id}/{datetime}` | Treni in arrivo |
| GET | `/news` | News in tempo reale |
| GET | `/statistiche` | Treni circolanti ora |
| GET | `/meteo/{station_id}` | Meteo stazione |
| GET | `/language/{lang}` | Cambio lingua (it/en) |
