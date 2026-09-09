import nbformat
import glob
import os
import uuid

notebooks_order = [
    ("01_satellite_eda.ipynb", "Part 1.1: Satellite Imagery (Deep Learning - Computer Vision) — EDA"),
    ("02_satellite_training.ipynb", "Part 1.2: Satellite Model Training (EfficientNet-B0)"),
    ("03_nlp_eda.ipynb", "Part 2.1: Disaster Tweets (Deep Learning - NLP) — EDA"),
    ("04_nlp_training.ipynb", "Part 2.2: NLP Model Fine-Tuning (DistilBERT)"),
    ("05_forecasting_eda.ipynb", "Part 3.1: Weather & Risk Forecasting (Machine Learning) — EDA"),
    ("06_forecasting_training.ipynb", "Part 3.2: Weather Model Training (XGBoost)")
]

base_dir = "d:/MyProjectsForFun/disaster intelligence/notebooks"

master_nb = nbformat.v4.new_notebook()

# 1. Setup Markdown
md_setup = """# 🌍 AI Disaster Intelligence Platform — Master Training Pipeline

This notebook contains the complete, end-to-end Deep Learning and Machine Learning pipelines for the **Terra-Aura Disaster Intelligence Platform**. 

### 🚀 Foolproof Execution Guide
1. **Google Colab Runtime:** Ensure you are running this in Google Colab with a **T4 GPU** enabled (`Runtime -> Change runtime type -> Hardware accelerator -> T4 GPU`).
2. **Google Drive Sync:** Ensure you have uploaded the `disaster intelligence` folder structure exactly to the root of your Google Drive (`My Drive/disaster intelligence/`).
3. **Run All:** Simply go to `Runtime -> Run all` and the notebook will automatically handle the rest!
"""
cell_md = nbformat.v4.new_markdown_cell(source=md_setup)
cell_md['id'] = str(uuid.uuid4())[:8]

# 2. Unified Install Cell
code_install = """# ── 1. Environment Setup & Dependency Installation ──────────────────
# This cell installs all required libraries across all models at once.
!pip install -q torch torchvision efficientnet_pytorch transformers datasets scikit-learn pandas numpy matplotlib seaborn xgboost
print("✅ All dependencies installed.")
"""
cell_install = nbformat.v4.new_code_cell(source=code_install)
cell_install['id'] = str(uuid.uuid4())[:8]

# 3. Mount Drive & Validate Paths & Check GPU
code_validate = """# ── 2. Hardware Check & Path Validation ───────────────────────────
import os
import torch
from google.colab import drive

# 1. Mount Google Drive
drive.mount('/content/drive')

# 2. Check GPU Availability
print("\\n--- HARDWARE CHECK ---")
if torch.cuda.is_available():
    print(f"✅ GPU detected: {torch.cuda.get_device_name(0)}")
else:
    print("❌ WARNING: No GPU detected! Deep Learning models (EfficientNet & DistilBERT) will take hours to train on CPU.")
    print("👉 Action: Go to 'Runtime' -> 'Change runtime type' -> Select 'T4 GPU'.")

# 3. Validate Google Drive Path Structure
print("\\n--- PATH VALIDATION ---")
PROJECT_ROOT = "/content/drive/MyDrive/disaster intelligence"

required_paths = [
    f"{PROJECT_ROOT}/data/raw/satellite",
    f"{PROJECT_ROOT}/data/raw/tweets/disaster_tweets.csv",
    f"{PROJECT_ROOT}/data/raw/weather/global_disaster_events.csv",
    f"{PROJECT_ROOT}/models"
]

all_paths_ok = True
for path in required_paths:
    if not os.path.exists(path):
        print(f"❌ MISSING: {path}")
        all_paths_ok = False
    else:
        print(f"✅ FOUND: {path}")

if not all_paths_ok:
    raise FileNotFoundError("One or more critical paths are missing. Please ensure you uploaded the folder exactly as instructed to 'My Drive/disaster intelligence/'.")
else:
    print("\\n🚀 All checks passed! Proceeding to Model Pipelines...")
"""
cell_validate = nbformat.v4.new_code_cell(source=code_validate)
cell_validate['id'] = str(uuid.uuid4())[:8]

master_nb.cells.extend([cell_md, cell_install, cell_validate])

# 4. Append Sub-Notebooks
for nb_name, title in notebooks_order:
    nb_path = os.path.join(base_dir, nb_name)
    if not os.path.exists(nb_path):
        print(f"Warning: {nb_name} not found.")
        continue
        
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
        
    chapter_cell = nbformat.v4.new_markdown_cell(source=f"---\n## {title}")
    chapter_cell['id'] = str(uuid.uuid4())[:8]
    master_nb.cells.append(chapter_cell)
    
    for cell in nb.cells:
        cell['id'] = str(uuid.uuid4())[:8]
        
        # Skip old titles and manual upload instructions
        if cell.cell_type == 'markdown' and 'Dataset Upload Instructions' in cell.source:
            continue
        if cell.cell_type == 'markdown' and cell.source.startswith('# '):
            continue
            
        if cell.cell_type == 'code':
            # Remove pip install lines without deleting the whole cell
            if '!pip install' in cell.source:
                new_lines = [line for line in cell.source.split('\\n') if not line.strip().startswith('!pip install')]
                cell.source = '\\n'.join(new_lines)
            
            # Remove redundant drive mounting lines without deleting the whole cell
            if 'from google.colab import drive' in cell.source:
                new_lines = []
                for line in cell.source.split('\\n'):
                    if 'from google.colab import drive' in line or "drive.mount" in line:
                        continue
                    new_lines.append(line)
                cell.source = '\\n'.join(new_lines)
            
            # Ensure the cell is not empty after stripping
            if not cell.source.strip():
                continue
            
        master_nb.cells.append(cell)

output_path = os.path.join(base_dir, "00_master_training_pipeline.ipynb")
with open(output_path, 'w', encoding='utf-8') as f:
    nbformat.write(master_nb, f)

print(f"Successfully generated fixed foolproof master notebook at {output_path}")
