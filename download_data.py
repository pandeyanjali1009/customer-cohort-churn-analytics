from pathlib import Path
from urllib.request import urlretrieve

URL = "https://www.datheon.in/datasets/telco_customer_churn.csv"
DEST = Path("data/telco_customer_churn.csv")

def main():
    DEST.parent.mkdir(exist_ok=True)
    print("Downloading Telco Customer Churn dataset...")
    urlretrieve(URL, DEST)
    if DEST.stat().st_size == 0:
        raise ValueError("Downloaded CSV is empty.")
    print(f"Saved: {DEST.resolve()} ({DEST.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
