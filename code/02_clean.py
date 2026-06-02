"""
02_clean.py
-----------
Build a clean firm-year panel from the most recent WRDS pull.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


def find_env():
    current = Path(os.getcwd())
    for path in [current] + list(current.parents):
        if (path / ".env").exists():
            return path / ".env"
        try:
            for sibling in path.iterdir():
                if sibling.is_dir() and (sibling / ".env").exists():
                    return sibling / ".env"
        except PermissionError:
            continue
    raise FileNotFoundError("Could not find .env in any parent or sibling directory.")


env_file     = find_env()
project_root = env_file.parent
os.chdir(project_root)
print(f"Project root: {project_root}")

RAW_DIR  = Path("data") / "raw"
PROC_DIR = Path("data") / "processed"
OUT_PATH = PROC_DIR / "panel_clean.parquet"
PROC_DIR.mkdir(parents=True, exist_ok=True)


def find_latest_folder(base_dir: Path) -> Path:
    folders = sorted(
        [f for f in base_dir.iterdir() if f.is_dir()],
        key=lambda f: f.name
    )
    if not folders:
        raise FileNotFoundError(f"No pull folders found in {base_dir}.")
    return folders[-1]


try:
    latest_folder = find_latest_folder(RAW_DIR)
except FileNotFoundError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print(f"Using pull folder: {latest_folder.name}")

parquet_files = sorted(latest_folder.glob("fyear_*.parquet"))

if not parquet_files:
    print(f"ERROR: No fyear_*.parquet files in {latest_folder}")
    sys.exit(1)

print(f"\nReading {len(parquet_files)} parquet files...")
chunks = []
for f in parquet_files:
    try:
        chunk = pd.read_parquet(f)
        chunks.append(chunk)
        print(f"  {f.name:<25}  {len(chunk):>8,} rows  |  {chunk.shape[1]} columns")
    except Exception as e:
        print(f"  WARNING: Could not read {f.name}: {e}")

if not chunks:
    print("ERROR: No data could be read.")
    sys.exit(1)

print("\nConcatenating chunks...")
df = pd.concat(chunks, ignore_index=True)
print(f"  Combined: {len(df):,} rows x {df.shape[1]} columns")

df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

n_before = len(df)
df = df.drop_duplicates()
n_dupes = n_before - len(df)
if n_dupes:
    print(f"\nDropped {n_dupes:,} exact duplicate rows")

if "gvkey" in df.columns and "fyear" in df.columns:
    n_key_dupes = df.duplicated(subset=["gvkey", "fyear"]).sum()
    if n_key_dupes:
        print(f"  Note: {n_key_dupes:,} duplicate gvkey-fyear pairs remain")

# -- Filter to EUR reporting currency -----------------------------------------
if "curcd" in df.columns:
    n_before = len(df)
    df = df[df["curcd"] == "EUR"].copy()
    n_removed = n_before - len(df)
    print(f"\nCurrency filter (EUR only):")
    print(f"  Before: {n_before:,} rows")
    print(f"  After:  {len(df):,} rows  (removed {n_removed:,} non-EUR observations)")
    if "loc" in df.columns:
        country_counts = df["loc"].value_counts().head(15)
        print(f"\n  Top countries remaining:")
        for country, count in country_counts.items():
            print(f"    {country}: {count:>8,}")
else:
    print("\nWARNING: curcd column not found — currency filter skipped.")

# -- KMU Filter (<=250 Mitarbeiter gemaess EU-Definition) ---------------------
if "emp" in df.columns:
    n_before = len(df)
    df = df[df["emp"] <= 0.25].copy()
    n_removed = n_before - len(df)
    print(f"\nKMU Filter (emp <= 0.25, d.h. <= 250 Mitarbeiter):")
    print(f"  Before: {n_before:,} rows")
    print(f"  After:  {len(df):,} rows  (removed {n_removed:,} non-KMU firms)")
else:
    print("\nWARNING: emp column not found — KMU filter skipped.")

# -- Drop rows missing panel identifiers --------------------------------------
n_before = len(df)
if "gvkey" in df.columns and "fyear" in df.columns:
    df = df.dropna(subset=["gvkey", "fyear"])
    n_dropped = n_before - len(df)
    if n_dropped:
        print(f"\nDropped {n_dropped:,} rows missing gvkey or fyear")
else:
    print("WARNING: gvkey or fyear not found.")

# -- Convert object columns to numeric ----------------------------------------
STRING_COLS = {
    "gvkey", "conm", "cusip", "isin", "sedol", "tic",
    "naics", "sic", "loc", "curcd", "fic", "exchg",
    "costat", "stalt", "datafmt", "indfmt", "popsrc", "consol"
}

print("\nConverting numeric columns...")
converted = 0
for col in df.columns:
    if df[col].dtype == object and col not in STRING_COLS:
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            converted += 1
        except Exception:
            pass
print(f"  Converted {converted} columns to numeric dtype")

if "fyear" in df.columns:
    df["fyear"] = df["fyear"].astype(int)

sort_cols = [c for c in ["gvkey", "fyear"] if c in df.columns]
if sort_cols:
    df = df.sort_values(sort_cols).reset_index(drop=True)
    print(f"\nSorted by: {sort_cols}")

print("\n" + "="*55)
print("Panel Statistics")
print("="*55)
print(f"  Total rows (firm-years):  {len(df):>10,}")
if "gvkey" in df.columns:
    print(f"  Unique firms (gvkey):     {df['gvkey'].nunique():>10,}")
if "fyear" in df.columns:
    print(f"  Fiscal years covered:     {int(df['fyear'].min())}--{int(df['fyear'].max())}")
if "loc" in df.columns:
    print(f"  Countries (loc):          {df['loc'].nunique():>10,}")
if "curcd" in df.columns:
    print(f"  Currencies:               {df['curcd'].unique().tolist()}")
print(f"  Total columns:            {df.shape[1]:>10,}")

if "fyear" in df.columns:
    print("\n  Observations per year:")
    for year, count in df.groupby("fyear").size().items():
        print(f"    {int(year)}: {count:>8,}")

print("\n  Completeness of key variables:")
key_vars = ["at", "sale", "ib", "nicon", "xrd", "dltt", "seq",
            "emp", "capx", "ebit", "ebitda", "ppent"]
for col in key_vars:
    if col in df.columns:
        pct = df[col].notna().sum() / len(df) * 100
        bar = "█" * int(pct / 5)
        print(f"    {col:<8}  {pct:>5.1f}%  {bar}")

print(f"\nSaving to {OUT_PATH} ...")
df.to_parquet(OUT_PATH, index=False)
size_mb = OUT_PATH.stat().st_size / 1_048_576
print(f"  Saved: {size_mb:.1f} MB")

log_path = PROC_DIR / "clean_log.txt"
log_path.write_text(
    f"02_clean.py log\n"
    f"===============\n"
    f"Run:              {datetime.now().isoformat()}\n"
    f"Source folder:    {latest_folder}\n"
    f"Files read:       {len(parquet_files)}\n"
    f"Currency filter:  EUR only\n"
    f"KMU filter:       emp <= 0.25 (<=250 Mitarbeiter)\n"
    f"Rows:             {len(df):,}\n"
    f"Columns:          {df.shape[1]}\n"
    f"Firms (gvkey):    {df['gvkey'].nunique() if 'gvkey' in df.columns else 'N/A'}\n"
    f"Output:           {OUT_PATH} ({size_mb:.1f} MB)\n"
)

print(f"\nClean panel ready: {OUT_PATH}")
print(f"Log written:       {log_path}")
print(f"\nNext step: python code/03_descriptives.py")

print("\nPreview of clean panel:")
df_check = pd.read_parquet(OUT_PATH)
print(f"Shape: {df_check.shape[0]:,} rows x {df_check.shape[1]} columns")
print(df_check[["gvkey", "conm", "fyear", "loc", "curcd",
                 "at", "sale", "nicon", "xrd", "dltt", "emp"]].head(10).to_string())
