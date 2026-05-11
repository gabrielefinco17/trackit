# TrackIt — Documentazione del Progetto

**Progetto:** TrackIt  
**Autori:** Yuri Bressanello, Gabriele Finco  
**Data:** Maggio 2026  

---

## 1. Descrizione Generale

**TrackIt** è un'applicazione web moderna per il monitoraggio in tempo reale dei treni italiani. Si interfaccia con le API non documentate di Trenitalia (ViaggiaTreno) tramite un backend proxy, offrendo agli utenti un'interfaccia minimalista e tipografica in bianco e nero per consultare partenze, arrivi, percorsi, ritardi e notizie sul traffico ferroviario italiano.

### Caratteristiche principali

- Monitoraggio in tempo reale di partenze e arrivi da qualsiasi stazione italiana
- Visualizzazione del percorso completo di un treno con fermate, orari previsti/effettivi e ritardi
- Mappa interattiva del percorso del treno (via Leaflet.js)
- Motore di ricerca con autocompletamento per stazioni e numeri treno
- Supporto multilingua (Italiano / Inglese) senza ricaricamento della pagina
- Notizie e avvisi in tempo reale sul traffico ferroviario
- Statistiche live: treni circolanti e treni del giorno
- Design stark minimalista: monocromatico bianco e nero, orientato alla tipografia

---

## 2. Architettura del Software

TrackIt segue un'architettura **Client-Server** a due livelli, con una netta separazione tra frontend e backend.

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER UTENTE                        │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              FRONTEND (index.html)                  │   │
│   │  HTML5 · CSS3 · JavaScript ES6+ · Leaflet.js        │   │
│   └───────────────────────┬─────────────────────────────┘   │
│                           │ HTTP fetch()                     │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI · Python)                      │
│                   localhost:8000                             │
│                                                             │
│   ┌──────────────┐   ┌──────────────┐   ┌───────────────┐  │
│   │  Proxy VT    │   │  Geocoding   │   │  CORS         │  │
│   │  Endpoints   │   │  Engine      │   │  Middleware   │  │
│   └──────┬───────┘   └──────┬───────┘   └───────────────┘  │
│          │                  │                               │
└──────────┼──────────────────┼───────────────────────────────┘
           │                  │
           ▼                  ▼
┌──────────────────┐  ┌───────────────────────┐
│  ViaggiaTreno    │  │  Nominatim (OSM)       │
│  API Trenitalia  │  │  (fallback geocoding)  │
└──────────────────┘  └───────────────────────┘
```

### 2.1 Frontend

Il frontend è contenuto interamente nel file `frontend/index.html` ed è una Single-Page Application (SPA) vanilla, senza dipendenze da framework (React, Vue, Angular, ecc.).

**Tecnologie utilizzate:**
- HTML5 / CSS3 con variabili native, CSS Grid e media query
- JavaScript ES6+ (async/await, fetch API, moduli ES)
- Leaflet.js per la visualizzazione della mappa interattiva del percorso

**Navigazione:** La SPA gestisce tre sezioni principali, attivabili tramite la barra di navigazione superiore:

| Sezione | ID DOM | Descrizione |
|---------|--------|-------------|
| Stazioni | `sec-stazioni` | Ricerca stazione, board partenze/arrivi, statistiche |
| Treni | `sec-treno` | Ricerca per numero treno, dettaglio percorso |
| News | `sec-news` | Notizie e avvisi Trenitalia in tempo reale |

### 2.2 Backend

Il backend è un server proxy costruito con **FastAPI** (Python), che si occupa di:

1. Ricevere le richieste del frontend
2. Inoltrarle alle API interne di Trenitalia (ViaggiaTreno)
3. Gestire il geocoding delle stazioni (cache statica + fallback Nominatim)
4. Restituire le risposte al frontend con le header CORS appropriate

**Tecnologie utilizzate:**
- Python 3.x
- FastAPI ≥ 0.110.0 (framework HTTP asincrono)
- Uvicorn ≥ 0.29.0 (server ASGI)
- Requests ≥ 2.31.0 (client HTTP per le chiamate a ViaggiaTreno e Nominatim)

---

## 3. Struttura del Progetto

```
trackit/
├── README.md                     # Panoramica generale del progetto
├── backend/
│   ├── main.py                   # Server FastAPI (unico file sorgente)
│   ├── requirements.txt          # Dipendenze Python
│   └── README.md                 # Istruzioni backend
├── frontend/
│   ├── index.html                # Applicazione frontend completa (SPA)
│   └── README.md                 # Istruzioni frontend
└── deploy/
    └── README.md                 # Istruzioni di avvio e deployment
