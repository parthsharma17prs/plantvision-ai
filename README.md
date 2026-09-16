# 🌿 PlantVision AI

**PlantVision AI** is an advanced, AI-powered agricultural intelligence platform designed to empower farmers, agronomists, and researchers. It integrates computer vision (**YOLOv8**), generative AI (**Google Gemini**), automated **Google Drive IoT ingestion**, and **live hyper-local weather intelligence** to detect plant diseases in real-time and provide actionable agricultural advisories.

---

## 🚀 Key Features

### 1. 🔍 YOLOv8 Plant Disease Diagnostics
- Real-time deep learning detection of leaf diseases across crops (potato, tomato, bell pepper, tea, etc.).
- Outputs detected disease classes, bounding box visual overlays, severity percentages, and an overall **Plant Health Index**.
- Standard and organic pesticide recommendations automatically mapped to diagnosed diseases.

### 2. 🤖 Gemini AI Agronomist & Treatment Advisor
- Integrated **Google Gemini** generative assistant acting as a 24/7 digital agronomist.
- Provides comprehensive 4-part treatment plans:
  - **Immediate Chemical Cure**
  - **Organic & Biological Remedies**
  - **Root Causes & Symptoms**
  - **Long-term Preventive Farm Practices**

### 3. 🌦️ Live Weather & Agricultural Spraying Advisory
- **Manual City Search**: Check weather and spraying safety for any city or district worldwide.
- **📍 GPS Live Location Detection**: One-tap device GPS coordinate resolution (`lat`/`lon`) with sub-district/village level precision.
- **Intelligent Spray Advisories**:
  - Rainfall alerts (prevent chemical runoff and root collar rot).
  - Humidity warnings (evaluate fungal spore germination risk).
  - Temperature & phytotoxicity cautions (optimal spray timing guidance).

### 4. 🛰️ Automated Google Drive Ingestion
- Background worker continuously polls a designated Google Drive folder for camera traps, drones, or field smartphone uploads.
- Automatically processes new leaf scans through YOLOv8 and stores results into the local database without manual intervention.

### 5. 📊 Real-Time Farmer Dashboard
- Live disease distribution charts (healthy vs. diseased donut charts).
- Confidence trend analysis over time.
- Complete searchable scan history with downloadable summaries.

### 6. 🌐 Multilingual Accessibility
- Available in 6 languages: **English**, **हिंदी (Hindi)**, **मराठी (Marathi)**, **ગુજરાતી (Gujarati)**, **தமிழ் (Tamil)**, and **తెలుగు (Telugu)**.

---

## 🛠️ Architecture & Tech Stack

- **Backend**: Python 3.10+, Flask, SQLite, Ultralytics YOLOv8, PyTorch, Google Generative AI (`google-generativeai`), Google Drive API v3.
- **Frontend (DTI)**: React 19, Vite, Tailwind CSS, Framer Motion, i18next, React Router.
- **APIs Integrated**: OpenWeather API (current weather & GPS coordinates), Google Gemini Pro Vision / Flash.

---

## 📁 Project Structure

```text
plantvision-ai/
├── app.py                     # Main Unified Flask Server & API
├── data.yaml                  # YOLOv8 dataset configuration
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration & API keys
├── run_local.cmd              # One-click start script
├── start_backend.cmd          # Backend launch script
├── run_complete.cmd           # Complete build and launch script
├── DTI/                       # Modern React + Vite Web Application
│   ├── src/
│   │   ├── layers/
│   │   │   ├── ui/pages/      # Dashboard, Scan, Results, Weather, Login
│   │   │   ├── services/api/  # Weather, Prediction, Auth API clients
│   │   │   └── ai/components/ # Floating AgriBot Chatbot
│   │   ├── i18n/              # Multilingual translations (en, hi, mr, gu, ta, te)
│   │   └── App.jsx
│   └── package.json
└── plant_dashboard/           # Static standalone dashboard fallback
    └── static/
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- **Python**: Version 3.10 or higher ([python.org](https://www.python.org/downloads/))
- **Node.js**: Version 18+ and npm ([nodejs.org](https://nodejs.org/))

### 2. Clone and Configure Environment
1. Clone the repository or navigate to the project directory:
   ```bash
   cd plantvision-ai
   ```

2. Create and configure your `.env` file:
   ```env
   # Gemini API Key for AI chat and agronomy recommendations
   GEMINI_API_KEY=your_gemini_api_key_here

   # OpenWeather API Key for live weather and GPS spraying advisor
   OPENWEATHER_API_KEY=your_openweather_api_key_here

   # Optional: Google Drive folder ID for automated drone/camera ingestion
   GDRIVE_FOLDER_ID=your_gdrive_folder_id_here
   ```

### 3. Install Dependencies
* **Python Backend**:
  ```bash
  pip install -r requirements.txt
  ```
* **React Frontend**:
  ```bash
  cd DTI
  npm install
  npm run build
  cd ..
  ```

---

## 🚀 Running the Application

### Option A: Quick Launch (Windows)
Double-click or run from command prompt:
```cmd
run_local.cmd
```

### Option B: Manual Launch
1. **Start the Unified Server**:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to:
   - **Main App**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - **Weather & Spray Advisor**: [http://127.0.0.1:5000/weather](http://127.0.0.1:5000/weather)
   - **Farm Dashboard**: [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)

### Option C: Frontend Hot-Reload Development
If modifying the React frontend live:
```bash
cd DTI
npm run dev
```
*(Development server runs at `http://localhost:5173` with proxy to backend on port 5000).*

---

## 🔌 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | `GET` | Server status, model weights, and Drive worker state |
| `/api/predict` | `POST` | Upload leaf image for YOLOv8 disease classification |
| `/api/latest-result` | `GET` | Fetches the most recent scan prediction & visual overlay |
| `/api/history` | `GET` | Returns list of past scan diagnoses and metrics |
| `/weather?city=<name>` | `GET` | Live weather and spray advisory by city name |
| `/weather?lat=<lat>&lon=<lon>` | `GET` | Live weather and spray advisory by GPS coordinates |
| `/chat` | `POST` | Interacts with Gemini AgriBot conversational assistant |
| `/recommendation` | `POST` | Generates detailed 4-section AI treatment remedy |
| `/api/auth/signup` | `POST` | Registers a new user account |
| `/api/auth/login` | `POST` | Authenticates user credentials |

---

## 🛡️ License & Contributing

Built for agricultural research and field automation. Contributions, issue reports, and feature suggestions are welcome!
