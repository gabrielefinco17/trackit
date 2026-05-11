# Deploy Instructions

This document contains all the necessary instructions to start and deploy the **TRACK IT** application locally, consolidated from the frontend and backend setups.

## 1. Backend Setup

The backend is a proxy service built with Python and FastAPI. It must be running for the frontend to fetch and parse train data correctly.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**
   - **Mac/Linux:** `source .venv/bin/activate`
   - **Windows:** `.venv\Scripts\activate`

4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The backend will now be available at **http://localhost:8000**.
   *Note: Interactive API documentation is automatically generated and available at http://localhost:8000/docs*

---

## 2. Frontend Setup

The frontend is a lightweight, dependency-free vanilla web interface contained inside `index.html`. 

**CRITICAL:** It must be served via a local HTTP server (not opened directly via `file:///` in your browser) to avoid CORS issues and allow API fetch requests to succeed.

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Serve the files:**
   You can use any simple HTTP server of your choice. Here are two standard and easy options:
   
   **Option A: Using Node.js (if installed)**
   ```bash
   npx serve .
   ```
   
   **Option B: Using Python (if installed)**
   ```bash
   python3 -m http.server 3000
   ```

3. **Access the Application:**
   Open your browser and navigate to the address provided by your server (usually **http://localhost:3000**).

---

## ⚠️ Notes on Deployment to Production

If you plan to deploy this application to a public server (e.g. Vercel, Heroku, DigitalOcean):
- **CORS Configuration**: The backend `main.py` needs to have its `allow_origins` array updated to reflect your production frontend URL instead of just `*`.
- **API URL**: The frontend `index.html` has a hardcoded `const API = 'http://localhost:8000'` block near the bottom of the script section. This must be updated to point to your live production backend URL before deploying.
