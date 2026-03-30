import re

def parse_gst_row(row):
    text = " ".join(row)

    match = re.search(r'(\d+\.?\d*)\s*%', text)

    if match:
        gst = float(match.group(1))
        service = text.replace(match.group(0), "").strip()

        return {
            "service": service,
            "gst_rate": gst
        }

    return None