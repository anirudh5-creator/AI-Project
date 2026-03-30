def chunk_data(structured_data, chunk_size=3):
    chunks = []

    for i in range(0, len(structured_data), chunk_size):
        chunk = structured_data[i:i+chunk_size]

        text = ""
        for item in chunk:
            text += f"Service: {item['service']}, GST: {item['gst_rate']}%\n"

        chunks.append(text)

    return chunks