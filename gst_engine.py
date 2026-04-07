def extract_price(text):
    import re

    match = re.search(r'(\d+)', text.replace(',', ''))
    if match:
        return int(match.group(1))
    return None


def calculate_gst(price, rate):
    gst_amount = price * rate / 100
    final_price = price + gst_amount
    return gst_amount, final_price