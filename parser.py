import fitz  # PyMuPDF
import os
from pathlib import Path

def extract_text_and_figures(pdf_path: str, out_dir: str):
    """Extract text and figures from PDF, save figures as PNG."""
    doc = fitz.open(pdf_path)
    text_chunks = []
    figure_paths = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        text_chunks.append({
            "page": page_num,
            "text": text
        })
        # Extract figures
        images = page.get_images(full=True)
        for i, img in enumerate(images):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            fig_path = Path(out_dir) / f"fig_page{page_num}_{i}.png"
            pix.save(str(fig_path))
            figure_paths.append(str(fig_path))
    return text_chunks, figure_paths
