# screeny

📸 **pixel-perfect screenshot capture** — because taking webpage screenshots shouldn't be a nightmare.

built this because every screenshot tool either produces blurry images, crashes on dynamic content, or costs money. no subscriptions, no quality loss, no missing content — just crisp, full-page captures that actually work.

## ✨ what you'll get:

- 🎯 **pixel-perfect quality** — 2x+ device scaling for retina-sharp screenshots
- 📱 **mobile & desktop views** — perfect device emulation for any viewport
- ⚡ **smart content loading** — waits for lazy images, fonts, and dynamic content
- 🚫 **ad/tracker blocking** — cleaner captures without popup distractions  
- 🎨 **animation freezing** — consistent screenshots every time
- 📊 **batch processing** — capture hundreds of URLs from txt/csv files
- 🖥️ **full-page capture** — gets everything, even content below the fold
- 🎯 **custom waiting** — wait for specific elements or network states
- 🆓 **completely free** — no subscriptions, no limits, no bullshit
- ⚡ **blazing fast** — powered by playwright for maximum performance

## 🚀 getting started:

### ⚡ quick setup

```bash
# grab the dependencies
pip install playwright
playwright install

# clone and run
git clone https://github.com/fr33lo/screeny.git
cd screeny
python screeny.py -u https://example.com
```

### 🎯 basic usage

```bash
# single url (retina quality)
python screeny.py -u https://github.com

# batch process from file  
python screeny.py -f urls.txt -o screenshots/

# mobile screenshot (iphone 13 pro)
python screeny.py -u https://example.com --mobile --width 390 --height 844 --scale 3.0

# ultra-high quality desktop
python screeny.py -u https://example.com --scale 4.0 --width 2560 --height 1440
```

### 💻 installation options

**standalone script (recommended)**
```bash
git clone https://github.com/fr33lo/screeny.git
cd screeny  
pip install playwright
playwright install
python screeny.py --help
```

**python package**  
```bash
pip install -e .
playwright install
screeny --help
```

**virtual environment**
```bash
python -m venv screeny-env
source screeny-env/bin/activate  # windows: screeny-env\Scripts\activate
pip install playwright && playwright install
```

## 🎮 command options:

**input**
- `-u, --url` — single URL to capture
- `-f, --file` — batch process from txt/csv file

**output**  
- `-o, --output` — save location (default: ./screenshots)
- `--format` — png or jpeg (default: png for quality)
- `--quality` — jpeg quality 1-100 (default: 90)

**viewport**
- `--width` — viewport width (default: 1920)
- `--height` — viewport height (default: 1080)
- `--scale` — device pixel ratio (default: 2.0 for retina)
- `--mobile` — mobile device emulation

**quality & timing**
- `--wait-timeout` — timeout in milliseconds (default: 30000)
- `--wait-selector` — wait for specific CSS element
- `--wait-state` — load, domcontentloaded, or networkidle
- `--no-animations` — freeze animations (default: true)
- `--no-ads` — block trackers & ads (default: true)

## 🧪 examples

```bash
# desktop - pixel perfect
python screeny.py -u https://github.com --scale 2.0 --width 1920 --height 1080

# mobile - iphone 13 pro
python screeny.py -u https://example.com --mobile --width 390 --height 844 --scale 3.0

# batch - from text file
python screeny.py -f urls.txt -o screenshots/

# batch - from csv (url in first column)
python screeny.py -f sites.csv -o results/ --format jpeg --quality 95

# wait strategies
python screeny.py -u https://spa-app.com --wait-selector ".main-content"
python screeny.py -u https://slow-site.com --wait-state networkidle --wait-timeout 60000

# ultra high quality
python screeny.py -u https://example.com --scale 3.0 --width 2560 --height 1440 --wait-state networkidle
```

## 📜 file formats:

**urls.txt**
```
https://github.com
https://stackoverflow.com  
https://docs.python.org
https://playwright.dev
```

**sites.csv**
```csv
url,name
https://github.com,GitHub
https://stackoverflow.com,Stack Overflow  
https://docs.python.org,Python Docs
```

🔧 **how it's built:**

playwright because it's the only browser automation tool that doesn't suck. python because it works. no frameworks, no bloat, just solid code that captures pixel-perfect screenshots.

**📚 tech stack:**
- **automation:** playwright (chromium engine)
- **language:** python 3.8+ with async support  
- **image processing:** playwright's built-in screenshot api
- **cli:** argparse for clean command-line interface
- **batch processing:** csv + text file parsing
- **waiting strategies:** networkidle, dom events, custom selectors
- **quality optimization:** device pixel ratio scaling, animation blocking
- **ad blocking:** built-in request filtering

**🎯 design philosophy:**
- performance-first (async processing)
- quality-focused (2x+ scaling by default)  
- zero-config for basic use
- extensive customization for power users
- no dependencies beyond playwright

## 🤝 contributing:

found a bug? have an idea? contributions are welcome!

1. **fork** the repo
2. **create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **commit** your changes (`git commit -m 'add amazing feature'`)
4. **push** to the branch (`git push origin feature/amazing-feature`)  
5. **open** a pull request

please keep code clean and follow the existing style. add examples for new features.

---

<div align="center">

**🐈‍⬛ part of the freelo.gay ecosystem**

*no subscriptions • no quality loss • no missing content • no bullshit*

**© 2025 freelo** • built because screenshot tools shouldn't suck 📸

[![GitHub](https://img.shields.io/badge/GitHub-fr33lo-green?style=flat&logo=github)](https://github.com/fr33lo/screeny) 
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-orange?style=flat&logo=playwright)](https://playwright.dev)

</div>