```

---

## 4. Funzionalità Implementate

### 4.1 Ricerca e Selezione Stazione

L'utente digita nella barra di ricerca il nome di una stazione. Il sistema chiama l'endpoint `/searchstat/{city_name}` che interroga l'API `cercaStazione` di ViaggiaTreno e restituisce una lista di autocompletamento. Le stazioni selezionate vengono salvate nella cronologia locale (`localStorage`) per accesso rapido futuro.

**Funzioni JS coinvolte:** `fetchStationAc()`, `renderStationAc()`, `selectStation()`, `saveHistory()`, `renderHistory()`

### 4.2 Board Partenze / Arrivi

Selezionata una stazione, viene caricata la board dei treni. L'utente può alternare tra visualizzazione **Partenze** e **Arrivi** tramite i pulsanti pill. È disponibile un filtro sulla soglia di ritardo per mostrare solo i treni in ritardo oltre N minuti.

**Funzioni JS coinvolte:** `loadBoard()`, `renderBoard()`, `renderRow()`, `toggleDir()`

Ogni riga della board mostra:
- Numero treno e categoria
- Stazione di origine/destinazione
- Orario previsto e orario effettivo
- Ritardo (evidenziato cromaticamente: verde/giallo/rosso)
- Binario di partenza/arrivo
- Stato del treno

### 4.3 Dettaglio Treno (Pannello Laterale)

Cliccando su un treno nella board o cercando per numero, si apre un pannello laterale (`#detail-panel`) con:

- Intestazione: numero treno, origine → destinazione
- Mappa Leaflet interattiva con il percorso geolocalizzato
- Lista completa delle fermate con orari previsti/effettivi e ritardi

**Funzioni JS coinvolte:** `openTrainDetail()`, `loadTrainRoute()`, `renderTrainRoute()`, `buildStopsList()`, `renderStop()`, `initTrainMap()`, `closeDetail()`

### 4.4 Ricerca per Numero Treno

Sezione dedicata alla ricerca diretta di un treno tramite numero. Il sistema usa l'autocompletamento (`/trainautocomplete/{train_id}`) per ottenere la stazione di partenza, necessaria per recuperare il percorso completo.

**Funzioni JS coinvolte:** `fetchTrainAc()`, `selectTrain()`, `searchTrain()`

### 4.5 Mappa Interattiva

La mappa Leaflet viene inizializzata dinamicamente per ogni treno. Il geocoding delle stazioni avviene tramite:

1. **Cache statica in-memory nel backend:** oltre 100 stazioni italiane principali con coordinate pre-calcolate
2. **Fallback su Nominatim (OpenStreetMap):** per stazioni non presenti in cache, con throttling thread-safe (≥1.1 secondi tra chiamate) e `lru_cache(maxsize=512)`
3. **Batch geocoding:** il frontend invia tutte le stazioni del percorso in un'unica richiesta POST a `/geocode/batch` per evitare rate limiting

La mappa disegna una polilinea del percorso e marker colorati per ogni fermata (passata, attuale, futura).

**Funzione JS:** `initTrainMap()`  
**Endpoint backend:** `GET /geocode/{station_name}`, `POST /geocode/batch`

### 4.6 News e Avvisi

La sezione News carica e visualizza le notizie ufficiali di Trenitalia tramite l'endpoint `/news`. Ogni notizia è espandibile per mostrare il corpo completo.

**Funzioni JS coinvolte:** `loadNews()`, `renderNews()`

### 4.7 Statistiche Live

Nella sezione Stazioni è presente una barra di statistiche aggiornata periodicamente che mostra:
- Numero di treni attualmente circolanti
- Totale treni del giorno
- Orario ultimo aggiornamento

**Funzione JS:** `loadStats()`  
**Endpoint backend:** `GET /statistiche`

### 4.8 Internazionalizzazione (i18n)

L'interfaccia supporta italiano e inglese. Il cambio lingua è istantaneo (senza ricaricamento della pagina) e aggiorna tutte le stringhe dell'interfaccia tramite attributi `data-i18n` e `data-i18n-placeholder`.

**Funzioni JS coinvolte:** `setLang()`, `applyTranslations()`, `t(key)`

---

