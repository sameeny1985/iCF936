# FI9 Spatial Encoding – Interactive Demo & Reference Implementation

**Paper:** *FI9: A 512-State Spatial Encoding Architecture Based on a 3×3 Graphical Cell Matrix for Compact Digital Representation*  
**Author:** Said Hassan Ameeny Poor  
**ORCID:** https://orcid.org/0009-0008-3450-7770  
**DOI:** 10.5281/zenodo.21733520 (Version 2.0)

This repository provides a **working, testable implementation** of the FI9 architecture described in the paper so that reviewers can verify encoding / decoding correctness, inspect the full 512-state codebook, and experiment with graphical tokens and hashes.

## What is FI9?

FI9 represents each digital value by the **spatial occupation pattern** of a fixed 3×3 matrix of cells.  
Each cell is either empty (0) or occupied by a point (1).  
There are exactly \(2^9 = 512\) possible symbols.

- States **0–255** → direct one-byte mapping (compatible with ASCII / UTF-8 bytes)
- States **256–511** → reserved for protocol control, graphical hashes, blockchain instructions, etc.

The fundamental principle of the paper:

> “The position of a point is the information.”

## Quick Start (Local)

### Option A – Static Web Demo (recommended for reviewers)

```bash
# Just open the file in any modern browser
open index.html
# or
python -m http.server 8000
# then visit http://localhost:8000
```

### Option B – Python library

```bash
pip install -r requirements.txt
python -c "
from fi9 import FI9
encoder = FI9()
symbols = encoder.encode(b'Hello FI9')
print(symbols)
print(encoder.decode(symbols))
"
```

### Option C – Run the Flask demo (for Render)

```bash
pip install -r requirements.txt
python app.py
# visit http://localhost:5000
```

## Deploying to GitHub + Render

1. **Push this repository to GitHub**
2. On [Render.com](https://render.com):
   - New → Static Site (or Web Service)
   - Connect the GitHub repo
   - For Static Site: set **Publish Directory** = `.` (root contains `index.html`)
   - For Web Service: set **Build Command** = `pip install -r requirements.txt`  
     **Start Command** = `gunicorn app:app`
3. After deployment, share the public URL with reviewers. They can immediately encode/decode text and inspect every FI9 symbol.

## Project Structure

```
fi9-demo/
├── index.html              # Fully self-contained interactive demo (no server needed)
├── app.py                  # Optional Flask backend (for Render Web Service)
├── fi9.py                  # Core FI9 library (Python)
├── requirements.txt
├── static/
│   └── style.css
├── templates/
│   └── index.html          # Flask version of the UI
├── docs/
│   └── codebook.md         # Human-readable description of the mapping
└── tests/
    └── test_fi9.py
```

## Cell Ordering Convention (Reference Codebook)

Cells are numbered in **row-major** order:

```
1 2 3
4 5 6
7 8 9
```

The numerical state of a symbol is the integer formed by treating the nine cells as bits, where **bit 0 (LSB)** corresponds to cell 1 (top-left) and **bit 8 (MSB)** corresponds to cell 9 (bottom-right).

This mapping is deterministic, bijective, and fully reversible (Properties 1–4 of the paper).

## Features Implemented for Reviewers

- Encode any text / binary data → sequence of FI9 symbols
- Decode FI9 symbols back to original bytes
- Visual 3×3 grid rendering for every state (0–511)
- Full interactive codebook browser
- Graphical token example (32 consecutive FI9 symbols)
- Graphical Hash (SHA-256 mapped into FI9 symbols)
- **Native FI Hash** (Section 7.1 research prototype) – pure spatial-domain hash performing nonlinear substitution + geometric diffusion directly on FI9 states (0–511)
- Unit tests verifying round-trip correctness, determinism and basic avalanche behaviour

## Limitations (as stated in the paper)

- This is a **symbolic representation layer**, not a replacement for SHA-256 or existing consensus algorithms.
- The Native FI Hash is a **research prototype** only; its security properties have not been formally analysed.
- No hardware or optical recognition implementation is included.

## Citation

```bibtex
@misc{ameeny_poor_2025_fi9,
  author       = {Said Hassan Ameeny Poor},
  title        = {FI9: A 512-State Spatial Encoding Architecture Based on a 3×3 Graphical Cell Matrix},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.21733520},
  version      = {2.0}
}
```

---

**For reviewers:** Open `index.html` (or the deployed Render URL) and try encoding the sentence  
“The position of a point is the information.”  
You will see the corresponding sequence of 3×3 graphical symbols and can verify that decoding recovers the original text exactly.
