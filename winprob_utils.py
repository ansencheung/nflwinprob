#winprob_utils

from selenium import webdriver  #type: ignore
from selenium.webdriver.chrome.service import Service #type: ignore
from webdriver_manager.chrome import ChromeDriverManager #type: ignore
from selenium.webdriver.common.by import By #type: ignore
from bs4 import BeautifulSoup #type: ignore
import json
import time
import pandas as pd #type: ignore
import re
import numpy as np #type: ignore
import os


def openDriver():
    # Setup headless browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print('Done Opening Driver')
    return driver

def getText(url,driver):

    driver.get(url)
    time.sleep(5)  # wait for JS to load


    soup = BeautifulSoup(driver.page_source, "html.parser")
    scripts = soup.find_all("script")

    # Find raw JSON from the correct script block
    script_text = ""
    for script in scripts:
        if 'wnPrb' in script.text and 'plys' in script.text:
            script_text = script.text
            break

    if not script_text:
        raise Exception("Could not find script containing wnPrb and plys")
    
    return script_text

def compute_time_seconds(prd, clck):
    if clck is None or prd is None:
        return None
    try:
        minutes, seconds = map(int, clck.strip().split(":"))
        quarter_offset = (prd - 1) * 900
        clock_remaining = minutes * 60 + seconds
        time_elapsed = quarter_offset + (900 - clock_remaining)
        return time_elapsed
    except:
        return None

def getData(script_text):

    start = script_text.find('"wnPrb":{"pts":')

    i = start
    while i < len(script_text):
        if script_text[i] == '}':
            end = i + 1
            break
        i += 1

    # Step 3: Extract the JSON string
    wnprb_json_text = script_text[start:end]

    # Clean header off
    prefix = '"wnPrb":{"pts":{'
    wnprb_clean = wnprb_json_text[len(prefix):]

    matrix = []
    i = 0
    length = len(wnprb_clean)

    while i < length:
        # Stop if we reach the end
        if wnprb_clean[i] == '}':
            break

        # === Parse ID ===
        while wnprb_clean[i] in ['"', ' ']:
            i += 1
        id_start = i
        while wnprb_clean[i] != ':':
            i += 1
        id_str = wnprb_clean[id_start:i]
        id_num = int(id_str.strip('"'))  # 🛠️ Fix: strip trailing quote

        i += 1  # skip the colon

        # === Parse PTS ===
        while wnprb_clean[i] == ' ':
            i += 1
        pts_start = i
        while i < length and wnprb_clean[i] not in [',', '}']:
            i += 1
        pts_str = wnprb_clean[pts_start:i]
        pts_val = float(pts_str)

        # Store
        matrix.append([id_num, pts_val])

        # Skip comma if there is one
        if i < length and wnprb_clean[i] == ',':
            i += 1

    # Convert to DataFrame
    df_pts = pd.DataFrame(matrix, columns=["id", "pts"])

        # Step 1: Find start of "plys":[
    plys_start = script_text.find('"plys":[')

    if plys_start == -1:
        raise Exception("Could not find 'plys':[")

    # Step 2: Find matching closing bracket ']'
    i = plys_start
    bracket_count = 0
    found_start = False
    length = len(script_text)

    while i < length:
        char = script_text[i]

        if char == '[':
            bracket_count += 1
            found_start = True
        elif char == ']':
            bracket_count -= 1
            if found_start and bracket_count == 0:
                plys_end = i + 1  # include the closing bracket
                break
        i += 1

    # Step 3: Slice the plys string
    plys_text = script_text[plys_start:plys_end]
    

        # Clean the prefix: remove `"plys":[`
    plys_clean = plys_text[len('"plys":['):]

    # Make a fast lookup for pts using the parsed DataFrame
    id_to_pts = dict(zip(df_pts["id"], df_pts["pts"]))

    # Initialize final matrix
    final_matrix = []

    i = 0
    length = len(plys_clean)

    while i < length:
        # Stop at end of list
        if plys_clean[i] == ']':
            break

        # === Find the next play object ===
        if plys_clean[i] != '{':
            i += 1
            continue

        obj_start = i
        brace_count = 0
        while i < length:
            if plys_clean[i] == '{':
                brace_count += 1
            elif plys_clean[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    obj_end = i + 1
                    break
            i += 1

        obj_str = plys_clean[obj_start:obj_end]

        # === Extract fields manually ===
        id_match = re.search(r'"id":"?(\d+)"?', obj_str)
        clck_match = re.search(r'"clck":"([^"]+)"', obj_str)
        prd_match = re.search(r'"prd":(\d+)', obj_str)

        if id_match:
            id_val = int(id_match.group(1))
            if id_val in id_to_pts:
                clck_val = clck_match.group(1) if clck_match else None
                prd_val = int(prd_match.group(1)) if prd_match else None
                final_matrix.append([id_val, prd_val, clck_val, id_to_pts[id_val]])

    # Convert to DataFrame
    df_final = pd.DataFrame(final_matrix, columns=["id", "prd", "clck", "pts"])
    # Apply to DataFrame
    df_final["time_sec"] = df_final.apply(lambda row: compute_time_seconds(row["prd"], row["clck"]), axis=1)

    # Preview
    df_final = df_final.sort_values("time_sec").reset_index(drop=True)

    return df_final

def createTensor(game_ids, filename, driver):
    all_data = []

    # Step 1️⃣: Check if file exists → load it if so
    if os.path.exists(filename):
        print(f"{filename} already exists. Loading existing data...")
        loaded_data = np.load(filename, allow_pickle=True)
        existing_len = len(loaded_data)
        print(f"Found {existing_len} existing games.")
        # Add existing data to all_data
        all_data.extend(loaded_data.tolist())
    else:
        existing_len = 0
        print(f"{filename} does not exist. Starting fresh.")

    # Step 2️⃣: Start processing from index existing_len
    for i, game_id in enumerate(game_ids[existing_len:]):
        true_index = existing_len + i  # this is your absolute index in full game_ids list

        try: 
            url = f"https://www.espn.com/nfl/game/_/gameId/{game_id}"
            script_text = getText(url, driver)
            df = getData(script_text)

            all_data.append((df[["time_sec", "pts"]].to_numpy(), int(game_id)))
            print(f"[{true_index}/{len(game_ids)}] Done getting data for {game_id}")

            # Optional: Save intermediate result every 10 games (in case crash happens)
            if (true_index + 1) % 10 == 0:
                np.save(filename, np.array(all_data, dtype=object))
                print(f"Intermediate save at {true_index + 1} games.")

        except Exception as e:
            print(f"Error with game {game_id}: {e}")

    # Step 3️⃣: Final save
    np.save(filename, np.array(all_data, dtype=object))
    print(f"Final save complete. Total games saved: {len(all_data)}")

    return np.array(all_data, dtype=object)


    
