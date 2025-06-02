# Import packages
#%pip install --quiet yfinance yahooquery
import re
import pandas as pd
import yfinance as yf
from yahooquery import search

from datetime import datetime, timedelta

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Merge rows where file has split data across multiple rows
def merge_faulty_rows(df):
    new_df = df.copy().astype(object)
    new_df.iloc[:,0] = new_df.iloc[:,0].replace("", pd.NA)
    bad_date_mask = new_df.iloc[:,0].isna()
    to_drop = []
    for idx in new_df.index[bad_date_mask]:
        prev_idx = idx - 1
        if prev_idx < 0:
            continue
        for col in new_df.columns:
            val_bad = new_df.at[idx, col]
            if pd.notna(val_bad) and str(val_bad).strip() != "":
                prev_val = new_df.at[prev_idx, col]
                if pd.notna(prev_val) and str(prev_val).strip() != "":
                    new_df.at[prev_idx, col] = f"{prev_val} {val_bad}"
                else:
                    new_df.at[prev_idx, col] = val_bad
        to_drop.append(idx)
    new_df = new_df.drop(index=to_drop).reset_index(drop=True)
    return new_df

# Get running cash balance
def get_cash_balance(data) -> pd.DataFrame:
    # Get final balance on each transaction day
    balance_tr = data.iloc[:, [0, -2]]
    balance_tr.columns = ['Date', 'Position_EUR']
    balance_tr['Date'] = pd.to_datetime(balance_tr['Date'], format='%d-%m-%Y')
    balance_tr = balance_tr.groupby(balance_tr.columns[0], as_index=False).first()

    # Fill in missing dates with previous balance
    start_date = balance_tr.loc[balance_tr['Position_EUR']>0, 'Date'].min()
    current_day = pd.to_datetime('today')
    date_range = pd.date_range(start=start_date, end=current_day, freq='D')
    df_dates = pd.DataFrame({'Date': date_range})
    daily_balance = pd.merge(df_dates, balance_tr, on='Date', how='left')
    daily_balance = daily_balance.sort_values(by='Date').reset_index(drop=True)
    daily_balance = daily_balance.fillna(method='ffill')
    daily_balance['Ticker'] = 'CASH'
    return daily_balance

def extract_quantity(text):
    # Remove rights issues prefix when applicable
    text = text.split(': ')[-1]

    # Split by spaces
    tokens = text.split()
    if tokens[0] in ["Compra", "Venda"]:
        # Check if the second token is numeric after cleaning
        first_num = tokens[1].replace(".", "").replace(",", "")
        
        # Try to see if there's a second number that should be combined
        if len(tokens) > 2 and tokens[2][0].isdigit():
            # If the next token starts with a digit, combine them
            second_num = tokens[2].replace(".", "").replace(",", "")
            qty_str = first_num + second_num
        else:
            # If not, just use the first number
            qty_str = first_num
            
        return int(qty_str)
    return None

def extract_price(text):
    match = re.search(r'@([\d\s]+(?:,\d+)?)', text)
    if not match:
        raise ValueError(f"No valid amount found in the string: {text}")
    
    num_str = match.group(1)
    num_str = re.sub(r'\s+', '', num_str)  # remove all whitespace
    num_str = num_str.replace(',', '.')    # turn comma into decimal point
    currency = text.split()[-2]
    return float(num_str), currency

