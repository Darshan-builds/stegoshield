# 🛡️ StegoShield

> **Steganographic Malware Carrier Detection & Static Analysis Suite**  
> *A defensive cybersecurity research prototype designed for digital forensics, malware triage, and academic demonstration.*

---

## 📸 Interface Preview

### 🏠 Executive Dashboard
![StegoShield Dashboard](assets/dashboard.png)

### 🔍 Threat Scorecard & Static Analysis Breakdown
![StegoShield Analysis](assets/analysis_view.png)

---

## 🚀 Quick Installation & Setup

### 🐧 Linux (Parrot OS, Kali, Ubuntu, Debian, Mint)

#### ⚡ Option A: Automated 1-Line Setup (Recommended)
Clone the repository and run the automated installer:
```bash
git clone https://github.com/Darshan-builds/stegoshield.git
cd stegoshield
chmod +x install.sh && ./install.sh
```

*(This automatically installs system graphics dependencies, creates a virtual environment, installs packages with timeout protection, and launches the app).*

---

#### 🛠️ Option B: Manual Step-by-Step Setup
```bash
# 1. Install system prerequisites (Qt/OpenGL libraries)
sudo apt update && sudo apt install -y python3-venv python3-full libgl1 libegl1 libxkbcommon-x11-0 libxcb-cursor0

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Run StegoShield
python app.py
```

---

### 🪟 Windows Setup

```powershell
# 1. Clone repository
git clone https://github.com/Darshan-builds/stegoshield.git
cd stegoshield

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch application
python app.py
```
*(Or double-click `run.bat`)*

---

### 🍎 macOS Setup

