"""
extractor.py
------------
Handles extraction of text and images from PDF files.
Works with both Inspection Report and Thermal Images PDF.
"""

import fitz  # PyMuPDF
import os
from PIL import Image
import io


def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                full_text += f"\n\n--- PAGE {page_num + 1} ---\n"
                full_text += text
        doc.close()
        return full_text.strip()
    except Exception as e:
        return f"ERROR reading PDF: {str(e)}"


def extract_images_from_pdf(pdf_path: str, output_folder: str,
                             prefix: str = "img", max_images: int = 10) -> list:
    """
    Extract up to max_images representative images from a PDF.
    Picks one best image per page rather than dumping everything.
    """
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    seen_xrefs = set()

    for page_num in range(len(doc)):
        if len(image_paths) >= max_images:
            break

        page = doc[page_num]
        image_list = page.get_images(full=True)

        # Pick the largest image on this page (most likely the real photo)
        best = None
        best_size = 0
        for img in image_list:
            xref = img[0]
            if xref in seen_xrefs:
                continue
            try:
                base_image = doc.extract_image(xref)
                size = len(base_image["image"])
                if size < 8000:   # skip tiny icons
                    continue
                if size > best_size:
                    best_size = size
                    best = (xref, base_image)
            except Exception:
                continue

        if best:
            xref, base_image = best
            seen_xrefs.add(xref)
            ext = base_image["ext"]
            img_filename = f"{prefix}_page{page_num + 1}.{ext}"
            img_path = os.path.join(output_folder, img_filename)
            with open(img_path, "wb") as f:
                f.write(base_image["image"])
            image_paths.append(img_path)

    doc.close()
    return image_paths


def extract_all(inspection_pdf: str, thermal_pdf: str,
                image_output_folder: str = "output/images") -> dict:
    """
    Master function: Extract everything from both PDFs.
    Limits to 8 inspection images + 8 thermal images (16 total max).
    """
    print("📖 Extracting text from Inspection Report...")
    inspection_text = extract_text_from_pdf(inspection_pdf)

    print("🌡️ Extracting text from Thermal Report...")
    thermal_text = extract_text_from_pdf(thermal_pdf)

    print("📸 Extracting images from Inspection Report (max 8)...")
    inspection_images = extract_images_from_pdf(
        inspection_pdf, image_output_folder, prefix="inspection", max_images=8
    )

    print("🔥 Extracting images from Thermal Report (max 8)...")
    thermal_images = extract_images_from_pdf(
        thermal_pdf, image_output_folder, prefix="thermal", max_images=8
    )

    print(f"✅ Done! {len(inspection_images)} inspection + {len(thermal_images)} thermal images")

    return {
        "inspection_text": inspection_text,
        "thermal_text": thermal_text,
        "inspection_images": inspection_images,
        "thermal_images": thermal_images,
        "all_images": inspection_images + thermal_images
    }
