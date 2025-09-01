import xml.etree.ElementTree as ET
import pandas as pd
import re
import os

'''
This code converts xml data to csv files for each indicator in Apple Health export.
'''

def preprocess_apple_health(xml_file, output_folder="apple_health_csv"):
    os.makedirs(output_folder, exist_ok=True)
    pattern = re.compile(r"HKQuantityTypeIdentifier\w+|HKCategoryTypeIdentifier\w+")

    # Store data in per-indicator buffers
    buffers = {}

    for event, elem in ET.iterparse(xml_file, events=("end",)):
        if elem.tag == "Record":
            t = elem.attrib.get("type", "")
            if pattern.match(t):
                time = elem.attrib.get("startDate")
                value = elem.attrib.get("value")
                if time and value:
                    try:
                        val = float(value)
                    except ValueError:
                        elem.clear()
                        continue
                    day = time.split(" ")[0]
                    if t not in buffers:
                        buffers[t] = []
                    buffers[t].append([time, day, val])

        elem.clear()  # free memory

    # Write one CSV per indicator
    for indicator, rows in buffers.items():
        df = pd.DataFrame(rows, columns=["timestamp", "day", "value"])
        safe_name = indicator.replace("HKQuantityTypeIdentifier", "").replace("HKCategoryTypeIdentifier", "")
        out_path = os.path.join(output_folder, f"{safe_name}.csv")
        df.to_csv(out_path, index=False)
        print(f"✅ Saved {indicator} → {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    xml_file = "/Users/liuchenshu/Documents/Research/NUS/Project - SEBLink/Biometric data/export.xml"  # replace with your Apple export.xml path
    preprocess_apple_health(xml_file)
