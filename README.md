# markitdownimage

Convert DOCX files to Markdown with automatic extraction of embedded images.

Images are extracted directly from the DOCX archive (`word/media/`) and saved as `figure_01.png`, `figure_02.png`, etc. in an `images/` folder next to the output file. All inline image references in the markdown are rewritten to proper relative paths.

## Requirements

- Python >= 3.10
- [markitdown](https://github.com/microsoft/markitdown)

## Installation

```bash
pip install -e .
```

> **Note:** Make sure you install with Python 3.10+. On macOS, the system `python3` may point to Python 3.9. Use `python3.11 -m pip install -e .` if needed.

After installation, add the bin directory to your PATH if prompted (e.g., `/Library/Frameworks/Python.framework/Versions/3.11/bin`).

## Usage

### Minimal (output defaults to same name as input)

```bash
markitdownimage paper.docx
```

This creates `paper.md` and an `images/` folder in the same directory as the input file.

### Specify output path

```bash
markitdownimage paper.docx -o output/paper_converted.md
```

### All arguments

```bash
markitdownimage <input_docx> [-o OUTPUT] [--legacy-dir LEGACY_DIR]
```

| Argument | Required | Default | Description |
|---|---|---|---|
| `input_docx` | Yes | — | Path to the input DOCX file |
| `-o`, `--output` | No | Same name as input with `.md` extension | Path to the output Markdown file |
| `--legacy-dir` | No | `GIFT` | Legacy folder to search for `(Dirujuk dari file ...)` references |

## How It Works

1. Opens the DOCX as a ZIP archive and extracts all files from `word/media/` → saved as `figure_01.png`, `figure_02.png`, etc.
2. Converts the DOCX to Markdown using [MarkItDown](https://github.com/microsoft/markitdown).
3. Replaces all `![](data:image/...;base64...)` placeholders in the output with proper relative links (`images/figure_NN.png`).
4. Handles legacy `(Dirujuk dari file filename.ext)` references by searching a specified legacy directory.

## Example Output Structure

```
project/
├── paper.docx
├── paper.md
└── images/
    ├── figure_01.png
    ├── figure_02.png
    └── ...
```
