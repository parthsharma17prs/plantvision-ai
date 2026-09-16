# 🌿 PlantVision AI

**PlantVision AI** is an enterprise-grade, multi-spectral agricultural intelligence platform engineered to empower farmers, agronomists, and crop researchers. It unifies deep computer vision (**YOLOv8**), specialized entomological and nutritional diagnostic engines, generative AI (**Google Gemini**), automated **Google Drive IoT ingestion**, and **live hyper-local weather intelligence** to evaluate crop health in real-time and provide actionable agricultural advisories.

---

## 🚀 Tri-Engine Diagnostic Suite

PlantVision AI features a cohesive **Tri-Engine Diagnostic Pipeline** executed synchronously on every leaf scan:

### 1. 🔬 YOLOv8 Plant Disease & Pathology Engine
- Real-time deep learning detection of foliar pathogens across crops (potato, tomato, bell pepper, tea, apple, corn, etc.).
- Outputs detected disease classes, spatial bounding box visual overlays, lesion severity percentages, and an overall **Plant Health Index**.
- Direct mapping to standard and organic fungicide treatments.

### 2. 🐛 Pest Detection Adapter (`pest_adapter.py`)
- **Target Pests Diagnosed**: Spider Mites (*Tetranychidae*), Aphids (*Aphis gossypii*), Silverleaf Whiteflies (*Bemisia tabaci*), Foliar Thrips (*Thrips tabaci*), Serpentine Leaf Miners (*Liriomyza*), Caterpillars/Armyworms (*Spodoptera*), Helopeltis / Tea Mosquito Bug (*Helopeltis theivora*), and Mealybugs.
- **Computer Vision Extraction**: Quantifies chlorotic stippling ratio (sap-sucking damage), dark necrotic puncture flecks, and lamina perimeter edge erosion.
- **Integrated Pest Management (IPM)**:
  - **Biological Biocontrols**: Predatory mites (*Phytoseiulus persimilis*, *Neoseiulus californicus*), Green Lacewings (*Chrysoperla carnea*), Ladybird Beetles (*Coccinella septempunctata*), and parasitic wasps (*Encarsia formosa*).
  - **Bio-Pesticides**: Cold-pressed Neem oil (Azadirachtin), *Beauveria bassiana*, *Verticillium lecanii*.
  - **Precision Chemical Control**: Targeted active ingredients (Spiromesifen, Imidacloprid, Fipronil, Spinetoram, Diafenthiuron), calibrated field dilution dosages, and Pre-Harvest Interval (PHI) safety windows.
  - **Cultural & Scouting Protocols**: Colored sticky traps (yellow for whiteflies/aphids, blue for thrips), microclimate humidity management, and economic threshold scouting.

### 3. 🧪 Nutrition Deficiency Engine (`nutrition_engine.py`)
- **7-Element Balance Spectrum**: Evaluates canopy levels of **Nitrogen (N)**, **Phosphorus (P)**, **Potassium (K)**, **Magnesium (Mg)**, **Iron (Fe)**, **Calcium (Ca)**, and **Zinc (Zn)**.
- **Spectral Canopy Telemetry**:
  - **Chlorosis Index**: Evaluates generalized chlorophyll degradation and leaf yellowing.
  - **Margin Scorch Index**: Pinpoints peripheral brown necrosis typical of potassium stress.
  - **Purpling Index**: Quantifies anthocyanin accumulation induced by phosphorus deficiency.
  - **Vein-to-Lamina Contrast**: Detects interveinal chlorosis patterns characteristic of iron and magnesium deficiencies.
- **Actionable Prescriptions**:
  - **Rapid Foliar Spray Recipe**: Formulation, dilution rate (g/L), non-ionic wetting agent, and optimal diurnal application window.
  - **Soil Amendment & Root Zone Strategy**: Target rhizosphere pH ranges (e.g. 6.0–6.8), organic compost/FYM guidelines, and long-term soil fertility maintenance.

---

## 🌟 Platform Capabilities

### 🤖 Gemini AI Agronomist & Treatment Advisor
- Integrated **Google Gemini** generative assistant acting as a 24/7 digital agronomist.
- Provides comprehensive 4-part treatment plans:
  - **Immediate Chemical Cure**
  - **Organic & Biological Remedies**
  - **Root Causes & Symptoms**
  - **Long-term Preventive Farm Practices**

### 🌦️ Live Weather & Agricultural Spraying Advisory
- **Manual City Search**: Check weather and spraying safety for any city or district worldwide.
- **📍 GPS Live Location Detection**: One-tap device GPS coordinate resolution (`lat`/`lon`) with sub-district/village level precision.
- **Intelligent Spray Advisories**:
  - Rainfall alerts (prevent chemical wash-off and root collar rot).
  - Humidity warnings (evaluate fungal spore germination risk).
  - Temperature & phytotoxicity cautions (optimal spray timing guidance).

