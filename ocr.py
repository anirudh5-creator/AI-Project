from paddleocr import PaddleOCR

# Updated initialization
ocr = PaddleOCR(use_textline_orientation=True, lang='en')

# Updated method
result = ocr.predict('Write_Every_day.png')

# Print results
for line in result:
    print(line)