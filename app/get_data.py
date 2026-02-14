#!/usr/bin/env python3
"""
Ollama Docker CSV Generator for Manim Bar Chart Race
Generates EXACT columns: Year, USA, CHN, RUS, JPN, DEU, IND, GBR, FRA, BRA, ITA, CAN, AUS, KOR, ISR, SAU, NZD, Milestone
"""

import requests
import pandas as pd
import json
import time
import os
from pathlib import Path

# === CONFIG ===
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # or "qwen2.5" or "gemma2"
OUTPUT_PATH = "data/data.csv"

def wait_for_ollama(timeout=60):
    """Wait for Ollama Docker container to be ready"""
    print("⏳ Waiting for Ollama...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": "ping", "stream": False}, timeout=5)
            if response.status_code == 200:
                print("✅ Ollama ready!")
                return True
        except:
            time.sleep(2)
    print("❌ Ollama not ready after 60s")
    return False

def generate_csv_data(title, start_year=1900, end_year=2026):
    """Generate generic CSV dataset for 100+ viral topics with EXACT required columns"""
    
    countries = ['USA', 'CHN', 'RUS', 'JPN', 'DEU', 'IND', 'GBR', 'FRA', 'BRA', 'ITA', 'CAN', 'AUS', 'KOR', 'ISR', 'SAU', 'NZD']
    columns_list = ['Year'] + countries + ['Milestone']
    
    # SMART RULES based on dataset type
    rules = {
        "military": "Values in Billions USD. USA leads, China surges post-2000, Russia peaks 1980s",
        "gdp": "Values in Trillions USD (PPP). USA starts dominant, China catches up post-1990", 
        "economy": "Values in Billions USD. Steady growth with crisis dips (2008, 2020)",
        "tech": "Values in Millions of units or Gbps. Exponential growth post-2000",
        "internet": "Values in Mbps or Millions users. Asia leads growth post-2010",
        "society": "Values as percentages or per 100k. Steady improvement trends",
        "health": "Values as per 100k or years. Developed nations lead",
        "environment": "Values in Millions tons or %. Sharp changes post-1990",
        "sports": "Values as counts or Millions USD. USA dominates most",
        "weird": "Values as counts or per 100k. Spikes around cultural events"
    }
    
    # Detect category from title
    category = "economy"
    title_lower = title.lower()
    for key in rules:
        if key in title_lower:
            category = key
            break
    
    prompt = f"""Generate REALISTIC TIME SERIES CSV for "{title}" ({start_year}-{end_year}) with EXACT columns:

{','.join(columns_list)}

🚨 CRITICAL: YEARLY INCREMENTAL DATA REQUIRED
- Year column: STRICTLY INCREMENTS BY 1 (1900, 1901, 1902, ..., 2026)
- One row PER YEAR, NO gaps, NO duplicates
- Years must be sequential: Year(n+1) = Year(n) + 1

RULES BY CATEGORY ({category}):
{rules[category]}

GENERAL RULES:
1. Years: {start_year}-{end_year} (annual, exactly {end_year-start_year+1} rows)
2. Leader (USA) starts 3-10x others
3. China: Rapid growth post-1990 (2x-5x annual acceleration)
4. Russia: Peak mid-period, 1990s collapse, 2020s recovery
5. Japan/Germany: Steady 2nd tier performers
6. India/Brazil: Late surge post-2000
7. Milestones: 8 key events matching {title} history

📈 GROWTH PATTERNS (YEARLY INCREMENTS):
- Realistic growth: 2-8% yearly increase
- Crises cause 10-30% drops in specific years
- Tech/emerging markets explode post-2000
- Values generally TREND UPWARD over time

Return ONLY valid CSV (no markdown, no explanation):
{','.join(columns_list)}
1900,4.2,0.8,1.5,0.9,1.2,0.3,0.8,0.6,0.2,0.4,0.5,0.3,0.1,0.05,0.2,0.02,"Early Competition"
1901,4.3,0.9,1.6,0.95,1.25,0.32,0.82,0.62,0.22,0.42,0.52,0.32,0.11,0.06,0.22,0.03,"Incremental Growth"
... (continue with YEARLY increments until 2026)
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Ultra-low for perfect yearly sequence
            "num_predict": 6000
        }
    }
    
    print(f"🤖 Generating '{title}' dataset (yearly increments)...")
    response = requests.post(OLLAMA_URL, json=payload, timeout=180)
    
    if response.status_code != 200:
        print(f"❌ Ollama error: {response.status_code}")
        return None
    
    result = response.json()["response"]
    
    # Extract clean CSV with validation
    csv_lines = []
    lines = result.split('\n')
    for line in lines:
        line = line.strip()
        if (line and ',' in line and len(line.split(',')) >= 18 and 
            not line.startswith(('```', '#', 'Note'))):
            csv_lines.append(line)
    
    csv_content = '\n'.join(csv_lines[:80])
    
    return csv_content

def validate_csv(csv_content):
    """Validate CSV has exact columns"""
    lines = csv_content.strip().split('\n')
    if len(lines) < 2:
        return False
        
    header = lines[0].strip().split(',')
    required_cols = ['Year', 'USA', 'CHN', 'RUS', 'JPN', 'DEU', 'IND', 'GBR', 'FRA', 'BRA', 'ITA', 'CAN', 'AUS', 'KOR', 'ISR', 'SAU', 'NZD', 'Milestone']
    
    # Check exact columns
    if [col.strip() for col in header] != required_cols:
        print("❌ Wrong columns:", [col.strip() for col in header])
        return False
    
    # Check reasonable data range
    for line in lines[1:]:
        values = line.split(',')
        try:
            year = int(values[0])
            usa = float(values[1])
            if not (1960 <= year <= 2026 and 100 <= usa <= 1000):
                return False
        except:
            return False
    
    return True

def save_csv(csv_content):
    """Save validated CSV"""
    Path("data").mkdir(exist_ok=True)
    
    with open(OUTPUT_PATH, 'w') as f:
        f.write(csv_content)
    
    df = pd.read_csv(OUTPUT_PATH)
    print(f"✅ CSV saved: {OUTPUT_PATH}")
    print(f"📊 Shape: {df.shape}")
    print(f"📈 Years: {df['Year'].min()} to {df['Year'].max()}")
    print(f"💰 USA range: ${df['USA'].min():.1f}B to ${df['USA'].max():.1f}B")
    print("\nFirst 3 rows:")
    print(df.head(3).to_string(index=False))

def main():
    print("🚀 Ollama Docker CSV Generator")
    print("=" * 50)
    
    # 1. Check Ollama
    if not wait_for_ollama():
        print("💡 Start Ollama Docker:")
        print("docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama")
        print("docker exec -it ollama ollama pull llama3.2")
        return
    
    # 2. Pull model if needed
    try:
        requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": "test", "stream": False}, timeout=10)
    except:
        print(f"📥 Pulling {MODEL}...")
        os.system(f"docker exec ollama ollama pull {MODEL}")
        time.sleep(5)
    
    # 3. Generate CSV
    csv_content = generate_csv_data('Nuclear Warhead Stockpiles (Cold War–Present)')
    if not csv_content or not validate_csv(csv_content):
        print("❌ Invalid CSV generated. Try different model.")
        return
    
    # 4. Save
    save_csv(csv_content)
    
    print("\n🎬 Ready for Manim!")
    print(f"uv run manim -pqh ultimate.py UltimateUniversalRace")

if __name__ == "__main__":
    main()