```bash
git clone https://github.com/Darshan-builds/stegoshield.git
cd stegoshield
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## 💡 Troubleshooting & Common Issues Fixed

### 1. `error: externally-managed-environment` (PEP 668)
* **Why:** Modern Linux (Parrot, Debian, Ubuntu 23+) blocks global `sudo pip install`.
* **Fix:** Use a virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
  *Or use the override flag:* `pip install -r requirements.txt --break-system-packages`

---

### 2. `WARNING: Connection timed out while downloading (pyside6)`
* **Why:** Full PySide6 is ~175 MB and drops on slow networks.
* **Fix:** We use **`pyside6-essentials`** (~60 MB) which contains all required Qt modules without bulky 3D engines:
  ```bash
  pip install --default-timeout=1000 --retries 10 -r requirements.txt
  ```

---

### 3. `qt.qpa.plugin: Could not find the Qt platform plugin "xcb"`
* **Why:** Missing Linux X11/XCB display libraries.
* **Fix:** Run:
  ```bash
  sudo apt install -y libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxkbcommon-x11-0
  ```

---

### 4. Git asking for `Username / Password` or `gnuTLS recv error (-54)`
* **Why:** The repository is set to **Private**, or terminal timeout occurred.
* **Fix:** 
  1. Go to your repo on GitHub ➔ **Settings** ➔ **Danger Zone** ➔ Change visibility to **Public**.
  2. Or if keeping Private, use a **Personal Access Token (PAT)** instead of account password:
     ```bash
     git clone https://<YOUR_TOKEN>@github.com/Darshan-builds/stegoshield.git
     ```

---

## ✨ Features & Detection Engine

| Forensic Module | Detection Capability |
|---|---|
| 🔐 **Cryptographic Fingerprinting** | Computes MD5, SHA-1, SHA-256, SHA-384, SHA-512 |
| 📋 **Magic Byte Format Validator** | Detects extension mismatches and spoofed header bytes |
| 📊 **Shannon Entropy Engine** | Calculates file-wide and chunk-level randomness for encrypted payloads |
| 📎 **Trailing Data Detection** | Identifies stealth payloads appended past logical `IEND` (PNG) / `EOI` (JPEG) markers |
| 🔬 **LSB Statistical Analysis** | Chi-Square Pair-of-Values (PoV) testing & inter-channel variance detection |
| 🧩 **PNG Chunk Parser** | Inspects ancillary chunks (`tEXt`, `zTXt`, `pHYs`) and IDAT stream abnormalities |
| 🖼️ **JPEG Marker Parser** | Scans application markers (`APP0`-`APP15`), COM comments, and payload injections |
| 🔤 **String & URL Heuristics** | Extracts URLs, IP addresses, Base64 patterns, and suspicious command keywords |
| 🗂️ **Nested Signature Scanner** | Detects embedded PE headers (`MZ`/`PE`), ELF binaries, ZIP/RAR/7z archives |
| 🛡️ **Weighted Risk Engine** | Computes an intuitive, explainable 0–100 threat score |
| 📄 **Forensic Reporting** | Generates standalone JSON audit trails and styled HTML reports |

---

## 🏗️ Project Architecture

```text
stegoshield/
├── core/                   # Offline static analysis engine
│   ├── analyzer.py         # Multi-module pipeline orchestrator
│   ├── risk_engine.py      # Weighted risk scoring engine
│   ├── format_validator.py # Magic bytes & header validation
│   ├── hashing.py          # Cryptographic hashing algorithms
│   ├── entropy.py          # Shannon entropy calculator
│   ├── trailing_data.py    # EOF trailing byte detector
│   ├── lsb_analyzer.py     # LSB Chi-Square statistical detector
│   ├── png_analyzer.py     # PNG chunk inspector
│   ├── jpeg_analyzer.py    # JPEG structure & marker parser
│   ├── noise_analyzer.py   # Pixel noise & residual analysis
│   ├── strings.py          # ASCII/Unicode string & URL extractor
│   ├── embedded_data.py    # Embedded executable & archive scanner
│   ├── metadata.py         # EXIF & image metadata parser
│   └── report_generator.py # JSON & HTML forensic export
├── gui/                    # Modern PySide6 Desktop GUI
│   ├── theme.py            # Datify Light Visual Identity & Onest typography
│   ├── main_window.py      # Navigation shell & layout
│   ├── dashboard.py        # Analytics overview
│   ├── analyze_view.py     # Real-time analysis view & modern scorecard
│   ├── compare_view.py     # Side-by-side differential analysis
│   ├── demo_view.py        # Synthetic test lab
│   ├── report_view.py      # Report browser
│   ├── settings_view.py    # Dynamic risk weight configuration
│   └── about_view.py       # Tool info & legal disclaimers
├── config/
│   └── scoring.json        # Configurable indicator weights & thresholds
├── demo/
│   ├── generate_samples.py # Safe synthetic test carrier generator
│   └── samples/            # Pre-generated test image cases
├── fonts/                  # Bundled Onest font family
├── tests/                  # Pytest unit test suite (28/28 passing)
├── assets/                 # Readme screenshots
├── install.sh              # 1-click Linux installer
├── run.sh                  # Linux launcher script
├── run.bat                 # Windows launcher script
├── app.py                  # Main application entry point
├── requirements.txt        # Python package dependencies
└── README.md
```

---

## 🧪 Automated Unit Testing

Validate all forensic detection modules with **pytest**:
```bash
python -m pytest tests/ -v
```

```text
tests/test_embedded_data.py    PASSED
tests/test_entropy.py          PASSED
tests/test_format_validator.py PASSED
tests/test_hashing.py          PASSED
tests/test_lsb.py              PASSED
tests/test_png.py              PASSED
tests/test_risk_engine.py      PASSED
tests/test_strings.py          PASSED
tests/test_trailing_data.py    PASSED

================ 28 passed in 1.4s ================
```

---

## ⚖️ Ethical & Defensive Scope

- **100% Defensive**: Performs non-destructive offline static analysis only.
- **Zero Detonation**: Does **not** execute, unpack, or execute embedded binaries, shellcodes, or scripts.
- **Research & Academic Focus**: Built strictly for malware analysis, digital forensics, and cybersecurity education.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