def load_trades(data) -> pd.DataFrame:
    # Ensure correct number of columns exist
    if data.shape[1] != 12:
        raise ValueError(f"Number of columns in table does not match statement structure.")

    # Keep only relevant rows
    trades = data.iloc[:, [0,4,5,8]].copy()
    trades = trades.loc[~data['ISIN'].isna()]
    trades.columns = ['Date','ISIN','Transaction','Amount']
    trades = trades[trades.apply(lambda row: row['Transaction'].endswith("(" + row['ISIN'] + ")"), axis=1)]

    parsed_rows = []
    for _, row in trades.iterrows():
        tr = row["Transaction"]
        isin_raw = row["ISIN"]
        isin = isin_raw.strip().upper()

        # Skip invalid-format ISIN immediately
        ISIN_PATTERN = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")
        if not ISIN_PATTERN.match(isin):
            continue

        # Parse date into pandas.Timestamp
        raw_date = row["Date"].strip()
        dt_py = datetime.strptime(raw_date, "%d-%m-%Y").date()
        dt = pd.Timestamp(dt_py)

        # Quantity is the second token; remove spaces (thousands separator) and other separators
        qty_str = extract_quantity(tr)
        try:
            qty = int(qty_str)
        except ValueError:
            continue
        side = tr.replace('Compra','Buy').replace('Venda','Sell')  
        qty = qty if "Buy" in side else -qty

        # After "@", we have "<price> <CURRENCY> (<ISIN>)"
        price_local, currency = extract_price(tr)

        parsed_rows.append({
            "Date": dt,
            "ISIN": isin,
            "Qty": qty,
            "Currency": currency,
            "Price": price_local
        })

    parsed = pd.DataFrame(parsed_rows)
    return parsed

def map_isin_to_ticker(isin: str) -> str | None:
    """
    Use yahooquery.search(isin) to fetch the top quote's "symbol".
    Returns the ticker if found, else None.
    """
    try:
        resp = search(isin)
    except Exception:
        return None
    if not isinstance(resp, dict):
        return None
    quotes = resp.get("quotes", [])
    if not quotes:
        return None
    return quotes[0].get("symbol")

def build_positions(parsed: pd.DataFrame, all_isins: set[str]) -> pd.DataFrame:
    filtered = parsed[parsed["ISIN"].isin(all_isins)].copy()
    if filtered.empty:
        return pd.DataFrame(columns=["Date", "ISIN", "Qty_cum", "Currency"])

    grouped = filtered.groupby(["ISIN", "Date", "Currency"], as_index=False).agg({"Qty": "sum"})
    if grouped.empty:
        return pd.DataFrame(columns=["Date", "ISIN", "Qty_cum", "Currency"])

    first_date = grouped["Date"].min()
    last_date = grouped["Date"].max()
    all_days = pd.DataFrame({"Date": pd.bdate_range(first_date, last_date)})

    dfs = []
    for isin, sub in grouped.groupby("ISIN"):
        curr = sub["Currency"].iloc[0]
        temp = all_days.copy()
        temp["ISIN"] = isin
        temp = temp.merge(sub[["Date", "Qty"]], on="Date", how="left").sort_values("Date")
        temp["Qty"] = temp["Qty"].fillna(0).astype(int)
        temp["Qty_cum"] = temp["Qty"].cumsum()
        temp["Currency"] = curr

        nz_idx = temp.index[temp["Qty_cum"] != 0]
        if len(nz_idx) == 0:
            continue
        first_nz = temp.loc[nz_idx[0], "Date"]
        temp = temp[temp["Date"] >= first_nz].copy()
        temp = temp[temp["Qty_cum"] != 0].copy()
        dfs.append(temp)

    if not dfs:
        return pd.DataFrame(columns=["Date", "ISIN", "Qty_cum", "Currency"])

    return pd.concat(dfs, axis=0).reset_index(drop=True)

