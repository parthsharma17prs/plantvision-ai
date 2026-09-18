#!/usr/bin/env python3
"""
PlantVision AI — Unified Platform Server with Live Google Drive to YOLO to Dashboard Pipeline
=============================================================================================
Combines:
1. Google Drive Ingestion Worker (Drive API v3, gdown, or local feeder watch)
2. YOLOv8 Plant Disease Diagnostics (bounding boxes, severity %, health %, annotated overlays)
3. Gemini AI Agriculture Chatbot & Dynamic 4-Section Treatment Advisor
4. SQLite Persistence (predictions, user accounts)
5. OpenWeather Integration & Agricultural Spraying Advisory
6. React Vite DTI Frontend + Static Dashboard routing
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import math
import os
import random
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from flask import Flask, jsonify, request, send_from_directory, Response
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from PIL import Image
from ultralytics import YOLO

from pest_adapter import PestDetectionAdapter
from nutrition_engine import NutritionDeficiencyEngine

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "predictions.db"
DEFAULT_WEIGHTS = ROOT / "yolov8n.pt"
FEED_DIR = ROOT / "agribot_feed"
FEED_DIR.mkdir(exist_ok=True)

# ─── Environment Configuration ───────────────────────────────────────────────
def _parse_root_dotenv() -> None:
    path = ROOT / ".env"
    if not path.is_file() or path.stat().st_size == 0:
        return
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and val:
            os.environ[key] = val

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=True, encoding="utf-8-sig")
except ImportError:
    pass

_parse_root_dotenv()

GEMINI_API_KEY_FALLBACK = ""
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "1nRLc9j0Fb3XoYu1WzeeknM1acwdzAndE").strip()
GDRIVE_POLL_INTERVAL = int(os.environ.get("GDRIVE_POLL_INTERVAL", "5"))

# ─── Disease Classes and Standard Agricultural Recommendations ────────────────
CLASS_NAME_MAPPING: dict[str, str] = {
    # PlantDoc / Field classes
    "Potato leaf early blight": "Early Blight",
    "Tomato Early blight leaf": "Early Blight",
    "Potato leaf late blight": "Late Blight",
    "Tomato leaf late blight": "Late Blight",
    "Tomato Septoria leaf spot": "Leaf Spot",
    "Bell_pepper leaf spot": "Leaf Spot",
    "Tomato leaf bacterial spot": "Bacterial Spot",
    "Tomato mold leaf": "Leaf Mold",
    "Tomato two spotted spider mites leaf": "Spider Mites",
    "Tomato leaf yellow virus": "Yellow Leaf Curl Virus",
    "Tomato leaf mosaic virus": "Mosaic Virus",
    "Squash Powdery mildew leaf": "Powdery Mildew",
    "Corn Gray leaf spot": "Gray Leaf Spot",
    "Corn leaf blight": "Leaf Blight",
    "Corn rust leaf": "Rust",
    "Apple Scab Leaf": "Apple Scab",
    "Apple rust leaf": "Apple Rust",
    "grape leaf black rot": "Black Rot",
    "Tomato Target Spot": "Target Spot",
    # PlantVillage raw classes
    "Pepper__bell___Bacterial_spot": "Bacterial Spot",
    "Pepper__bell___healthy": "Healthy",
    "Potato___Early_blight": "Early Blight",
    "Potato___Late_blight": "Late Blight",
    "Potato___healthy": "Healthy",
    "Tomato_Bacterial_spot": "Bacterial Spot",
    "Tomato_Early_blight": "Early Blight",
    "Tomato_Late_blight": "Late Blight",
    "Tomato_Leaf_Mold": "Leaf Mold",
    "Tomato_Septoria_leaf_spot": "Leaf Spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Spider Mites",
    "Tomato__Target_Spot": "Target Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Yellow Leaf Curl Virus",
    "Tomato__Tomato_mosaic_virus": "Mosaic Virus",
    "Tomato_healthy": "Healthy",
    # Healthy foliage
    "Apple leaf": "Healthy",
    "Bell_pepper leaf": "Healthy",
    "Blueberry leaf": "Healthy",
    "Cherry leaf": "Healthy",
    "Peach leaf": "Healthy",
    "Potato leaf": "Healthy",
    "Raspberry leaf": "Healthy",
    "Soyabean leaf": "Healthy",
    "Soybean leaf": "Healthy",
    "Strawberry leaf": "Healthy",
    "Tomato leaf": "Healthy",
    "grape leaf": "Healthy",
    "Healthy": "Healthy",
    "Algal Leaf": "Algal Leaf",
    "Anthracnose": "Anthracnose",
    "Bird Eye Spot": "Bird Eye Spot",
    "Brown Blight": "Brown Blight",
    "Gray Light": "Gray Light",
    "Red Leaf Spot": "Red Leaf Spot",
    "White Spot": "White Spot",
}

PESTICIDE_RECOMMENDATIONS: dict[str, str] = {
    "Early Blight": "Spray Mancozeb 75% WP @ 2.5g/L or Chlorothalonil 75% WP @ 2g/L. Repeat every 10–14 days.",
    "Late Blight": "Spray Metalaxyl 8% + Mancozeb 64% WP @ 2g/L or Copper Oxychloride 50% WP @ 3g/L urgently.",
    "Leaf Spot": "Apply Copper fungicide or Neem oil extract (5ml/L) with systemic azoxystrobin spray.",
    "Bacterial Spot": "Spray Copper Hydroxide 77% WP @ 2g/L + Streptocycline 100ppm to eliminate bacterial foliar infection.",
    "Leaf Mold": "Ensure adequate greenhouse ventilation. Spray Difenoconazole 25% EC @ 1ml/L or Chlorothalonil @ 2g/L.",
    "Spider Mites": "Apply Abamectin 1.9% EC @ 1ml/L or Fenpyroximate 5% EC @ 1.5ml/L. Introduce predatory phytoseiid mites.",
    "Target Spot": "Apply Azoxystrobin + Difenoconazole @ 1ml/L or Chlorothalonil 75% WP @ 2g/L.",
    "Yellow Leaf Curl Virus": "Vector-borne (Whitefly). Spray Acetamiprid 20% SP @ 0.5g/L or Imidacloprid 17.8% SL @ 0.5ml/L. Remove diseased plants.",
    "Mosaic Virus": "Disinfect tools with 10% trisodium phosphate. Control aphid vectors using Thiamethoxam @ 0.2g/L. Rogue infected plants.",
    "Apple Scab": "Apply Captan 50% WP @ 2.5g/L or Difenoconazole 25% EC @ 0.5ml/L at green tip stage.",
    "Apple Rust": "Apply Myclobutanil 10% WP @ 1g/L or Mancozeb 75% WP @ 2g/L before blossom.",
    "Powdery Mildew": "Spray Wettable Sulfur 80% WP @ 3g/L or Dinocap 48% EC @ 1ml/L.",
    "Rust": "Apply Propiconazole 25% EC @ 1ml/L or Tebuconazole 25.9% EC @ 1ml/L.",
    "Black Rot": "Spray Mancozeb @ 2.5g/L or Pyraclostrobin 20% WG @ 0.5g/L during early shoot emergence.",
    "Algal Leaf": "Spray Copper Oxychloride 50% WP @ 3g/L or Copper Hydroxide 77% WP @ 2g/L.",
    "Anthracnose": "Prune infected twigs. Spray Chlorothalonil 75% WP @ 2g/L or Carbendazim 50% WP @ 1g/L.",
    "Bird Eye Spot": "Spray Hexaconazole 5% EC @ 2ml/L or Propiconazole 25% EC @ 1ml/L.",
    "Brown Blight": "Apply Mancozeb 75% WP @ 2.5g/L or Azoxystrobin 23% SC @ 1ml/L.",
    "Gray Light": "Prune affected bushes. Apply Propiconazole 25% EC @ 1ml/L after plucking rounds.",
    "Helopeltis": "Spray Thiamethoxam 25% WG @ 0.2g/L or Quinalphos 25% EC @ 2ml/L.",
    "Red Leaf Spot": "Spray Copper Hydroxide 77% WP @ 2g/L or Copper Oxychloride @ 3g/L.",
    "White Spot": "Apply Wettable Sulfur 80% WP @ 3g/L or Potassium Bicarbonate @ 5g/L.",
    "Healthy": "Crop foliage is vigorous and healthy! Maintain balanced NPK nutrition, scheduled drip irrigation, and clean cultivation.",
}

# ─── Strict JSON Provider ───────────────────────────────────────────────────
def json_safe_payload(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): json_safe_payload(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe_payload(v) for v in obj]
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (np.floating, float)):
        x = float(obj)
        if math.isnan(x) or math.isinf(x):
            return 0.0
        return x
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, str) or obj is None:
        return obj
    return obj

class StrictJSONProvider(DefaultJSONProvider):
    ensure_ascii = False
    def dumps(self, obj: Any, **kwargs: Any) -> str:
        kwargs.setdefault("allow_nan", False)
        if isinstance(obj, (dict, list)):
            obj = json_safe_payload(obj)
        return super().dumps(obj, **kwargs)

# ─── App Setup ──────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=None)
app.json = StrictJSONProvider(app)
CORS(app)

FRONTEND_DIST = ROOT / "DTI" / "dist"
ASSISTANT_DIR = ROOT / "assistant"
PLANT_DASHBOARD_STATIC = ROOT / "plant_dashboard" / "static"

# ─── Database Initialization ────────────────────────────────────────────────
def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            disease TEXT NOT NULL,
            confidence_pct REAL NOT NULL,
            severity_pct REAL NOT NULL,
            health_pct REAL NOT NULL,
            recommendation TEXT NOT NULL,
            source TEXT DEFAULT 'upload',
            filename TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )
    try:
        conn.execute("ALTER TABLE predictions ADD COLUMN source TEXT DEFAULT 'upload'")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE predictions ADD COLUMN filename TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()

# ─── Model Loading ──────────────────────────────────────────────────────────
def pick_weights() -> Path:
    env_raw = os.environ.get("PLANTDOC_WEIGHTS", "").strip()
    if env_raw:
        env_path = Path(env_raw).expanduser()
        if not env_path.is_absolute():
            env_path = (ROOT / env_path).resolve()
        if env_path.is_file():
            return env_path
    for cand in [
        ROOT / "best.pt",
        ROOT / "runs" / "detect" / "train" / "weights" / "best.pt",
        ROOT / "runs" / "runs" / "detect" / "plant_disease_runs" / "yolo_train" / "weights" / "best.pt",
        ROOT / "runs" / "detect" / "runs" / "detect" / "train" / "weights" / "best.pt",
    ]:
        if cand.exists():
            return cand
    return DEFAULT_WEIGHTS

def load_model(weights_path: Path) -> YOLO:
    if not weights_path.exists():
        if weights_path.name == "yolov8n.pt":
            print("[INFO] Loading base yolov8n.pt model...")
            return YOLO("yolov8n.pt")
        raise FileNotFoundError(f"Weights not found: {weights_path}")
    return YOLO(str(weights_path))

WEIGHTS_PATH = pick_weights()
MODEL = load_model(WEIGHTS_PATH)

# ─── Shared Live State for Google Drive & Dashboard ─────────────────────────
state_lock = threading.Lock()
state = {
    "status": "ready",
    "drive_status": "initializing",
    "drive_folder_id": GDRIVE_FOLDER_ID,
    "last_processed_file_id": None,
    "last_processed_filename": None,
    "last_processed_timestamp": None,
    "latest_result": None,
    "total_drive_images_processed": 0,
    "error": None
}

# ─── Prediction & Image Processing Logic ────────────────────────────────────
def map_class_to_disease(raw_class_name: str) -> str:
    if "___" in raw_class_name:
        parts = raw_class_name.split("___", 1)
        if len(parts) == 2:
            plant, disease = parts
            disease = disease.replace("_", " ")
            if disease.lower() == "healthy":
                return f"{plant} Healthy"
            return disease.title()
    return CLASS_NAME_MAPPING.get(raw_class_name, raw_class_name)

def recommend_pesticide(disease_name: str) -> str:
    for k, v in PESTICIDE_RECOMMENDATIONS.items():
        if k.lower() in disease_name.lower():
            return v
    return PESTICIDE_RECOMMENDATIONS.get(
        disease_name, "Apply broad-spectrum bio-fungicide and isolate affected leaves. Consult agricultural officer."
    )

def compute_infected_area_pct(bbox_xyxy: tuple[float, float, float, float], image_w: int, image_h: int) -> float:
    x1, y1, x2, y2 = bbox_xyxy
    box_w = max(0.0, x2 - x1)
    box_h = max(0.0, y2 - y1)
    bbox_area = box_w * box_h
    image_area = float(max(1, image_w * image_h))
    return min(100.0, max(0.0, (bbox_area / image_area) * 100.0))

def decode_data_url(data_url: str) -> Image.Image:
    if "," not in data_url:
        raise ValueError("Invalid image payload.")
    encoded = data_url.split(",", 1)[1]
    image_bytes = base64.b64decode(encoded)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")

def encode_image_to_data_url(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def save_prediction_history(payload: dict[str, Any], source: str = "upload", filename: str = None) -> None:
    try:
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO predictions (created_at, disease, confidence_pct, severity_pct, health_pct, recommendation, source, filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                payload.get("disease", "Unknown"),
                payload.get("confidence", 0.0),
                payload.get("severity", 0.0),
                payload.get("plantHealth", 100.0),
                payload.get("suggestion", ""),
                source,
                filename or payload.get("filename")
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error saving prediction: {e}")

def run_ai_inference(image: Image.Image, filename: str = "leaf_scan.jpg", source: str = "upload", conf: float = 0.2) -> dict[str, Any]:
    """Universal AI inference pipeline for both Google Drive and manual scans."""
    image_np = np.array(image.convert("RGB"))
    results = MODEL.predict(source=image_np, conf=conf, verbose=False)
    if not results:
        raise RuntimeError("Model returned no results.")

    result = results[0]
    plotted_bgr = result.plot()
    annotated = Image.fromarray(plotted_bgr[:, :, ::-1])
    annotated_data_url = encode_image_to_data_url(annotated)

    names = MODEL.names
    boxes = result.boxes
    img_h, img_w = result.orig_shape

    if boxes is None or len(boxes) == 0:
        pest_res = PestDetectionAdapter.analyze(image, disease_hint="Healthy", plant_hint="Plant")
        nutr_res = NutritionDeficiencyEngine.analyze(image, plant_hint="Plant", disease_hint="Healthy")
        payload = {
            "success": True,
            "detected": False,
            "disease": "Healthy",
            "plant": "Plant",
            "confidence": 95.0,
            "status": "Healthy",
            "severity": 0.0,
            "plantHealth": 100.0,
            "infected_area": 0.0,
            "suggestion": "No diseased spots or pathogens detected. Leaves appear vigorous and healthy.",
            "annotatedImage": annotated_data_url,
            "detections": [],
            "pest_analysis": pest_res,
            "nutrition_analysis": nutr_res,
            "model": WEIGHTS_PATH.name,
            "model_trained": WEIGHTS_PATH.name != "yolov8n.pt",
            "filename": filename,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    else:
        detections: list[dict[str, Any]] = []
        for box in boxes:
            class_id = int(box.cls[0]) if box.cls is not None else -1
            raw_name = str(names.get(class_id, class_id))
            disease = map_class_to_disease(raw_name)
            box_conf = float(box.conf[0]) if box.conf is not None else 0.0
            confidence_pct = max(0.0, min(100.0, box_conf * 100.0))
            coords = box.xyxy[0].tolist()
            bbox_xyxy = (float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3]))
            infected_area_pct = compute_infected_area_pct(bbox_xyxy, img_w, img_h)
            severity_pct = max(0.0, min(100.0, (confidence_pct + infected_area_pct) / 2.0))
            health_pct = max(0.0, min(100.0, 100.0 - infected_area_pct))
            plant_name = "Plant"
            if "___" in raw_name:
                plant_name = raw_name.split("___", 1)[0].replace("_", " ").title()
            is_healthy = disease.lower().endswith("healthy") or disease.lower() == "healthy"
            detections.append({
                "disease": disease,
                "plant": plant_name,
                "confidence": confidence_pct,
                "severity": severity_pct,
                "plantHealth": health_pct,
                "infected_area": round(infected_area_pct, 2),
                "status": "Healthy" if is_healthy else "Diseased",
                "suggestion": recommend_pesticide(disease),
                "bbox": bbox_xyxy,
            })

        best = max(detections, key=lambda d: d["confidence"])
        pest_res = PestDetectionAdapter.analyze(image, disease_hint=best["disease"], plant_hint=best["plant"])
        nutr_res = NutritionDeficiencyEngine.analyze(image, plant_hint=best["plant"], disease_hint=best["disease"])

        payload = {
            "success": True,
            "detected": True,
            "disease": best["disease"],
            "plant": best["plant"],
            "confidence": round(best["confidence"], 2),
            "status": best["status"],
            "severity": round(best["severity"], 2),
            "plantHealth": round(best["plantHealth"], 2),
            "infected_area": round(best["infected_area"], 2),
            "suggestion": best["suggestion"],
            "annotatedImage": annotated_data_url,
            "detections": detections,
            "pest_analysis": pest_res,
            "nutrition_analysis": nutr_res,
            "model": WEIGHTS_PATH.name,
            "model_trained": WEIGHTS_PATH.name != "yolov8n.pt",
            "filename": filename,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    save_prediction_history(payload, source=source, filename=filename)

    with state_lock:
        state["latest_result"] = payload
        state["last_processed_filename"] = filename
        state["last_processed_timestamp"] = payload["timestamp"]
        state["status"] = "ok"

    return payload

# ─── Google Drive Ingestion Worker ──────────────────────────────────────────
def get_drive_service():
    """Attempts to construct Google Drive v3 API service from available credentials."""
    import pickle
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    possible_creds = [
        ROOT / "Agribot" / "token.pickle",
        ROOT.parent / "Agribot" / "token.pickle",
        ROOT / "token.pickle",
    ]
    creds = None
    for p in possible_creds:
        if p.is_file():
            try:
                with open(p, "rb") as f:
                    creds = pickle.load(f)
                if creds and creds.valid:
                    return build("drive", "v3", credentials=creds)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    return build("drive", "v3", credentials=creds)
            except Exception as err:
                print(f"⚠️ Failed reading {p}: {err}")
    return None

def download_drive_file_media(service, file_id: str) -> Image.Image:
    from googleapiclient.http import MediaIoBaseDownload
    req = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    buf.seek(0)
    return Image.open(buf).convert("RGB")

def poll_google_drive_folder(service, folder_id: str) -> dict[str, Any] | None:
    query = (
        f"'{folder_id}' in parents and trashed=false and "
        f"(mimeType='image/png' or mimeType='image/jpeg' or mimeType='image/webp')"
    )
    res = service.files().list(
        q=query, orderBy="modifiedTime desc", pageSize=1,
        fields="files(id, name, modifiedTime)"
    ).execute()
    files = res.get("files", [])
    return files[0] if files else None

def scan_local_feed_folder() -> tuple[Path, str] | None:
    """Fallback / companion live watcher: checks agribot_feed/ for images."""
    if not FEED_DIR.exists():
        return None
    valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
    images = [p for p in FEED_DIR.iterdir() if p.suffix.lower() in valid_exts]
    if not images:
        return None
    images.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest = images[0]
    return latest, latest.name

def drive_sync_once() -> dict[str, Any]:
    """Performs a single sync check against Drive or Feed directory."""
    global state
    service = None
    try:
        service = get_drive_service()
    except Exception as e:
        print(f"⚠️ Drive service init notice: {e}")

    # 1. Try Google Drive API if available
    if service is not None and GDRIVE_FOLDER_ID:
        try:
            latest = poll_google_drive_folder(service, GDRIVE_FOLDER_ID)
            if latest:
                file_id, filename = latest["id"], latest["name"]
                with state_lock:
                    is_new = state["last_processed_file_id"] != file_id
                if is_new:
                    print(f"📥 [Drive] Downloading newly detected image: {filename} ({file_id})")
                    img = download_drive_file_media(service, file_id)
                    result = run_ai_inference(img, filename=filename, source="google_drive")
                    with state_lock:
                        state["last_processed_file_id"] = file_id
                        state["total_drive_images_processed"] += 1
                        state["drive_status"] = "connected"
                    return {"synced": True, "filename": filename, "result": result}
        except Exception as e:
            print(f"⚠️ Drive poller error: {e}")
            with state_lock:
                state["error"] = str(e)
                state["drive_status"] = "error"

    # 2. Check local companion feed directory (agribot_feed)
    feed_item = scan_local_feed_folder()
    if feed_item:
        img_path, filename = feed_item
        with state_lock:
            is_new = state["last_processed_file_id"] != filename
        if is_new:
            try:
                img = Image.open(img_path).convert("RGB")
                result = run_ai_inference(img, filename=filename, source="agribot_feed")
                with state_lock:
                    state["last_processed_file_id"] = filename
                    state["total_drive_images_processed"] += 1
                    state["drive_status"] = "active_feed"
                return {"synced": True, "filename": filename, "result": result}
            except Exception as e:
                print(f"⚠️ Feed error: {e}")

    with state_lock:
        if state["drive_status"] != "connected":
            state["drive_status"] = "monitoring"
    return {"synced": False, "message": "No new images detected"}

def drive_polling_thread():
    """Continuous background worker polling Google Drive."""
    print(f"🚀 [Drive Worker] Starting poller thread (Folder: {GDRIVE_FOLDER_ID}, Interval: {GDRIVE_POLL_INTERVAL}s)")
    while True:
        try:
            drive_sync_once()
        except Exception as e:
            print(f"⚠️ Drive background poller error: {e}")
        time.sleep(GDRIVE_POLL_INTERVAL)

# ─── Gemini AI Integration ──────────────────────────────────────────────────
CHAT_SYSTEM = """You are an expert agricultural plant pathologist and crop health consultant.
If the user's message is NOT about plants, crops, farming, agriculture, plant diseases, soil, fertilizers, irrigation, pests, or gardening, respond with EXACTLY this line:
I only answer plant and farming queries

