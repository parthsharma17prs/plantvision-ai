# 🌿 PlantVision AI — Multi-Spectral Agricultural Intelligence Platform

**PlantVision AI** is an enterprise-grade agricultural intelligence and crop pathology platform engineered for agronomists, farmers, and agricultural researchers. It unifies deep computer vision (**YOLOv8**), algorithmic entomology and foliar nutrition diagnostics (**Tri-Engine Diagnostic Suite**), generative AI agronomy advisories (**Google Gemini**), automated **Google Drive IoT ingestion**, and **live hyper-local weather intelligence** with GPS spraying advisories.

---

## 🚀 Tri-Engine Diagnostic Suite

PlantVision AI executes three synchronous diagnostic engines on every analyzed leaf image:

```text
                                  ┌───────────────────────────┐
                                  │     Input Leaf Image      │
                                  └─────────────┬─────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
    ┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────────┐
    │     1. YOLOv8 Pathology  │   │  2. Pest Adapter (IPM)   │   │ 3. Nutrition Deficiency  │
    ├──────────────────────────┤   ├──────────────────────────┤   ├──────────────────────────┤
    │ • 30 PlantDoc Classes    │   │ • 8 Major Pest Vectors   │   │ • 7 Nutrient Elements    │
    │ • Disease Bounding Boxes │   │ • Chlorotic Stippling %  │   │ • Spectral Canopy Telemetry│
    │ • Lesion Severity Index  │   │ • Puncture Fleck Ratio   │   │ • Rapid Foliar Recipe    │
    │ • Plant Health Score %   │   │ • Bio & Chemical Control │   │ • Soil Amendment Plan    │
    └──────────────────────────┘   └──────────────────────────┘   └──────────────────────────┘
```

### 1. 🔬 YOLOv8 Plant Disease & Pathology Engine
- Trained on **PlantDoc** and **PlantVillage** multi-class foliar datasets.
- Real-time localization with spatial bounding box overlays.
- Computes infected surface area percentage, lesion severity index, and overall **Plant Health Index**.
- Direct classification across 30 foliar disease categories (blights, spots, rusts, molds, viruses, and healthy states).

### 2. 🐛 Pest Detection Adapter (`pest_adapter.py`)
- **Target Pests Evaluated**: Spider Mites (*Tetranychidae*), Aphids (*Aphis gossypii*), Silverleaf Whiteflies (*Bemisia tabaci*), Foliar Thrips (*Thrips tabaci*), Serpentine Leaf Miners (*Liriomyza*), Caterpillars/Armyworms (*Spodoptera*), Helopeltis / Tea Mosquito Bug (*Helopeltis theivora*), and Mealybugs.
- **Computer Vision Extraction**: Measures chlorotic stippling ratio (sap-sucking damage), necrotic puncture flecks, and perimeter lamina erosion.
- **Integrated Pest Management (IPM)**:
  - **Biological Controls**: Predatory mites (*Phytoseiulus persimilis*), Green Lacewings (*Chrysoperla carnea*), Ladybird Beetles (*Coccinella septempunctata*).
  - **Biopesticides**: Cold-pressed Neem oil (Azadirachtin), *Beauveria bassiana*, *Verticillium lecanii*.
  - **Targeted Chemical Dosages**: Calibrated field dilution rates (e.g., Spiromesifen, Imidacloprid, Fipronil) with Pre-Harvest Interval (PHI) safety windows.

### 3. 🧪 Nutrition Deficiency Engine (`nutrition_engine.py`)
- **7-Element Balance Spectrum**: Nitrogen (**N**), Phosphorus (**P**), Potassium (**K**), Magnesium (**Mg**), Iron (**Fe**), Calcium (**Ca**), and Zinc (**Zn**).
- **Spectral Canopy Telemetry**:
  - *Chlorosis Index*: Generalized chlorophyll degradation.
  - *Margin Scorch Index*: Peripheral necrosis characteristic of Potassium deficit.
  - *Purpling Index*: Anthocyanin accumulation indicating Phosphorus starvation.
  - *Vein-to-Lamina Contrast*: Interveinal chlorosis patterns for Iron and Magnesium imbalances.
