# Specification: PlantVision AI ML Model Extraction & Packaging

## 1. Overview
The goal is to extract and bundle all assets, code, configurations, evaluation data, and sample test images for the PlantVision AI Machine Learning models into a dedicated, self-contained directory (`plantvision_ml_bundle/`). Each asset will be documented with clear descriptions explaining its role, architecture specifications, dataset mapping, and verification procedures.

## 2. Directory Architecture
The extracted bundle will be organized into logical subdirectories under `plantvision_ml_bundle/`:

```
plantvision_ml_bundle/
├── README.md                          # Master documentation explaining all bundle contents & usage
├── MODEL_CARD.md                      # Scientific audit specification covering all 30 foliar classes
├── requirements.txt                   # Isolated Python dependencies for inference & evaluation
├── quick_test.py                      # Ready-to-run 1-command verification script
│
├── weights/                           # Model checkpoints & tensor specs
│   ├── best.pt                        # Fine-tuned YOLOv8n weights (~6.2 MB)
│   ├── yolov8n.pt                     # Base pretrained YOLOv8n checkpoint
│   └── README.md                      # Detailed descriptions of weights, shapes, and export options
│
├── inference/                         # Production-ready inference and Tri-Engine suite
│   ├── run_model.py                   # CLI inference runner with multi-engine diagnostic output
│   ├── pest_adapter.py                # Pest vector chlorotic stippling analysis & biocontrols
│   ├── nutrition_engine.py            # 7-element canopy nutrient deficiency analytics
│   ├── predict.py                     # Standalone detection and bounding box visualizer
│   └── README.md                      # Descriptions and API usage for inference modules
│
├── configs/                           # Dataset class and split configurations
│   ├── data_combined.yaml             # Combined PlantDoc + PlantVillage configuration
│   ├── data_plantdoc.yaml             # PlantDoc field dataset configuration
│   ├── data_plantvillage.yaml         # PlantVillage laboratory dataset configuration
│   ├── classes_mapping.txt            # Index to human-readable pathology class mapping
│   └── README.md                      # Descriptions of dataset structures and classes
│
├── training/                          # Training pipelines & notebooks
│   ├── train_yolo.py                  # Multi-dataset automated training script
│   ├── PlantDoc_YOLOv8_Colab.ipynb    # Google Colab T4 training notebook (PlantDoc)
│   ├── YOLOv8_PlantVillage_T4_Training.ipynb # High-res leaf training notebook (PlantVillage)
│   └── README.md                      # Training reproduction guide & hyperparameter notes
│
├── evaluation/                        # Performance curves & metric reports
│   ├── model_evaluation_report.txt    # Textual evaluation report and class breakdown
│   ├── results.csv                    # Epoch-by-epoch training and validation metrics
│   ├── results.png                    # Loss and mAP curve charts
│   ├── BoxPR_curve.png                # Precision-Recall curve
│   ├── BoxF1_curve.png                # F1 score vs confidence curve
│   ├── confusion_matrix.png           # Raw confusion matrix
│   ├── confusion_matrix_normalized.png # Normalized confusion matrix
│   ├── labels.jpg                     # Class distribution visualization
│   └── README.md                      # Descriptions of evaluation plots and metric interpretation
│
└── sample_images/                     # Sample leaf images for instant testing
    ├── README.md                      # Metadata for each sample (expected diagnosis & crop)
    └── (5-8 representative test images copied from test datasets)
```

## 3. Component Details & Descriptions

### A. Model Weights (`weights/`)
- `best.pt`: The fine-tuned weights file resulting from training YOLOv8n on the agricultural leaf datasets.
- `yolov8n.pt`: The initial pre-trained base model.
- `weights/README.md`: Explains model architecture (YOLOv8 Nano, 3.01M parameters, input resolution 640x640, output tensor format `[x1, y1, x2, y2, conf, class_id]`, conversion commands to ONNX/TensorRT/CoreML).

### B. Inference Engine (`inference/`)
- `run_model.py`: Orchestrates the Tri-Engine diagnostic suite:
  1. YOLOv8 foliar pathology detection and bounding box severity calculation.
  2. Pest damage chlorotic stippling analysis (`pest_adapter.py`).
  3. Canopy nutrient deficiency indexing across 7 elements (`nutrition_engine.py`).
- Self-contained import handling so scripts can run both inside `inference/` and via `quick_test.py` at bundle root.

### C. Dataset Configurations (`configs/`)
- `data_combined.yaml`, `data_plantdoc.yaml`, `data_plantvillage.yaml`: Complete YAML files specifying path roots, train/val/test splits, number of classes (`nc`), and class name arrays.
- `classes_mapping.txt`: Canonical index-to-class list for indexing predictions.
- `configs/README.md`: Summary of datasets, class distributions, and labeling formats.

### D. Training & Notebooks (`training/`)
- `train_yolo.py`: Standalone CLI trainer with support for `--dataset combined|plantdoc|plantvillage`, `--epochs`, `--batch-size`, and `--imgsz`.
- Notebooks for reproducing training in cloud environments (Google Colab / Kaggle).

### E. Evaluation Metrics & Charts (`evaluation/`)
- Copies of `BoxPR_curve.png`, `BoxF1_curve.png`, `confusion_matrix.png`, `results.png`, `results.csv`, and `model_evaluation_report.txt`.
- `evaluation/README.md`: Guide explaining how to interpret the curves (precision, recall, mAP@0.5, mAP@0.5:0.95) and diagnosis of common edge cases.

### F. Sample Images & Quick Test Runner (`sample_images/` & `quick_test.py`)
- Selected test images representing diverse crops (Apple, Potato, Tomato, Bell Pepper, Corn) with both healthy and diseased leaves.
- `quick_test.py`: Simple runner that loads `weights/best.pt`, processes the sample images, prints detections and disease diagnoses, and saves annotated output images into an `output/` folder.

## 4. Verification Plan
1. Validate file extraction: Confirm all required files exist in their respective directories.
2. Execute `quick_test.py` from within `plantvision_ml_bundle/`:
   - Verify `weights/best.pt` loads without errors.
   - Verify sample images are detected with predicted bounding boxes and classes.
   - Confirm output annotations are saved.
3. Validate documentation completeness: Ensure each subdirectory has a clear `README.md` and the root `README.md` and `MODEL_CARD.md` provide complete guidance.