If the question IS on-topic, provide practical, smallholder-farmer friendly advice formatted with these headings:
Cause:
Symptoms:
Prevention:
Treatment:"""

RECOMMENDATION_SYSTEM = """You are a senior plant pathologist. Provide actionable, concise disease management steps for smallholder farmers formatted in plain text with these exact headings:
Cause:
Symptoms:
Prevention:
Treatment:"""

# Cache for models, active model, and responses to drastically reduce latency
_GEMINI_MODEL_INSTANCES: dict[tuple[str, str], Any] = {}
_RECOMMENDATION_CACHE: dict[str, str] = {}
_CHAT_CACHE: dict[str, str] = {}
_ACTIVE_GEMINI_MODEL: str | None = None

def _gemini_model_names_to_try() -> list[str]:
    # Ultra-low-latency Flash Lite models prioritized first
    models = [
        "gemini-3.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.1-flash-lite",
        "gemini-3.6-flash",
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-3.7-flash",
    ]
    global _ACTIVE_GEMINI_MODEL
    if _ACTIVE_GEMINI_MODEL and _ACTIVE_GEMINI_MODEL in models:
        return [_ACTIVE_GEMINI_MODEL] + [m for m in models if m != _ACTIVE_GEMINI_MODEL]
    return models

def _gemini_generate(system_instruction: str, user_message: str, empty_message: str = "Could not generate reply.", max_tokens: int = 380) -> str:
    global _ACTIVE_GEMINI_MODEL
    try:
        import google.generativeai as genai
    except ImportError:
        return "Gemini AI library is not available. Please run: pip install google-generativeai"

    api_key = (os.environ.get("GEMINI_API_KEY", "").strip() or GEMINI_API_KEY_FALLBACK).strip()
    if not api_key:
        return "Gemini API key is not configured. Please add GEMINI_API_KEY in your .env file."

    genai.configure(api_key=api_key)
    last_err = None

    gen_config = genai.types.GenerationConfig(
        max_output_tokens=max_tokens,
        temperature=0.25,
        top_p=0.85
    )

    for model_name in _gemini_model_names_to_try():
        try:
            cache_key = (model_name, system_instruction)
            if cache_key in _GEMINI_MODEL_INSTANCES:
                model = _GEMINI_MODEL_INSTANCES[cache_key]
            else:
                model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
                _GEMINI_MODEL_INSTANCES[cache_key] = model

            response = model.generate_content(user_message, generation_config=gen_config)
            text = getattr(response, "text", "") or ""
            out = text.strip()
            if out:
                _ACTIVE_GEMINI_MODEL = model_name
                return out
        except Exception as exc:
            last_err = exc
            continue

    if last_err:
        return f"Gemini Error: {last_err}"
    return empty_message

# ─── Real-Time Analytics Helper ──────────────────────────────────────────────
def get_realtime_stats() -> dict[str, Any]:
    conn = get_db_connection()
    rows = conn.execute("SELECT disease, confidence_pct FROM predictions ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()

    total = len(rows)
    healthy = sum(1 for r in rows if "healthy" in (r["disease"] or "").lower())
    diseased = total - healthy
    avg_conf = round(sum(r["confidence_pct"] for r in rows) / total, 1) if total > 0 else 0.0
    rate = round((diseased / total) * 100.0, 1) if total > 0 else 0.0

    return {
        "total_analyzed": total,
        "healthy_count": healthy,
        "diseased_count": diseased,
        "disease_rate_pct": rate,
        "avg_confidence": avg_conf
    }

# ─── API Routes ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def api_health() -> Any:
    with state_lock:
        drv_st = state["drive_status"]
        tot_proc = state["total_drive_images_processed"]
    return jsonify({
        "status": "ok",
        "weights": WEIGHTS_PATH.name,
        "weightsPath": str(WEIGHTS_PATH),
        "model_trained": WEIGHTS_PATH.name != "yolov8n.pt",
        "drive_status": drv_st,
        "drive_folder_id": GDRIVE_FOLDER_ID,
        "total_drive_images": tot_proc
    })

@app.get("/api/drive/status")
def api_drive_status() -> Any:
    with state_lock:
        return jsonify({
            "status": state["drive_status"],
            "folder_id": state["drive_folder_id"],
            "polling_interval_sec": GDRIVE_POLL_INTERVAL,
            "last_processed_file_id": state["last_processed_file_id"],
            "last_processed_filename": state["last_processed_filename"],
            "last_processed_timestamp": state["last_processed_timestamp"],
            "total_processed": state["total_drive_images_processed"],
            "error": state["error"]
        })

@app.post("/api/drive/sync")
def api_drive_sync() -> Any:
    res = drive_sync_once()
    return jsonify(res)

@app.get("/api/latest-result")
def api_latest_result() -> Any:
    with state_lock:
        current = dict(state.get("latest_result") or {})
    if not current or not current.get("disease"):
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 1").fetchone()
            conn.close()
            if row:
                disease_name = row["disease"]
                sample_img = Image.new("RGB", (256, 256), color=(45, 110, 50))
                pest_res = PestDetectionAdapter.analyze(sample_img, disease_hint=disease_name)
                nutr_res = NutritionDeficiencyEngine.analyze(sample_img, disease_hint=disease_name)
                current = {
                    "success": True,
                    "detected": True,
                    "disease": disease_name,
                    "confidence": row["confidence_pct"],
                    "severity": row["severity_pct"],
                    "plantHealth": row["health_pct"],
                    "suggestion": row["recommendation"],
                    "annotatedImage": f"/static/uploads/{row['filename']}" if row["filename"] else None,
                    "pest_analysis": pest_res,
                    "nutrition_analysis": nutr_res,
                    "detections": [{
                        "disease": disease_name,
                        "confidence": row["confidence_pct"],
                        "severity": row["severity_pct"],
                    }],
                }
                with state_lock:
                    state["latest_result"] = current
        except Exception as e:
            print(f"⚠️ DB latest_result load error: {e}")
    current["stats"] = get_realtime_stats()
    return jsonify(current)

@app.post("/api/predict")
@app.post("/predict")
def api_predict() -> Any:
    body = request.get_json(silent=True) or {}
    image_data_url = str(body.get("imageDataUrl") or body.get("image") or body.get("imageData") or "").strip()
    conf = float(body.get("conf") or body.get("confidence") or 0.2)

    if not image_data_url:
        return jsonify({"error": "imageDataUrl is required"}), 400

    try:
        image = decode_data_url(image_data_url)
        filename = f"upload_{int(time.time())}.png"
        payload = run_ai_inference(image, filename=filename, source="upload", conf=conf)
        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/history")
def api_history() -> Any:
    limit = min(int(request.args.get("limit", 50)), 100)
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT id, created_at, disease, confidence_pct, severity_pct, health_pct, recommendation, source, filename
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()
    conn.close()

    return jsonify([
        {
            "id": row["id"],
            "createdAt": row["created_at"],
            "disease": row["disease"],
            "confidence": row["confidence_pct"],
            "severity": row["severity_pct"],
            "plantHealth": row["health_pct"],
            "suggestion": row["recommendation"],
            "source": row["source"],
            "filename": row["filename"]
        }
        for row in rows
    ])

@app.post("/api/diagnose/pest")
def api_diagnose_pest() -> Any:
    body = request.get_json(silent=True) or {}
    image_data_url = str(body.get("imageDataUrl") or body.get("image") or "").strip()
    disease_hint = str(body.get("disease") or "").strip()
    plant_hint = str(body.get("plant") or "").strip()
    if not image_data_url:
        return jsonify({"error": "imageDataUrl is required"}), 400
    try:
        img = decode_data_url(image_data_url)
        res = PestDetectionAdapter.analyze(img, disease_hint=disease_hint, plant_hint=plant_hint)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/api/diagnose/nutrition")
def api_diagnose_nutrition() -> Any:
    body = request.get_json(silent=True) or {}
    image_data_url = str(body.get("imageDataUrl") or body.get("image") or "").strip()
    disease_hint = str(body.get("disease") or "").strip()
    plant_hint = str(body.get("plant") or "").strip()
    if not image_data_url:
        return jsonify({"error": "imageDataUrl is required"}), 400
    try:
        img = decode_data_url(image_data_url)
        res = NutritionDeficiencyEngine.analyze(img, plant_hint=plant_hint, disease_hint=disease_hint)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/chat")
def api_chat() -> Any:
    body = request.get_json(silent=True) or {}
    msg = str(body.get("message", "")).strip()
    if not msg:
        return jsonify({"error": "message is required"}), 400

    cache_key = msg.lower()
    if cache_key in _CHAT_CACHE:
        return jsonify({"reply": _CHAT_CACHE[cache_key], "cached": True})

    reply = _gemini_generate(CHAT_SYSTEM, msg, max_tokens=350)
    clean_reply = reply.replace("\x00", "")
    if "Gemini Error" not in clean_reply and len(clean_reply) > 20:
        _CHAT_CACHE[cache_key] = clean_reply
    return jsonify({"reply": clean_reply})

@app.post("/api/recommendation")
def api_recommendation() -> Any:
    body = request.get_json(silent=True) or {}
    disease = str(body.get("disease", "")).strip()
    if not disease:
        return jsonify({"error": "disease is required"}), 400
    sev = float(body.get("severity", 0) or 0)
    health = float(body.get("plantHealth", 0) or 0)
    conf = float(body.get("confidence", 0) or 0)
    hint = str(body.get("staticHint", "") or "").strip()

    cache_key = f"{disease.lower()}_{round(sev/15)}_{round(health/15)}"
    if cache_key in _RECOMMENDATION_CACHE:
        return jsonify({"recommendation": _RECOMMENDATION_CACHE[cache_key], "cached": True})

    prompt = (
        f"Diagnosed Leaf Details:\n"
        f"- Disease: {disease}\n"
        f"- Confidence: {conf:.1f}%\n"
        f"- Estimated Severity: {sev:.1f}%\n"
        f"- Plant Health Index: {health:.1f}%\n"
        f"- Note: {hint}\n\n"
        "Provide concise, tailored treatment, cause, symptoms, and organic prevention for smallholder farmers."
    )
    rec = _gemini_generate(RECOMMENDATION_SYSTEM, prompt, max_tokens=380)
    clean_rec = rec.replace("\x00", "")
    if "Gemini Error" not in clean_rec and len(clean_rec) > 20:
        _RECOMMENDATION_CACHE[cache_key] = clean_rec
    return jsonify({"recommendation": clean_rec})

@app.get("/weather")
def api_weather() -> Any:
    city = request.args.get("city", "").strip()
    lat = request.args.get("lat", "").strip()
    lon = request.args.get("lon", "").strip()

    if not city and not (lat and lon):
        if "text/html" in request.headers.get("Accept", ""):
            if (FRONTEND_DIST / "index.html").exists():
                return send_from_directory(FRONTEND_DIST, "index.html")
            if (PLANT_DASHBOARD_STATIC / "index.html").exists():
                return send_from_directory(PLANT_DASHBOARD_STATIC, "index.html")
        return jsonify({"error": "Query parameter required: city or lat & lon"}), 400

    api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        return jsonify({
            "error": "Missing OPENWEATHER_API_KEY in .env file. Add your key from https://openweathermap.org/api"
        }), 503

    if lat and lon:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={urllib.parse.quote(lat)}&lon={urllib.parse.quote(lon)}&appid={api_key}&units=metric"
    else:
        q = urllib.parse.quote(city)
        url = f"https://api.openweathermap.org/data/2.5/weather?q={q}&appid={api_key}&units=metric"

    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"OpenWeather error: {e.code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    main = payload.get("main", {})
    wx = (payload.get("weather") or [{}])[0]
    rain = float((payload.get("rain") or {}).get("1h", 0.0))
    temp = float(main.get("temp", 25.0))
    hum = int(main.get("humidity", 50))

    tips = []
    if rain >= 5.0:
        tips.append("Heavy rain alert: Avoid chemical spraying; ensure drainage furrows are open to prevent fungal root collar rot.")
    elif rain <= 0.2 and temp >= 30.0:
        tips.append("Hot, dry conditions: Apply drip or morning furrow irrigation; delay foliar sprays until evening to avoid phytotoxicity.")
    if hum >= 80:
        tips.append("High ambient humidity: High risk of fungal spores germination. Scout for early blight and leaf spots.")
    if not tips:
        tips.append("Favorable conditions for routine foliar maintenance and protective bio-fungicide sprays.")

    resolved_name = payload.get("name") or (f"Lat: {lat}, Lon: {lon}" if lat and lon else city)

    return jsonify({
        "city": resolved_name,
        "coord": payload.get("coord", {}),
        "description": str(wx.get("description", "")).title(),
        "temp_c": round(temp, 1),
        "humidity": hum,
        "rain_mm": round(rain, 2),
        "farming_tip": " ".join(tips)
    })

# ─── Authentication Endpoints ───────────────────────────────────────────────
def hash_pwd(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@app.post("/api/auth/signup")
def api_signup() -> Any:
    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "")).strip()
    email = str(body.get("email", "")).strip().lower()
    pwd = str(body.get("password", "")).strip()

    if not name or not email or not pwd:
        return jsonify({"error": "Name, email and password are required"}), 400
    if len(pwd) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    conn = get_db_connection()
    if conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
        conn.close()
        return jsonify({"error": "Email already registered"}), 409

    conn.execute(
        "INSERT INTO users (created_at, name, email, password_hash) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), name, email, hash_pwd(pwd)),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Signup successful"})

@app.post("/api/auth/login")
def api_login() -> Any:
    body = request.get_json(silent=True) or {}
    email = str(body.get("email", "")).strip().lower()
    pwd = str(body.get("password", "")).strip()

    if not email or not pwd:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user or user["password_hash"] != hash_pwd(pwd):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    })

# ─── Static Assets & Frontend Catch-All ─────────────────────────────────────
@app.get("/")
def index_route() -> Any:
    if (FRONTEND_DIST / "index.html").exists():
        return send_from_directory(FRONTEND_DIST, "index.html")
    if (PLANT_DASHBOARD_STATIC / "index.html").exists():
        return send_from_directory(PLANT_DASHBOARD_STATIC, "index.html")
    if (ASSISTANT_DIR / "index.html").exists():
        return send_from_directory(ASSISTANT_DIR, "index.html")
    return jsonify({
        "message": "PlantVision AI Backend running.",
        "endpoints": ["/api/health", "/api/drive/status", "/api/latest-result", "/api/history"]
    })

@app.get("/<path:path>")
def static_proxy(path: str) -> Any:
    if path.startswith("api/"):
        return jsonify({"error": "Endpoint not found"}), 404

    for base in [FRONTEND_DIST, PLANT_DASHBOARD_STATIC, ASSISTANT_DIR]:
        target = base / path
        if target.is_file():
            return send_from_directory(base, path)

    if (FRONTEND_DIST / "index.html").exists():
        return send_from_directory(FRONTEND_DIST, "index.html")
    if (PLANT_DASHBOARD_STATIC / "index.html").exists():
        return send_from_directory(PLANT_DASHBOARD_STATIC, "index.html")
    return jsonify({"error": "Not found"}), 404

# ─── Main Startup ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    # Start Google Drive polling daemon thread
    t = threading.Thread(target=drive_polling_thread, daemon=True)
    t.start()

    port = int(os.environ.get("PORT", 5000))
    print(f"🌿 PlantVision AI platform server running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
