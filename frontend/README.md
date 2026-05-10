# Frontend – RotaieVive

## Avvio rapido

Apri semplicemente `index.html` nel browser (con il backend già in esecuzione su `localhost:8000`).

Per sviluppo locale con ricaricamento automatico:
```bash
npx serve .       # oppure
python -m http.server 3000
```

## Struttura

```
frontend/
└── index.html    # tutto in un file: HTML + CSS + JS vanilla
```

## Funzionalità implementate

| Feature | Stato |
|---------|-------|
| Autocompletamento stazioni | ✅ |
| Partenze/Arrivi da stazione | ✅ |
| Percorso treno con fermate e ritardi | ✅ |
| Autocomplete numero treno | ✅ |
| Soglia ritardo configurabile + badge colorati | ✅ |
| News in tempo reale | ✅ |
| Contatore treni circolanti (ticker + stats) | ✅ |
| Salvataggio stazioni recenti (localStorage) | ✅ |
| Tema scuro/chiaro | ✅ |
| Supporto IT/EN | ✅ |
| Layout responsive mobile/desktop | ✅ |
| Toast notifiche per ritardi | ✅ |
| Timeline visuale fermate (passata/corrente/futura) | ✅ |

## Design

- **Estetica**: industriale/ferroviario — palette scura con accento giallo-rotaie
- **Font**: Bebas Neue (display) + IBM Plex Mono (dati) + IBM Plex Sans (corpo)
- **Animazioni**: entrata staggered delle righe, pulsing badge per ritardi critici, ticker live
