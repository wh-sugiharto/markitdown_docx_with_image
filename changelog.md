# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-04-17
### Added
- `-o` / `--output` argument is now optional; defaults to same filename as input with `.md` extension.
- Output `images/` folder is placed relative to the output Markdown file location.

### Changed
- Renamed `fix_markitdown_images.py` → `markitdownimage.py` for consistency with the CLI command name.
- Updated `setup.py` to reference new module name and bumped version to `1.1.0`.
- Rewrote `README.md` with complete CLI reference table and how-it-works explanation.

---

## [1.1.0] - 2026-04-17
### Added
- New `extract_docx_images()` function: extracts images directly from DOCX ZIP (`word/media/`) instead of decoding base64.
- New `replace_base64_placeholders()` function: replaces truncated `data:image/...;base64...` placeholders with proper relative image links (`images/figure_NN.png`).

### Fixed
- Images were not saved because MarkItDown (v0.0.1a1) truncates base64 data to `...`. Now bypassed by reading directly from the DOCX archive.
- `markitdownimage` command not found: root cause is Python version mismatch (system python3 = 3.9; markitdown requires Python >=3.10). Script must be run with `python3.11`.

---

## [1.0.0] - 2026-03-18
### Added
- Initial commit with standard repository structure (README, LICENSE, gitignore).
- Basic tool setup (`setup.py` & `fix_markitdown_images.py`).

### Changed
- Translated `README.md` to English and added detailed CLI arguments.

