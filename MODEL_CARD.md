# 🌿 Model Card: PlantVision AI Foliar Pathology Detector

> **Model Identifier**: `plantvision-yolov8n-foliar`  
> **Model Weights File**: `best.pt` (6.22 MB)  
> **Base Architecture**: Ultralytics YOLOv8 Nano (`yolov8n.pt`)  
> **Target Task**: Real-Time Multi-Class Plant Disease & Leaf Object Detection  
> **Release Date**: September 2026  
> **Framework**: PyTorch / Ultralytics  

---

## 1. Model Overview & Architecture

This model is a real-time object detection convolutional neural network based on the **YOLOv8 Nano** architecture, trained to identify, locate, and classify foliar plant diseases across major agricultural crops.

- **Parameters**: ~3.01 Million
- **GFLOPs**: ~8.2 GFLOPs @ 640x640 resolution
- **Inference Speed**: ~18–25 ms on CPU, ~2–4 ms on NVIDIA GPU
- **Input Resolution**: 640 × 640 RGB (dynamic scaling supported down to 320 × 320)
- **Output Format**: Multi-class bounding boxes $[x_1, y_1, x_2, y_2]$, confidence score $[0.0 - 1.0]$, and class index $[0 - 29]$.

---

## 2. Training Dataset Specification

The model architecture supports three modular dataset configurations:
- **PlantDoc Dataset** ([`data_plantdoc.yaml`](./data_plantdoc.yaml)):
  - **Total**: 2,567 real-world field images with multi-lesion bounding boxes across 30 foliar disease classes.
  - **Splits**: 1,979 train, 349 validation, 239 test.
- **PlantVillage Dataset** ([`data_plantvillage.yaml`](./data_plantvillage.yaml)):
  - **Total**: 20,638 high-resolution leaf images across 15 agricultural classes (Pepper, Potato, Tomato).
  - **Splits**: 16,504 train, 4,134 validation.
- **Combined Unified Dataset** ([`data_combined.yaml`](./data_combined.yaml)):
  - **Total**: 7,380 images across 31 unified disease and healthy foliage classes.
  - **Splits**: 6,020 train, 1,360 validation. Merges field complexity with laboratory depth.

### 30 Evaluated Foliar Classes

| ID | Class Name | Target Crop | Pathology Type |
| :--- | :--- | :--- | :--- |
| `0` | **Apple Scab Leaf** | Apple | Fungal (*Venturia inaequalis*) |
| `1` | **Apple leaf** | Apple | Healthy Foliage |
| `2` | **Apple rust leaf** | Apple | Fungal (*Gymnosporangium*) |
| `3` | **Bell_pepper leaf spot** | Bell Pepper | Bacterial / Fungal Spot |
| `4` | **Bell_pepper leaf** | Bell Pepper | Healthy Foliage |
| `5` | **Blueberry leaf** | Blueberry | Healthy Foliage |
| `6` | **Cherry leaf** | Cherry | Healthy Foliage |
| `7` | **Corn Gray leaf spot** | Corn / Maize | Fungal (*Cercospora zeae-maydis*) |
| `8` | **Corn leaf blight** | Corn / Maize | Fungal (*Exserohilum turcicum*) |
| `9` | **Corn rust leaf** | Corn / Maize | Fungal (*Puccinia sorghi*) |
| `10` | **Peach leaf** | Peach | Foliar Leaf State |
| `11` | **Potato leaf early blight** | Potato | Fungal (*Alternaria solani*) |
| `12` | **Potato leaf late blight** | Potato | Oomycete (*Phytophthora infestans*) |
| `13` | **Potato leaf** | Potato | Healthy Foliage |
| `14` | **Raspberry leaf** | Raspberry | Healthy Foliage |
| `15` | **Soyabean leaf** | Soybean | Foliar Leaf State |
| `16` | **Soybean leaf** | Soybean | Foliar Leaf State |
| `17` | **Squash Powdery mildew leaf**| Squash / Cucurbit | Fungal (*Podosphaera*) |
| `18` | **Strawberry leaf** | Strawberry | Foliar Leaf State |
| `19` | **Tomato Early blight leaf** | Tomato | Fungal (*Alternaria solani*) |
| `20` | **Tomato Septoria leaf spot** | Tomato | Fungal (*Septoria lycopersici*) |
| `21` | **Tomato leaf bacterial spot**| Tomato | Bacterial (*Xanthomonas*) |
| `22` | **Tomato leaf late blight** | Tomato | Oomycete (*Phytophthora infestans*) |
| `23` | **Tomato leaf mosaic virus** | Tomato | Viral (ToMV) |
| `24` | **Tomato leaf yellow virus** | Tomato | Viral (TYLCV) |
| `25` | **Tomato leaf** | Tomato | Healthy Foliage |
| `26` | **Tomato mold leaf** | Tomato | Fungal (*Passalora fulva*) |
| `27` | **Tomato two spotted spider mites leaf** | Tomato | Pest Vector Damage (*Tetranychidae*) |
| `28` | **grape leaf black rot** | Grape | Fungal (*Guignardia bidwellii*) |
| `29` | **grape leaf** | Grape | Healthy Foliage |

