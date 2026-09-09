import nbformat
import glob
import os
import uuid

notebooks_order = [
    "01_satellite_eda.ipynb",
    "02_satellite_training.ipynb",
    "03_nlp_eda.ipynb",
    "04_nlp_training.ipynb",
    "05_forecasting_eda.ipynb",
    "06_forecasting_training.ipynb"
]

base_dir = "d:/MyProjectsForFun/disaster intelligence/notebooks"

# Create a new blank notebook
master_nb = nbformat.v4.new_notebook()

# Add a Master Title cell and drive mounting instructions
title_cell = nbformat.v4.new_markdown_cell(
    source="# 🌍 AI Disaster Intelligence Platform — Master Training Notebook\n\nThis notebook contains the complete end-to-end Exploratory Data Analysis (EDA) and Training pipelines for all three machine learning models: Satellite Imagery (EfficientNet), NLP (DistilBERT), and Weather Forecasting (XGBoost).\n\nEnsure you have your dataset uploaded to your Google Drive at `My Drive/disaster intelligence/data/`."
)
title_cell['id'] = str(uuid.uuid4())[:8]

mount_cell = nbformat.v4.new_code_cell(
    source="# ── Mount Google Drive ──────────────────────────────────────────\nfrom google.colab import drive\ndrive.mount('/content/drive')"
)
mount_cell['id'] = str(uuid.uuid4())[:8]

master_nb.cells.extend([title_cell, mount_cell])

for idx, nb_name in enumerate(notebooks_order):
    nb_path = os.path.join(base_dir, nb_name)
    if not os.path.exists(nb_path):
        print(f"Warning: {nb_name} not found.")
        continue
        
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
        
    # Chapter Title formatting
    chapter_title = nb_name.replace('.ipynb', '').replace('_', ' ').title()
    # E.g., "01 Satellite Eda" -> "Chapter 1: Satellite EDA"
    chapter_title_text = f"## Chapter {idx + 1}: {chapter_title[3:]}"
    
    chapter_cell = nbformat.v4.new_markdown_cell(source=f"---\n{chapter_title_text}")
    chapter_cell['id'] = str(uuid.uuid4())[:8]
    master_nb.cells.append(chapter_cell)
    
    # Append all cells from the notebook, skipping redundant drive mounts
    for cell in nb.cells:
        # Give a new ID to avoid duplicates
        cell['id'] = str(uuid.uuid4())[:8]
        
        # Skip redundant google drive mount cells inside the chapters
        if cell.cell_type == 'code' and 'drive.mount' in cell.source and 'from google.colab' in cell.source:
            continue
            
        master_nb.cells.append(cell)

output_path = os.path.join(base_dir, "00_master_training_pipeline.ipynb")
with open(output_path, 'w', encoding='utf-8') as f:
    nbformat.write(master_nb, f)

print(f"Successfully merged all 6 notebooks into {output_path}")
