# MarkItDown Image Recovery

A tool to convert DOCX files into Markdown format with image recovery from legacy folders.

## Installation

You can install the tool using the following command:
```bash
pip install -e .
```

## Usage

Run the main command with the required arguments. The tool expects the path to the input DOCX file and the output Markdown file. You can also specify a legacy directory to search for images.

```bash
markitdownimage <input_docx> -o <output.md> [--legacy-dir LEGACY_DIR_NAME]
```

### Arguments:
- `input_docx`: Path to the input DOCX file (Required).
- `-o`, `--output`: Path to the output Markdown file (Required).
- `--legacy-dir`: Legacy project directory name to search for images. (Optional, default is `GIFT`).

### Example:
```bash
markitdownimage documents/report.docx -o revisions/report_revised.md --legacy-dir old_images
```