---

## 3. Tri-Engine Pipeline Integration

In the PlantVision AI platform, `best.pt` does not operate in isolation. It anchors the **Tri-Engine Diagnostic Suite**:

1. **Pathology Localization (YOLOv8)**: Detects lesion bounding boxes, computes infected surface area percentage, and derives the **Plant Health Index** ($100\% - \text{Infected Area}$).
2. **Pest Vector Correlation (`pest_adapter.py`)**: Computer vision filters evaluate chlorotic stippling (sap-sucking pests) and puncture flecks, recommending biological biocontrols and chemical IPM dilutions.
3. **Nutrient Deficiency Analytics (`nutrition_engine.py`)**: Analyzes 4 spectral canopy indices across 7 elements (N, P, K, Mg, Fe, Ca, Zn) and formulates foliar spray recipes.

---

## 4. Evaluation & Diagnostic Plots

Training metrics and validation curves are preserved in the repository under [`runs/detect/train/`](./runs/detect/train/):

- **Precision-Recall Curve**: `runs/detect/train/BoxPR_curve.png`
- **F1-Confidence Curve**: `runs/detect/train/BoxF1_curve.png`
- **Confusion Matrix**: `runs/detect/train/confusion_matrix.png`
- **Loss Curves & mAP**: `runs/detect/train/results.png` & `results.csv`
- **Validation Batch Ground Truth vs Prediction**: `runs/detect/train/val_batch0_labels.jpg` vs `val_batch0_pred.jpg`

---

## 5. How an Expert Can Verify / Audit This Model

An expert can test this model locally in three steps:

### A. Run CLI Inference on Any Leaf Image
```powershell
python run_model.py --source "datasets/plantdoc/test/images/<image_name>.jpg"
```

### B. Evaluate Model Metrics on the Full Test Set
```powershell
yolo detect val model=best.pt data=data_plantdoc.yaml split=test
```

### C. Inspect Programmatically in Python
```python
from ultralytics import YOLO

# Load model
model = YOLO("best.pt")

# Print architecture summary
model.info()

# Run inference
results = model.predict("datasets/plantdoc/test/images/sample.jpg", conf=0.25)
for box in results[0].boxes:
    print(f"Detected {model.names[int(box.cls)]} with confidence {float(box.conf):.2f}")
```

---

## 6. Recommendations & Scaling Notes for Production

- **Current Stage**: The current `best.pt` has been validated through the complete training and end-to-end inference pipeline.
- **Production Retraining**: For final production deployment with maximal mAP, execute 50–100 epochs on a GPU using:
  ```powershell
  python train_yolo.py --dataset plantdoc --epochs 50 --imgsz 640 --device 0
  ```
  Or via the provided Google Colab notebook [`PlantDoc_YOLOv8_Colab.ipynb`](./PlantDoc_YOLOv8_Colab.ipynb).
