# TRACK IT

A modern, minimal, typography-driven web application to track trains in real-time in Italy (via Trenitalia ViaggiaTreno API).

## 🚀 Features

- **Real-time Tracking**: Monitor train departures and arrivals from any Italian station.
- **Train Details**: View the exact route of a train, showing past and future stops, delays, and current location on a map.
- **Stark Minimalist UI**: High-contrast pure black and white monochrome design focusing completely on typography and spacing.
- **Multi-language Support**: Seamless toggle between Italian and English interfaces without page reloads.
- **Smart Search Engine**: Autocomplete functionality for stations and train numbers.
- **Real-time News**: Built-in access to current railway traffic news and alerts.
- **Statistics**: View live statistics on daily train volume and currently running trains.

## 🏗 Software Structure

The application follows a simple, robust Client-Server architecture:

### Frontend
A pure, dependency-free vanilla web interface contained entirely in one directory: `frontend/`.
- **HTML5/CSS3**: Utilizes native CSS variables, grid layouts, and media queries for complete responsiveness inside `index.html`.
- **JavaScript (ES6+)**: Handles all state, routing (via DOM manipulation), API calls, and i18n logic.
- **Leaflet.js**: Used for rendering the map in the train detail panel.

### Backend
A fast, asynchronous proxy server built with **FastAPI** in the `backend/` directory.
- **Python/FastAPI**: Handles requests and proxies them to the undocumented Trenitalia API.
- **Geocoding**: Uses a built-in memory cache system mapped to Nominatim for resolving train station coordinates to render the map, with `POST /geocode/batch` support to avoid rate limiting.
- **CORS Handling**: Properly configured to allow the frontend to consume data smoothly.

## 🧪 Tests Done

- **API Robustness**: The geocoding endpoint was refactored with a thread-safe cache to handle batch requests efficiently and eliminate Nominatim 429 Rate Limit errors. Single geocode endpoints return `null` instead of `404` to prevent breaking the map rendering flow.
- **Frontend Fallbacks**: The frontend handles null or error responses gracefully. Data mapping was corrected so `binario` (Platform) correctly displays depending on Arrival or Departure context.
- **Responsive Design Verification**: Verified layouts on mobile formats (max-width: 700px), ensuring the grid structure collapses gracefully for smaller screens and columns are hidden correctly.
- **Localization Checks**: Verified that all static strings correctly switch between English and Italian upon user selection.
