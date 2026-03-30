import json
from cleaner import clean_row
from parser import parse_gst_row

def build_dataset(all_rows):
    data = []

    for row in all_rows:
        row = clean_row(row)
        parsed = parse_gst_row(row)

        if parsed:
            data.append(parsed)

    return data


def save_dataset(data):
    with open("data/processed/gst_data.json", "w") as f:
        json.dump(data, f, indent=4)