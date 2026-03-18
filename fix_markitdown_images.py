#!/usr/bin/env python3
"""
Convert DOCX to Markdown using MarkItDown and RECOVER images from legacy folder.
Input:  DOCX file (default: searches in Rev1 folder)
Output: paper_revised.md + images copied to 'images/' folder from legacy GIFT/
"""

import os
import sys
import re
import shutil
import argparse
from pathlib import Path
from markitdown import MarkItDown

def recover_images(markdown_text, output_dir, legacy_image_dirs):
    """
    Finds text references like '(Dirujuk dari file filename.ext)' 
    and attempts to find/copy that file from legacy directories.
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Regex matches: (Dirujuk dari file filename.ext)
    # Group 1 = filename with extension
    pattern = re.compile(r'\(Dirujuk dari file\s+([^\)]+)\)', re.IGNORECASE)

    counter = 1
    
    def replacer(match):
        nonlocal counter
        original_ref = match.group(1).strip()
        
        # Clean up filename: 
        # 1. Remove markdown escapes (e.g., \_) using simple replace
        # 2. Strip whitespace
        desired_name = original_ref.replace(r"\_", "_").strip()
        desired_path = Path(desired_name)
        name_stem = desired_path.stem
        desired_ext = desired_path.suffix.lower()
        
        # Search for this file in legacy dirs
        found_path = None
        
        for search_dir in legacy_image_dirs:
            candidates = []
            
            # 1. Try exact name match (highest priority)
            candidates.extend(list(search_dir.glob(desired_name)))
            
            # 2. Try exact stem match with any extension (e.g. .jpg vs .png)
            # This avoids "GIFT.jpg" matching "GIFT_Final_Report.txt"
            if not candidates:
                # glob pattern: stem.* 
                # explicit check to ensure stem is exact
                potential = list(search_dir.glob(f"{name_stem}.*"))
                candidates.extend([p for p in potential if p.stem == name_stem])
            
            if candidates:
                # Pick the best match
                def score(p):
                    s = 0
                    # Exact match gets 100
                    if p.name == desired_name: s += 100
                    
                    # Extension match gets 50
                    if p.suffix.lower() == desired_ext: s += 50
                    
                    # Image preference if we are looking for an image
                    if desired_ext in ['.png', '.jpg', '.jpeg'] and p.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                        s += 20
                        
                    return s
                
                # Sort by score desc
                found_path = sorted(candidates, key=lambda x: -score(x))[0]
                break
        
        if found_path:
            # Copy to new images dir
            # Standardize name for the new paper
            new_filename = f"{found_path.name}" 
            new_path = output_dir / new_filename
            
            shutil.copy2(found_path, new_path)
            print(f"[+] Recovered: {original_ref} -> {new_path}")
            
            # If it's an image, return image link
            if found_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                return f"![{name_stem}](images/{new_filename})"
            else:
                # If it's a text file/table, maybe return a link or reference?
                # For now, let's format it as a bold link
                return f"**[Attached: [{new_filename}](images/{new_filename})]**"
        else:
            print(f"[!] NOT FOUND: {original_ref} (cleaned: {desired_name})")
            return f"**[MISSING FILE: {original_ref}]**"

    new_text = pattern.sub(replacer, markdown_text)
    return new_text

def main():
    parser = argparse.ArgumentParser(description="Convert DOCX using MarkItDown & Recover Images.")
    parser.add_argument("input_docx", help="Path to input DOCX file")
    parser.add_argument("-o", "--output", required=True, help="Path to output Markdown file")
    parser.add_argument("--legacy-dir", default="GIFT", help="Legacy project directory to search for images (optional)")
    args = parser.parse_args()

    # define paths
    base_dir = Path.cwd()
    input_path = Path(args.input_docx)
    output_md = Path(args.output)
    
    # Images will be saved in an 'images' folder relative to the output markdown file
    output_dir = output_md.parent
    images_dir = output_dir / "images"
    
    # Legacy dirs to search
    legacy_base = base_dir / args.legacy_dir
    legacy_deep = legacy_base / "GIFT" 
    legacy_dirs = [legacy_deep, legacy_base]

    if not input_path.exists():
        print(f"Error: Input DOCX not found: {input_path}")
        sys.exit(1)

    print(f"[*] Input Source: {input_path}")
    print(f"[*] Recovery Source: {legacy_base}")
    print(f"[*] Output Target: {output_md}")
    print(f"[*] Images Target: {images_dir}")

    # 1. Convert using MarkItDown
    print("[-] Running MarkItDown conversion...")
    md = MarkItDown()
    try:
        result = md.convert(str(input_path))
        raw_markdown = result.text_content
    except Exception as e:
        print(f"Error during MarkItDown conversion: {e}")
        sys.exit(1)

    # 2. Extract/Recover Images
    print("[-] Recovering images from legacy folder...")
    final_markdown = recover_images(raw_markdown, images_dir, legacy_dirs)

    # 3. Save Markdown
    output_md.parent.mkdir(parents=True, exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(final_markdown)

    print(f"\n[=] Success! Markdown saved to '{output_md}'")
    print(f"[=] Images saved to '{images_dir}'")

if __name__ == "__main__":
    main()