- **Actionable Prescriptions**: Complete foliar spray formulation (g/L with wetting agents) and root zone soil amendment guidelines.

---

## 📦 Datasets & Model Pipeline

The platform is integrated with two comprehensive agricultural datasets:

| Dataset | Source Archive | Size | Samples | Type | Target Classes | Configuration |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PlantDoc** | `archive (1).zip` | 74.1 MB | 2,567 images | Object Detection (BBoxes) | 30 classes | [`data_plantdoc.yaml`](file:///c:/Users/VINOD%20SHARMA/plantvision-ai/data_plantdoc.yaml) |
| **PlantVillage** | `archive.zip` | 657.5 MB | 20,639 images | Normalized Detection Splits | 15 classes | [`data_plantvillage.yaml`](file:///c:/Users/VINOD%20SHARMA/plantvision-ai/data_plantvillage.yaml) |

### Dataset Extraction & Preparation Utility (`setup_datasets.py`)
Extracts and validates both archives into a standardized training structure:
```powershell
python setup_datasets.py
```
- **PlantDoc**: Extracted into `datasets/plantdoc/` (`train`: 1,979, `valid`: 349, `test`: 239).
- **PlantVillage**: De-duplicated from nested hierarchies into `datasets/plantvillage/` (`train`: 16,504, `val`: 4,134).

---

## 🏋️ Training & Inference Workflow

### 1. Training the Model (`train_yolo.py`)
Train YOLOv8 on either dataset with automated export to `best.pt`:
```powershell
# Train on PlantDoc (default - 30 object detection classes):
python train_yolo.py --dataset plantdoc --epochs 50 --imgsz 640

# Train on PlantVillage (15 classes):
python train_yolo.py --dataset plantvillage --epochs 50 --imgsz 640

# Quick verification smoke-test (1 epoch on 2% subset for CPU):
python train_yolo.py --dataset plantdoc --quick-test --device cpu
```
> **Auto-Deployment**: When training finishes, `train_yolo.py` automatically copies the weights to `best.pt` in the project root, which `app.py` loads on startup.

### 2. Terminal Model Inference (`run_model.py`)
Run the full Tri-Engine suite directly from the command line:
```powershell
# Run inference on a random sample from the test split:
python run_model.py

# Run on a specific leaf image:
python run_model.py --source "datasets/plantdoc/test/images/sample.jpg"

# Run on 5 random samples with custom confidence threshold:
python run_model.py --num-samples 5 --conf 0.15
```
> Annotated detection images with bounding boxes are saved to `runs/detect/predict/`.

---

## 🌐 Full Project Architecture & Execution

The project operates on a coordinated dual-server architecture:

```text
┌─────────────────────────────────────────────────────────────┐
│                       Web Browser                           │
│     (Dashboard, Scanner, Results, Weather, Login, Chat)     │
└───────────────┬─────────────────────────────┬───────────────┘
                │ :5173 (HMR Dev)             │ :5000 (Direct / Production)
                ▼                             ▼
┌──────────────────────────────┐     ┌────────────────────────────────────┐
│      Vite Frontend Dev       │     │     Flask Unified Platform         │
│     (React 19 + Tailwind)    │────►│ • SQLite Persistence               │
│ • Proxies /api to :5000      │     │ • YOLOv8 Engine (best.pt)          │
│ • Proxies /weather to :5000  │     │ • Tri-Engine Diagnostics           │
│ • Proxies /chat to :5000     │     │ • Google Drive Ingestion Poller    │
└──────────────────────────────┘     │ • OpenWeather & Gemini Integrations│
                                     └────────────────────────────────────┘
```

### Running the Application

#### Option A: One-Click Full Project Launch (Windows)
Double-click or execute from the terminal:
```cmd
run_complete.cmd
```
*Builds the DTI React frontend and launches the unified Flask backend serving everything on port 5000.*

#### Option B: Development Mode with Live Hot-Reloading
1. **Start Backend Server**:
   ```cmd
   run_local.cmd
   ```
   *(Running on `http://127.0.0.1:5000`)*

2. **Start Frontend Dev Server**:
   ```bash
   cd DTI
   npm run dev
   ```
   *(Running on `http://localhost:5173` with instant Hot Module Replacement)*

---

## 📱 Web Application Interfaces

Once running, navigate to:

| Interface | URL | Purpose |
| :--- | :--- | :--- |
| **Main Landing Page** | [http://localhost:5173/](http://localhost:5173/) | Overview, platform statistics, quick actions |
| **AI Leaf Scanner** | [http://localhost:5173/scan](http://localhost:5173/scan) | Drag-and-drop leaf upload, webcam capture, live bounding box detection |
| **Diagnostic Results** | [http://localhost:5173/results](http://localhost:5173/results) | Multi-tab analysis: Pathology, Pest IPM, Nutrition, AI Agronomist |
| **Farmer Dashboard** | [http://localhost:5173/dashboard](http://localhost:5173/dashboard) | Live scan history, disease distribution donuts, confidence analytics |
| **Weather & Spraying** | [http://localhost:5173/weather](http://localhost:5173/weather) | Live GPS weather, rain alerts, humidity warnings, optimal spray timing |
| **Server Health API** | [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health) | Real-time JSON health check, model weight verification |

---

## 📁 Repository Structure

```text
plantvision-ai/
├── app.py                     # Main Unified Flask Server & API
├── pest_adapter.py            # Pest Detection Adapter (IPM, Biocontrols, Chemical dosages)
├── nutrition_engine.py        # Nutrition Deficiency Engine (7-Element spectrum, Spectral indices)
├── setup_datasets.py          # Dataset Extractor & YAML Generator for PlantDoc & PlantVillage
├── train_yolo.py              # YOLOv8 Training Script with Presets & Auto-Export
├── run_model.py               # Terminal Model Inference & Tri-Engine CLI Runner
├── best.pt                    # Active Trained YOLOv8 Model Weights
├── yolov8n.pt                 # Base Pretrained Weights Fallback
├── data_plantdoc.yaml         # YOLO Config for PlantDoc Dataset (30 classes)
├── data_plantvillage.yaml     # YOLO Config for PlantVillage Dataset (15 classes)
├── requirements.txt           # Python Dependencies
├── run_complete.cmd           # Complete Production Build & Launch Script
├── run_local.cmd              # Fast Backend Launch Script
├── datasets/                  # Extracted Training Datasets
│   ├── plantdoc/              # PlantDoc (train/valid/test with bounding box labels)
│   └── plantvillage/          # PlantVillage (train/val splits)
├── DTI/                       # Modern React 19 + Vite Frontend
│   ├── src/
│   │   ├── layers/
│   │   │   ├── ui/pages/      # Dashboard, Scan, Results, Weather, Login
│   │   │   ├── services/api/  # Prediction, Weather, Auth API Clients
│   │   │   └── ai/components/ # AgriBot Conversational Assistant
│   │   ├── i18n/              # 6 Languages (en, hi, mr, gu, ta, te)
│   │   └── App.jsx
│   └── package.json
└── plant_dashboard/           # Standalone Dashboard Fallback
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | `GET` | Health status, active weights (`best.pt`), model trained status |
| `/api/predict` | `POST` | Upload leaf image for Tri-Engine analysis (YOLOv8 + Pest + Nutrition) |
| `/api/diagnose/pest` | `POST` | Dedicated endpoint for Pest Detection Adapter analysis |
| `/api/diagnose/nutrition` | `POST` | Dedicated endpoint for Nutrition Deficiency Engine analysis |
| `/api/latest-result` | `GET` | Retrieves the most recent scan with full pathology and telemetry |
| `/api/history` | `GET` | Returns list of past scan records stored in SQLite |
| `/weather?city=<name>` | `GET` | Live weather and spray advisory by city |
| `/weather?lat=<lat>&lon=<lon>` | `GET` | Live weather and spray advisory by GPS coordinates |
| `/chat` | `POST` | Google Gemini agricultural conversational assistant |
| `/api/recommendation` | `POST` | Generates 4-part treatment plan (chemical, organic, cause, prevention) |
| `/api/auth/login` | `POST` | User authentication |
| `/api/auth/signup` | `POST` | User registration |

---

## 🛡️ License & Contributing

Built for agricultural research, crop health monitoring, and field automation. Contributions, issue reports, and feature suggestions are welcome!