## 5. Descrizione degli Endpoint Backend

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/searchstat/{city_name}` | Autocompletamento stazioni per nome città |
| GET | `/traininfo/{train_id}` | Informazioni base su un treno dato il numero |
| GET | `/trainautocomplete/{train_id}` | Autocompletamento numero treno → stazione di partenza |
| GET | `/andamentotreno/{station_id}/{train_id}/{timestamp}` | Percorso completo con fermate, orari, ritardi |
| GET | `/partenze/{station_id}/{datetime_str}` | Treni in partenza da una stazione |
| GET | `/arrivi/{station_id}/{datetime_str}` | Treni in arrivo a una stazione |
| GET | `/news` | Notizie sul traffico ferroviario |
| GET | `/statistiche` | Contatori treni circolanti e giornalieri |
| GET | `/meteo/{station_id}` | Meteo per stazione |
| GET | `/language/{lang}` | Cambio lingua (it/en) lato ViaggiaTreno |
| GET | `/dettaglioStazione/{station_id}/{train_number}` | Dettaglio fermata di un treno in una stazione |
| GET | `/geocode/{station_name}` | Geocoding singolo stazione → {lat, lon} |
| POST | `/geocode/batch` | Geocoding batch di più stazioni in un'unica richiesta |

Tutti gli endpoint proxy invocano internamente la funzione `vt_get(path)` che gestisce timeout (10s), parsing JSON con fallback a testo semplice, e propagazione degli errori HTTP come `502 Bad Gateway`.

---

## 6. Modulo Geocoding — Dettaglio

Il geocoding è il componente più complesso del backend. La strategia a tre livelli garantisce prestazioni e affidabilità:

```
Richiesta stazione
       │
       ▼
┌──────────────────────────────┐
│  1. Normalizzazione nome     │  strip() + upper()
│     (es. "Roma termini"      │
│      → "ROMA TERMINI")       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  2. Cache statica            │  ~100 stazioni principali
│     _STATION_COORDS dict     │  coordinate pre-calcolate
└──────────────┬───────────────┘
               │ Cache MISS
               ▼
┌──────────────────────────────┐
│  3. Nominatim (OSM)          │  Query: "<nome> stazione
│     _geocode_nominatim()     │   ferroviaria italia"
│     lru_cache(maxsize=512)   │  Throttle: ≥1.1s tra chiamate
│     Thread-safe lock         │  Timeout: 10s
└──────────────┬───────────────┘
               │
               ▼
          {lat, lon} | null
