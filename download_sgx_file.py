import requests
import argparse
import os
import logging
import configparser
from datetime import datetime, timedelta

# --- Logging Setup ---
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_filename = os.path.join(log_dir, f"sgx_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Download SGX Derivative Files by Date or Range")
parser.add_argument('--config', help='Path to config file (INI format)')
parser.add_argument('--date', help='Single date in YYYYMMDD format')
parser.add_argument('--start-date', help='Start date in YYYYMMDD format (for range)')
parser.add_argument('--end-date', help='End date in YYYYMMDD format (required with --start-date)')
parser.add_argument('--output-dir', help='Directory to save files')
parser.add_argument('--redownload', action='store_true', help='Force redownload even if file was already downloaded')
args = parser.parse_args()

# --- Load Config File if Provided ---
config = configparser.ConfigParser()
if args.config:
    config.read(args.config)
    config_defaults = config['DEFAULT']
else:
    config_defaults = {}

# --- Helper Function to Get Arg or Config Value ---
def get_config_value(cli_value, config_key, default=None):
    if cli_value is not None:
        return cli_value
    return config_defaults.get(config_key, default)

# --- Assign Final Parameter Values ---
date = get_config_value(args.date, 'date')
start_date = get_config_value(args.start_date, 'start_date')
end_date = get_config_value(args.end_date, 'end_date')
output_dir = get_config_value(args.output_dir, 'output_dir', 'downloads')
redownload = args.redownload or config_defaults.get('redownload', 'false').lower() == 'true'

# --- Create Output Directory ---
os.makedirs(output_dir, exist_ok=True)

# --- Load Download History ---
record_file = os.path.join(output_dir, "downloaded_files.txt")
downloaded_files = set()
if os.path.exists(record_file):
    with open(record_file, "r") as f:
        downloaded_files = set(line.strip() for line in f if line.strip())

# --- Download Function ---
def download_for_date(date_str):
    base_urls = {
        f"WEBPXTICK_DT-{date_str}.zip": f"https://links.sgx.com/1.0.0/derivatives-web/tick-download/webpxtick_dt_{date_str}.zip",
        f"TC_{date_str}.txt": f"https://links.sgx.com/1.0.0/derivatives-web/tick-download/tc_{date_str}.txt",
        "TickData_structure.dat": "https://links.sgx.com/1.0.0/derivatives-web/tick-download/TickData_structure.dat",
        "TC_structure.dat": "https://links.sgx.com/1.0.0/derivatives-web/tick-download/TC_structure.dat"
    }

    for filename, url in base_urls.items():
        if filename in downloaded_files and not redownload:
            logging.info(f"Skipping {filename} (already downloaded)")
            continue

        logging.info(f"Downloading: {filename}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                save_path = os.path.join(output_dir, filename)
                with open(save_path, "wb") as f:
                    f.write(response.content)
                logging.info(f"Saved to {save_path}")
                with open(record_file, "a") as log:
                    log.write(f"{filename}\n")
            else:
                logging.error(f"Failed to download {filename} — Status: {response.status_code}")
        except Exception as e:
            logging.exception(f"Error downloading {filename}: {e}")

# --- Main Execution ---
if date:
    download_for_date(date)
elif start_date and end_date:
    try:
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        if start > end:
            logging.error("Start date cannot be after end date.")
            exit(1)
        current = start
        while current <= end:
            date_str = current.strftime("%Y%m%d")
            logging.info(f"\n===== Processing date: {date_str} =====")
            download_for_date(date_str)
            current += timedelta(days=1)
    except ValueError:
        logging.error("Invalid date format. Use YYYYMMDD.")
else:
    logging.error("You must specify --date or both --start-date and --end-date.")