def main(csv_path: str | None = None):
    # 1) Load trades from CSV
    data = pd.read_csv(csv_path).pipe(merge_faulty_rows)
    parsed = load_trades(data)
    if parsed.empty:
        print("No valid trades found. Exiting.")
        return

    # 2) Map each unique ISIN to ticker (via yahooquery); collect unmapped
    unique_isins = set(parsed["ISIN"].unique().tolist())
    isin_to_ticker: dict[str, str] = {}
    not_mapped: set[str] = set()
    print("\n2) Mapping ISINs → Yahoo tickers:")
    for isin in sorted(unique_isins):
        ticker = map_isin_to_ticker(isin)
        if ticker:
            isin_to_ticker[isin] = ticker
            print(f"  ✔ {isin} → {ticker}")
        else:
            not_mapped.add(isin)
            print(f"  ✘ {isin} → NOT FOUND")

    # 3) Build end‐of‐day positions for all ISINs (mapped + unmapped)
    positions = build_positions(parsed, unique_isins)
    if positions.empty:
        return
    # Attach ticker (NaN for unmapped)
    positions["Ticker"] = positions["ISIN"].map(isin_to_ticker)
    # positions = positions[positions["ISIN"].isin(['ES0183746314','DE0007500001'])]

    # 4) Build price_map for unmapped ISINs
    price_map = {}
    for isin in not_mapped:
        sub = parsed[parsed["ISIN"] == isin].sort_values("Date")
        if sub.empty:
            continue
        purchases = sub[sub["Qty"] > 0]
        if not purchases.empty:
            price_map[isin] = purchases.iloc[0]["Price"]
        else:
            price_map[isin] = sub.iloc[0]["Price"]

    # 5) Download historical close prices for *mapped* tickers via yfinance
    first_date = positions["Date"].min()
    last_date = positions["Date"].max()
    yf_start = first_date.strftime("%Y-%m-%d")
    yf_end = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
    unique_tickers = list(isin_to_ticker.values())

    if unique_tickers:
        yf_data = yf.download(
            tickers=unique_tickers,
            start=yf_start,
            end=yf_end,
            progress=False
        )
        close_df = yf_data["Close"].copy()
        all_bdays = pd.bdate_range(first_date, last_date)
        close_df = close_df.reindex(all_bdays).ffill()
    else:
        all_bdays = pd.bdate_range(first_date, last_date)
        close_df = pd.DataFrame(index=all_bdays)

    # 6) Download FX rates for non‐EUR positions
    currencies = positions["Currency"].unique().tolist()
    fx_tickers = [f"EUR{c}=X" for c in currencies if c != "EUR"]
    if fx_tickers:
        fx_data = yf.download(
            tickers=fx_tickers,
            start=yf_start,
            end=yf_end,
            progress=False
        )
        fx_close = fx_data["Close"].copy()
        fx_close = fx_close.reindex(all_bdays).ffill()
    else:
        fx_close = pd.DataFrame(index=all_bdays)

    # 7) Merge positions with prices & FX (use price_map for unmapped)
    def get_close_local(row):
        isin = row["ISIN"]
        if isin in price_map:
            close = float(price_map[isin])
            return round(close, 3)
        close = float(close_df.loc[row["Date"], row["Ticker"]])
        return round(close, 3)

    def get_fx_rate(row):
        if row["Currency"] == "EUR":
            return 1.0
        fx_sym = f"EUR{row['Currency']}=X"
        return float(fx_close.loc[row["Date"], fx_sym])

    positions["Close_Local"] = positions.apply(get_close_local, axis=1)
    positions["FX_Rate"]    = positions.apply(get_fx_rate, axis=1)
    positions["Close_EUR"]  = positions["Close_Local"] / positions["FX_Rate"]
    positions["Position_EUR"] = positions["Qty_cum"] * positions["Close_EUR"]
    positions = positions[positions['Position_EUR']>0]

    # 8) Load & build daily EUR cash balance
    cash = get_cash_balance(data)  
    cash = cash.loc[cash['Date'].isin(all_bdays.tolist())]
    positions = pd.concat([positions, cash]).sort_values(by='Date').reset_index(drop=True)

    # 10) Final DataFrame and save
    output_filename = "daily_positions_eur_notional_with_cash.csv"
    positions.to_csv(output_filename, index=False)

    return positions

if __name__ == "__main__":
    csv_path='../Account.csv'
    main(csv_path)