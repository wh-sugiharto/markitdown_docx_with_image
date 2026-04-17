#!/usr/bin/env python3
"""
markitdownimage - Convert DOCX to Markdown using MarkItDown and extract embedded images.
Input:  DOCX file
Output: output.md + images extracted to 'images/' folder

Dua strategi pemulihan gambar:
  1. extract_docx_images   : ekstrak langsung dari DOCX ZIP (word/media/) dan
                             cocokkan ke posisi placeholder di markdown
  2. recover_legacy_images : referensi teks '(Dirujuk dari file ...)' 
                             -> dicari dari folder legacy (fallback)
"""

import os
import re
import sys
import shutil
import zipfile
import argparse
from pathlib import Path
from markitdown import MarkItDown


# ──────────────────────────────────────────────────────────────────────────────
# Strategi 1: Ekstrak gambar dari DOCX ZIP → cocokkan ke placeholder markdown
# ──────────────────────────────────────────────────────────────────────────────

def extract_docx_images(docx_path: Path, images_dir: Path) -> dict:
    """
    Mengekstrak semua file dari word/media/ di dalam DOCX (format ZIP).
    Mengembalikan dict {urutan_index: path_file} dimulai dari 1.

    Nama file asli di DOCX (image1.png, image2.png, dst) dipertahankan,
    tapi juga diberi rename ke figure_01.png, figure_02.png untuk konsistensi.
    """
    images_dir.mkdir(parents=True, exist_ok=True)

    extracted = {}  # { i: Path }

    with zipfile.ZipFile(docx_path) as z:
        # Ambil semua file di word/media/
        media_files = sorted(
            [f for f in z.namelist() if f.startswith("word/media/")],
            key=lambda x: x  # sort by name
        )

        if not media_files:
            print("[~] No embedded media found in DOCX.")
            return extracted

        # Urutkan berdasarkan nomor angka di nama file (image1, image2, dst)
        def sort_key(name):
            nums = re.findall(r'\d+', Path(name).stem)
            return int(nums[0]) if nums else 0

        media_files.sort(key=sort_key)

        for i, member in enumerate(media_files, start=1):
            orig_name = Path(member).name
            ext       = Path(member).suffix.lower()
            new_name  = f"figure_{i:02d}{ext}"
            dest      = images_dir / new_name

            with z.open(member) as src, open(dest, "wb") as dst:
                shutil.copyfileobj(src, dst)

            extracted[i] = dest
            size_kb = dest.stat().st_size / 1024
            print(f"[+] Extracted: {orig_name} → {new_name}  ({size_kb:.1f} KB)")

    return extracted


def replace_base64_placeholders(markdown_text: str, extracted: dict) -> str:
    """
    Mengganti semua placeholder '![](data:image/...;base64...)' di markdown
    dengan link relatif ke file yang sudah diekstrak, secara berurutan.

    Placeholder muncul karena MarkItDown versi lama memotong data base64.
    Kita ganti satu per satu sesuai urutan kemunculan.
    """
    # Pola untuk menangkap placeholder base64 (inkl. yang sudah truncate jadi '...')
    pattern = re.compile(
        r'!\[([^\]]*)\]\(data:image/[^\)]+\)',
        re.DOTALL
    )

    image_index = [1]  # Gunakan list agar bisa dimodifikasi di dalam closure

    def replacer(match):
        i        = image_index[0]
        alt_text = match.group(1).strip()

        if i in extracted:
            rel_path = f"images/{extracted[i].name}"
            label    = alt_text if alt_text else extracted[i].name
            image_index[0] += 1
            return f"![{label}]({rel_path})"
        else:
            # Lebih banyak placeholder dari gambar yang ada
            print(f"[!] No image for placeholder #{i} (no matching extracted file)")
            image_index[0] += 1
            return match.group(0)  # Kembalikan aslinya

    new_text = pattern.sub(replacer, markdown_text)

    replaced = image_index[0] - 1
    print(f"[=] Replaced {replaced} placeholder(s) with image links.")
    return new_text


# ──────────────────────────────────────────────────────────────────────────────
# Strategi 2: Pulihkan gambar dari referensi teks legacy (Dirujuk dari file …)
# ──────────────────────────────────────────────────────────────────────────────