```

In caso di fallimento totale, l'endpoint restituisce `null` con HTTP 200 (invece di 404) per non interrompere il rendering della mappa.

---

## 7. Funzioni JavaScript — Riepilogo

| Funzione | Categoria | Descrizione |
|----------|-----------|-------------|
| `t(key)` | i18n | Restituisce la stringa tradotta per la lingua corrente |
| `applyTranslations()` | i18n | Aggiorna tutti gli elementi DOM con `data-i18n` |
| `setLang(l)` | i18n | Cambia lingua e riapplica le traduzioni |
| `apiFetch(path)` | Rete | Wrapper fetch verso il backend con gestione errori |
| `fmtTime(ts)` | Utilità | Formatta un timestamp in HH:MM |
| `fmtDate(ts)` | Utilità | Formatta un timestamp in data leggibile |
| `delayClass(min)` | Utilità | Restituisce la classe CSS per il livello di ritardo |
| `delayText(min)` | Utilità | Restituisce il testo del ritardo formattato |
| `toast(msg, type)` | UI | Mostra una notifica temporanea |
| `toggleTheme()` | UI | Alterna tema chiaro/scuro |
| `showSection(id)` | Navigazione | Attiva la sezione SPA selezionata |
| `loadStats()` | Statistiche | Carica e aggiorna le statistiche live |
| `fetchStationAc(q)` | Stazioni | Richiede l'autocompletamento stazioni |
| `renderStationAc(list)` | Stazioni | Renderizza i suggerimenti autocomplete |
| `selectStation(id, name)` | Stazioni | Seleziona una stazione e carica la board |
| `saveHistory(id, name)` | Stazioni | Salva la stazione nella cronologia locale |
| `renderHistory()` | Stazioni | Mostra i chip delle stazioni recenti |
| `toggleDir(dir)` | Stazioni | Alterna tra partenze e arrivi |
| `loadBoard()` | Stazioni | Carica i treni per la stazione selezionata |
| `renderBoard(trains)` | Stazioni | Renderizza la tabella dei treni |
| `renderRow(tr, i, isPartenza)` | Stazioni | Renderizza una singola riga treno |
| `fetchTrainAc(q)` | Treni | Autocompletamento numero treno |
| `selectTrain(num)` | Treni | Seleziona un treno dall'autocomplete |
| `searchTrain()` | Treni | Avvia la ricerca per numero treno |
| `openTrainDetail(num, stationId)` | Treni | Apre il pannello dettaglio treno |
| `loadTrainRoute(...)` | Treni | Carica il percorso completo del treno |
| `renderTrainRoute(data, container)` | Treni | Renderizza il percorso nel DOM |
| `closeDetail()` | Treni | Chiude il pannello laterale |
| `buildStopsList(stops)` | Treni | Costruisce la lista delle fermate |
| `toggleStopsList(btn)` | Treni | Espande/collassa la lista fermate |
| `renderStop(s, i, total)` | Treni | Renderizza una singola fermata |
| `initTrainMap(stops, containerId)` | Mappa | Inizializza la mappa Leaflet con il percorso |
| `loadNews()` | News | Carica le notizie Trenitalia |
| `renderNews(n, i)` | News | Renderizza un singolo articolo news |

---

## 8. Test Effettuati

### 8.1 Robustezza API e Geocoding

- **Problema riscontrato:** L'endpoint di geocoding originale restituiva errori HTTP 404 quando una stazione non poteva essere risolta, interrompendo il rendering della mappa.
- **Soluzione implementata:** L'endpoint `/geocode/{station_name}` ora restituisce `null` con HTTP 200 in caso di fallimento, permettendo al frontend di gestire gracefully l'assenza di coordinate.
- **Rate limiting Nominatim:** La funzione `_geocode_nominatim()` è stata resa thread-safe con un lock (`threading.Lock()`) e un throttle minimo di 1.1 secondi tra le chiamate. Questo ha eliminato gli errori HTTP 429 (Too Many Requests) che si verificavano con richieste batch concorrenti.
- **Endpoint batch:** Implementato `POST /geocode/batch` per inviare tutte le stazioni di un percorso in un'unica richiesta, riducendo drasticamente i tempi di caricamento della mappa.

### 8.2 Correttezza dei Dati Frontend

- **Problema riscontrato:** Il campo `binario` (Platform) veniva visualizzato in modo errato, confondendo il binario di partenza con quello di arrivo.
- **Soluzione implementata:** La logica di data mapping è stata corretta per differenziare correttamente il contesto (partenza vs arrivo) al momento del rendering di ogni riga.
- **Gestione risposte null/errore:** Il frontend è stato testato per gestire gracefully risposte null o strutture dati incomplete provenienti dall'API (es. stazioni senza coordinate geocodificate).

### 8.3 Design Responsive

- **Test su mobile (max-width: 700px):** Verificato che il layout CSS Grid collassi correttamente su schermi stretti.
- **Colonne nascoste:** Verificata la corretta visibilità/nascondimento delle colonne della board su formato mobile.
- **Mappa:** Verificato che il componente mappa Leaflet si ridimensioni correttamente nei breakpoint mobile.

### 8.4 Internazionalizzazione

- **Copertura stringhe:** Verificato che tutte le stringhe statiche dell'interfaccia siano presenti nei dizionari `i18n.it` e `i18n.en`.
- **Cambio lingua dinamico:** Verificato che il cambio IT/EN aggiorni correttamente tutti gli elementi DOM (testi, placeholder, attributi aria) senza ricaricare la pagina.
- **Persistenza:** Verificato che la lingua selezionata sia mantenuta durante la sessione.

---

## 9. Istruzioni di Avvio

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Documentazione API interattiva disponibile su: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
python3 -m http.server 3000      # oppure: npx serve .
```

Aprire il browser su: `http://localhost:3000`

> **Nota:** Il frontend **deve** essere servito tramite HTTP server locale (non aperto come `file:///`) per evitare errori CORS nelle chiamate fetch verso il backend.

---

## 10. Note per il Deployment in Produzione

Prima di deploiare in produzione, è necessario:

1. **Backend — CORS:** Aggiornare `allow_origins=["*"]` in `main.py` con l'URL specifico del frontend in produzione.
2. **Frontend — URL API:** Aggiornare la costante `const API = 'http://localhost:8000'` (riga ~991 di `index.html`) con l'URL del backend in produzione.

---

## 11. Dipendenze

### Backend (`requirements.txt`)

| Pacchetto | Versione minima | Scopo |
|-----------|-----------------|-------|
| fastapi | ≥ 0.110.0 | Framework HTTP asincrono |
| uvicorn[standard] | ≥ 0.29.0 | Server ASGI per FastAPI |
| requests | ≥ 2.31.0 | Client HTTP (ViaggiaTreno + Nominatim) |

### Frontend (CDN)

| Libreria | Versione | Scopo |
|----------|----------|-------|
| Leaflet.js | latest | Mappa interattiva del percorso treno |

Nessuna altra dipendenza frontend: puro HTML/CSS/JS vanilla.
