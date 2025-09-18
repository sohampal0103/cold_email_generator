# Research Paper (IEEE Format)

This folder contains the IEEE-formatted LaTeX paper for the Cold Email Generator project.

## Files
- `ieee_paper.tex`: Main LaTeX source using the IEEEtran class.
- `references.bib`: Bibliography entries used in the paper.

## Build on Overleaf (Recommended)
1. Create a new project and upload `ieee_paper.tex`, `references.bib`, and optionally the `imgs/architecture.png` (place at `imgs/architecture.png` or update the path in the paper).
2. Set compiler to `pdfLaTeX`.
3. Build. Overleaf will resolve the `IEEEtran` class automatically.

## Build Locally (macOS)
Ensure a LaTeX distribution is installed (e.g., MacTeX).

```bash
# If you don't have latexmk, install MacTeX or a minimal TeX distribution
cd paper
latexmk -pdf ieee_paper.tex
```

The output `ieee_paper.pdf` will be generated in the same folder.

## Notes
- Update the author block with your correct email.
- Replace or update the architecture figure path if needed.
- Add more references in `references.bib` as you cite new sources.