def recover_legacy_images(markdown_text: str, images_dir: Path, legacy_dirs: list) -> str:
    """
    Mencari referensi teks '(Dirujuk dari file filename.ext)',
    mencari file tersebut di direktori legacy, lalu menyalinnya ke images_dir.
    """
    pattern = re.compile(r'\(Dirujuk dari file\s+([^\)]+)\)', re.IGNORECASE)

    def replacer(match):
        original_ref = match.group(1).strip()
        desired_name = original_ref.replace(r"\_", "_").strip()
        desired_path = Path(desired_name)
        name_stem    = desired_path.stem
        desired_ext  = desired_path.suffix.lower()

        found_path = None
        for search_dir in legacy_dirs:
            candidates = list(search_dir.glob(desired_name))
            if not candidates:
                potential  = list(search_dir.glob(f"{name_stem}.*"))
                candidates = [p for p in potential if p.stem == name_stem]
            if candidates:
                def score(p):
                    s = 0
                    if p.name == desired_name:                                         s += 100
                    if p.suffix.lower() == desired_ext:                                s += 50
                    if desired_ext in ['.png', '.jpg', '.jpeg'] \
                       and p.suffix.lower() in ['.png', '.jpg', '.jpeg']:              s += 20
                    return s
                found_path = sorted(candidates, key=lambda x: -score(x))[0]
                break

        if found_path:
            new_filename = found_path.name
            shutil.copy2(found_path, images_dir / new_filename)
            print(f"[+] Recovered (legacy): {original_ref} → {new_filename}")
            if found_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                return f"![{name_stem}](images/{new_filename})"
            return f"**[Attached: [{new_filename}](images/{new_filename})]**"
        else:
            print(f"[!] NOT FOUND (legacy): {original_ref}")
            return f"**[MISSING FILE: {original_ref}]**"

    return pattern.sub(replacer, markdown_text)


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert DOCX using MarkItDown & extract embedded images."
    )
    parser.add_argument("input_docx", help="Path to input DOCX file")
    parser.add_argument(
        "-o", "--output", default=None,
        help="Path to output Markdown file (default: same name as input with .md extension)"
    )
    parser.add_argument(
        "--legacy-dir", default="GIFT",
        help="Legacy directory to search for referenced images (default: GIFT)"
    )
    args = parser.parse_args()

    # Tentukan output path: default ke nama file input + .md di direktori yang sama
    if args.output is None:
        args.output = str(Path(args.input_docx).with_suffix(".md"))

    base_dir   = Path.cwd()
    input_path = Path(args.input_docx)
    output_md  = Path(args.output)
    output_dir = output_md.parent
    images_dir = output_dir / "images"

    legacy_base = base_dir / args.legacy_dir
    legacy_dirs = [legacy_base / "GIFT", legacy_base]

    if not input_path.exists():
        print(f"Error: Input DOCX not found: {input_path}")
        sys.exit(1)

    print(f"[*] Input  : {input_path}")
    print(f"[*] Output : {output_md}")
    print(f"[*] Images : {images_dir}")
    print()

    # 1. Ekstrak semua gambar dari DOCX ZIP terlebih dahulu
    print("[-] Extracting embedded images from DOCX...")
    extracted = extract_docx_images(input_path, images_dir)
    print()

    # 2. Konversi DOCX → Markdown via MarkItDown
    print("[-] Running MarkItDown conversion...")
    md = MarkItDown()
    try:
        result       = md.convert(str(input_path))
        raw_markdown = result.text_content
    except Exception as e:
        print(f"Error during MarkItDown conversion: {e}")
        sys.exit(1)
    print()

    # 3. Ganti placeholder base64 truncated dengan link ke file gambar
    print("[-] Replacing base64 placeholders with image links...")
    processed = replace_base64_placeholders(raw_markdown, extracted)
    print()

    # 4. Tangani referensi legacy 'Dirujuk dari file ...' (fallback)
    print("[-] Checking for legacy image references...")
    final_markdown = recover_legacy_images(processed, images_dir, legacy_dirs)
    print()

    # 5. Simpan output
    output_md.parent.mkdir(parents=True, exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(final_markdown)

    print(f"[=] Done!")
    print(f"[=] Markdown : {output_md}")
    print(f"[=] Images   : {images_dir}  ({len(list(images_dir.iterdir()))} files)")


if __name__ == "__main__":
    main()