### 🛰️ Automated Google Drive Ingestion
- Background worker continuously polls a designated Google Drive folder for camera traps, drones, or field smartphone uploads.
- Automatically processes new leaf scans through the Tri-Engine pipeline and persists records in SQLite without manual intervention.

### 📊 Real-Time Farmer Dashboard
- Live disease distribution charts (healthy vs. diseased donut charts).
- Confidence trend analysis over time.
- Complete history log with real-time **Scans Archived** telemetry badge *(CSV export deprecated in favor of live telemetry)*.

### 🌐 Multilingual Accessibility
- Available in 6 languages: **English**, **हिंदी (Hindi)**, **मराठी (Marathi)**, **ગુજરાતી (Gujarati)**, **தமிழ் (Tamil)**, and **తెలుగు (Telugu)**.

---

## 🛠️ Architecture & Tech Stack

- **Backend**: Python 3.10+, Flask, SQLite, Ultralytics YOLOv8, PyTorch, NumPy, Pillow, Google Generative AI (`google-generativeai`), Google Drive API v3.
- **Pest & Nutrition Modules**: Custom pure-Python algorithmic and computer vision modules ([pest_adapter.py](file:///c:/Users/VINOD%20SHARMA/plantvision-ai/pest_adapter.py), [nutrition_engine.py](file:///c:/Users/VINOD%20SHARMA/plantvision-ai/nutrition_engine.py)).
- **Frontend (DTI)**: React 19, Vite, Tailwind CSS, Framer Motion, i18next, React Router.
- **APIs Integrated**: OpenWeather API (current weather & GPS coordinates), Google Gemini Pro Vision / Flash.

---

## 📁 Project Structure

```text
plantvision-ai/
├── app.py                     # Main Unified Flask Server & API
├── pest_adapter.py            # Pest Detection Adapter (IPM, Biocontrols, Chemical dosages)
├── nutrition_engine.py        # Nutrition Deficiency Engine (7-Element spectrum, Spectral indices)
├── data.yaml                  # YOLOv8 dataset configuration
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration & API keys
├── run_local.cmd              # One-click start script
├── start_backend.cmd          # Backend launch script
├── run_complete.cmd           # Complete build and launch script
├── DTI/                       # Modern React + Vite Web Application
│   ├── src/
│   │   ├── layers/
│   │   │   ├── ui/pages/      # Dashboard, Scan, Results (Multi-Tab), Weather, Login
│   │   │   ├── services/api/  # Weather, Prediction, Pest & Nutrition API clients
│   │   │   └── ai/components/ # Floating AgriBot Chatbot
│   │   ├── i18n/              # Multilingual translations (en, hi, mr, gu, ta, te)
│   │   └── App.jsx
│   └── package.json
└── plant_dashboard/           # Standalone dashboard fallback
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
   - **Scan Page**: [http://127.0.0.1:5000/scan](http://127.0.0.1:5000/scan)
   - **Diagnostic Results**: [http://127.0.0.1:5000/results](http://127.0.0.1:5000/results)
   - **Weather & Spray Advisor**: [http://127.0.0.1:5000/weather](http://127.0.0.1:5000/weather)
   - **Farm Dashboard**: [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)

### Option C: Frontend Development Mode
If actively modifying the React frontend:
```bash
cd DTI
npm run dev
```
*(Development server runs at `http://localhost:5173` with proxy to backend on port 5000).*

---

## 🔌 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | `GET` | Server health, model weights, Drive worker state |
| `/api/predict` | `POST` | Upload leaf image for Tri-Engine analysis (YOLOv8 + Pest + Nutrition) |
| `/api/diagnose/pest` | `POST` | Dedicated endpoint for Pest Detection Adapter analysis |
| `/api/diagnose/nutrition` | `POST` | Dedicated endpoint for Nutrition Deficiency Engine analysis |
| `/api/latest-result` | `GET` | Fetches the most recent scan with full pest, nutrition, and pathology data |
| `/api/history` | `GET` | Returns list of past scan diagnoses and telemetry metrics |
| `/weather?city=<name>` | `GET` | Live weather and spray advisory by city name |
| `/weather?lat=<lat>&lon=<lon>` | `GET` | Live weather and spray advisory by GPS coordinates |
| `/chat` | `POST` | Interacts with Gemini AgriBot conversational assistant |
| `/api/recommendation` | `POST` | Generates detailed 4-section AI treatment remedy |
| `/api/auth/signup` | `POST` | Registers a new user account |
| `/api/auth/login` | `POST` | Authenticates user credentials |

---

## 🛡️ License & Contributing

Built for agricultural research and field automation. Contributions, issue reports, and feature suggestions are welcome!
