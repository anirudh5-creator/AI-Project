from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import numpy as np

# ---------- STEP 1: INIT OCR ----------
ocr = PaddleOCR(lang='en')

# ---------- STEP 2: PDF PATH ----------
pdf_path = r"C:\Users\athar\Desktop\Atharva Garg 22.04.2023\All folders\Atharva Garg\Classes\MNNIT\Semister\4th sem\Subject\Artificial Intelligence\Project\PaddleOCR\services.pdf"

# ---------- STEP 3: CONVERT PDF TO IMAGES ----------
images = convert_from_path(pdf_path)

# ---------- STEP 4: TABLE EXTRACTION FUNCTION ----------
def extract_table(result):
    rows = []

    for res in result:
        boxes = res['rec_boxes']
        texts = res['rec_texts']

        data = list(zip(boxes, texts))

        # ---------- SAFE COORDINATE HANDLING ----------
        def get_y(box):
            if isinstance(box[0], (list, tuple)):
                return box[0][1]
            return box[1]

        def get_x(box):
            if isinstance(box[0], (list, tuple)):
                return box[0][0]
            return box[0]

        # ---------- SORT BY ROW ----------
        data.sort(key=lambda x: get_y(x[0]))

        grouped_rows = []
        current_row = []
        prev_y = None

        for box, text in data:
            y = get_y(box)

            if prev_y is None or abs(y - prev_y) < 20:
                current_row.append((box, text))
            else:
                grouped_rows.append(current_row)
                current_row = [(box, text)]

            prev_y = y

        grouped_rows.append(current_row)

        # ---------- SORT COLUMNS ----------
        for row in grouped_rows:
            row = sorted(row, key=lambda x: get_x(x[0]))
            rows.append([text for _, text in row])

    return rows

# ---------- STEP 5: PROCESS PDF ----------
all_rows = []

for i, img in enumerate(images):
    print(f"\n📄 Processing Page {i+1}...")

    img_np = np.array(img)   # FIX: PIL → numpy

    result = ocr.predict(img_np)

    table = extract_table(result)

    for row in table:
        print(row)
        all_rows.append(row)

# ---------- STEP 6: GST EXTRACTION ----------
print("\n🔍 Extracting GST Data...\n")

for row in all_rows:
    try:
        # Extract numbers from row
        numbers = [x for x in row if any(c.isdigit() for c in x)]

        # GST rows usually have 2–3 numeric values
        if len(numbers) >= 2:
            description = " ".join(row[:-len(numbers)])
            gst_rate = numbers[-1]

            print("📌 Service:", description)
            print("💰 GST Rate:", gst_rate, "%\n")

    except:
        continue