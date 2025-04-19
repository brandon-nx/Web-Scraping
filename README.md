# Web Automation
Python tool to automate daily SGX derivatives data downloads by date or date range, with logging, CLI, and recovery support. This Python script automates the download of daily derivative files published by the Singapore Exchange (SGX). It supports downloading a single day's data or a full range of dates. The script logs all activity and supports both command-line arguments and configuration via `.ini` files.

---

## ✅ Features

- Download SGX files by date or date range
- Automatically creates folders and logs downloads
- Tracks successfully downloaded files to avoid duplicates
- Supports redownload option for failed or refreshed data
- Logging to both console and file
- Configurable via command-line and `.ini` config files

---

## 📦 Files Downloaded

For each date, the script downloads:

- `WEBPXTICK_DT-YYYYMMDD.zip`
- `TC_YYYYMMDD.txt`
- `TickData_structure.dat`
- `TC_structure.dat`

All files are fetched from the official SGX derivatives research portal.

---

## 🚀 Usage

Make sure you have Python 3 installed.

### 🔹 Basic Single-Date Download

```bash
python download_sgx_file.py --date 20240410
