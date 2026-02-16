import requests
import pandas as pd
import os
import time
from pathlib import Path

# === CONFIG ===
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"
OUTPUT_DIR = "datasets"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Starting numbers for 1916 to prevent the "Baseline" text error
STARTING_VALUES = {
    "USA": 55.0, "RUS": 45.0, "CHN": 12.0, "IND": 8.0, 
    "EGY": 2.0, "KOR": 1.5, "UKR": 3.0, "POL": 4.5, 
    "PAK": 2.5, "SYR": 1.0, "VNM": 1.0, "PRK": 0.5, 
    "ISR": 0.2, "TUR": 3.5
}

def format_human_readable(n):
    """Converts strings/floats to clean numeric strings or K/M format."""
    try:
        # Clean the string of any placeholder text the AI might have hallucinated
        clean_n = "".join(c for c in str(n) if c.isdigit() or c in '.-')
        val = float(clean_n)
        if val >= 1_000_000: return f"{val/1_000_000:.2f}M"
        if val >= 1_000: return f"{val/1_000:.2f}K"
        return str(round(val, 2))
    except:
        return "0.0" # Default if AI still sends "Baseline+%"

def get_era_context(year):
    if year < 1939: return "Pre-WWII volatility. Military spending is moderate."
    if year < 1946: return "WWII Total War. Spending should spike 10-20% annually."
    if year < 1991: return "Cold War Tensions. Steady annual growth of 3-5%."
    return "Modern multipolar era. Diverse spending trends."

def generate_chunk_with_retry(title, start_year, end_year, countries, last_row_seed=None):
    target_years = list(range(start_year, end_year + 1))
    columns = ['Year'] + countries + ['Milestone', 'Primary_Source']
    
    # If no seed, use our hardcoded STARTING_VALUES
    if not last_row_seed:
        last_row_seed = f"1915," + ",".join([str(STARTING_VALUES.get(c, 1.0)) for c in countries])

    for attempt in range(3):
        print(f"      🔄 Attempt {attempt + 1} for {start_year}-{end_year}...")
        
        system_prompt = (
            "You are a numeric data engine. Output ONLY raw CSV rows. "
            "NEVER use the word 'Baseline'. Use ONLY digits and decimals for values. "
            "No headers. No markdown."
        )
        
        user_prompt = (
            f"Task: CSV for {title}\n"
            f"Years: {', '.join(map(str, target_years))}\n"
            f"Columns: {','.join(columns)}\n"
            f"Context: {get_era_context(start_year)}\n"
            f"Seed Data (Previous Year): {last_row_seed}\n"
            "Constraint: Every country column MUST be a float (e.g. 72.45). Do NOT write text formulas."
        )

        payload = {
            "model": MODEL,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 1000, "stop": ["Task:", "```"]}
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload).json().get("response", "").strip()
            parsed_rows = []
            found_years = []
            
            for line in response.split('\n'):
                parts = [p.strip().strip('"') for p in line.split(',')]
                if len(parts) >= len(columns) and parts[0].isdigit():
                    yr = int(parts[0])
                    # Verify this row is actually numeric data, not "Baseline+2%"
                    if yr in target_years and yr not in found_years:
                        # Safety check: is the second column a number?
                        if any(char.isdigit() for char in parts[1]):
                            parsed_rows.append(parts)
                            found_years.append(yr)
            
            if len(found_years) == len(target_years):
                parsed_rows.sort(key=lambda x: int(x[0]))
                return parsed_rows
        except:
            continue
            
    return []

def generate_full_dataset(title, start, end, countries):
    header = ['Year'] + countries + ['Milestone', 'Primary_Source']
    final_lines = [','.join(header)]
    last_line_str = None

    for s in range(start, end + 1, 5):
        e = min(s + 4, end)
        print(f"   📊 Processing {s}-{e}...")
        
        chunk = generate_chunk_with_retry(title, s, e, countries, last_row_seed=last_line_str)
        
        if not chunk:
            print(f"      🔴 Gap detected at {s}. AI failed to provide numeric data.")
            continue

        for row in chunk:
            formatted = [row[0]] # Year
            for i in range(1, len(countries) + 1):
                formatted.append(format_human_readable(row[i]))
            formatted.extend(row[len(countries)+1:]) # Milestone/Source
            
            line = ','.join(formatted)
            final_lines.append(line)
            last_line_str = line

    return '\n'.join(final_lines)

def repair_and_interpolate_csv(filename):
    """Fills any missing years and interpolates the data for a smooth video."""
    df = pd.read_csv(filename)
    
    # 1. Ensure Year is the index and numeric
    df['Year'] = pd.to_numeric(df['Year'])
    df = df.set_index('Year')
    
    # 2. Create a full range of years from start to end
    full_range = range(df.index.min(), df.index.max() + 1)
    df = df.reindex(full_range)
    
    # 3. Interpolate numeric columns (Countries)
    # This fills gaps like [10, NaN, NaN, 40] with [10, 20, 30, 40]
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].interpolate(method='linear')
    
    # 4. Forward fill text columns (Milestones/Sources)
    df = df.ffill()
    
    # Save it back
    df.to_csv(filename)
    print(f"✨ CSV Repaired: {filename}")


def main():
    if not os.path.exists("data/1_geopolitics.csv"): return
    master_df = pd.read_csv("data/1_geopolitics.csv")
    
    for _, task in master_df.iterrows():
        title = task['title']
        filename = f"{OUTPUT_DIR}/{title.replace(' ', '_').lower()}.csv"
        if os.path.exists(filename): continue

        print(f"\n🎯 GENERATING: {title}")
        data = generate_full_dataset(title, int(task['start']), int(task['end']), str(task['countries']).split())
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)

        repair_and_interpolate_csv(filename)


# Usage:
# repair_and_interpolate_csv("datasets/world_military_spending.csv")
if __name__ == "__main__":
    main()
