"""
Assumptions:
- Request and Additional Data sections always have the same amount in left/right (wrong)
- Never any new labels in the Request and Additional Data sections
- Only one line for all dosing rows except for the last

Issues:
- Decimals
- 9 vs. 0
- 0 vs. O
- 7-AAA vs. TAAA
- ) vs. J
- ri vs. n (seems impossible unless higher res)
- (0 vs. 6
- I/ vs. V
"""

import cv2
import pytesseract
import numpy as np
import argparse
from difflib import SequenceMatcher

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Check similarity of two strings, 
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to input image")
args = vars(ap.parse_args())
img = cv2.imread(args["image"])
size = img.shape[0] // 300 * 2 + 1 # Found with experimentation

# scale_amt = 1000 / img.shape[0]
# img = cv2.resize(img, None, fx=scale_amt, fy=scale_amt)

# Sharpen - good for bad images 
if img.shape[0] < 1000: # 1000 is arbitrary, probably adjust later
    kernel = np.array([[0, -1, 0],
                    [-1, 5,-1],
                    [0, -1, 0]])
    img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)

def divideSections():
    # Find the contours 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    # rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # print(contours)
    
    # Creating a copy of image
    im2 = img.copy()
    
    # A text file is created and flushed
    file = open("recognized.txt", "w+")
    file.write("")
    file.close()
    
    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file

    objects = []
    sectionPos = []
    headers = ["Request", "Additional Data", "Dosing", "Analytes", "Comments"]
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        objects.append((x, y, w, h))
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cropped = img[y:y + h, x:x + w]
        text = pytesseract.image_to_string(cropped, lang='eng', config='--psm 7')

        text = text.replace("\n", "")
        text = text.strip()

        if text in headers:
            sectionPos.append((y, text))
            sectionPos.append((y + h, text))
        if text == "Additional":
            sectionPos.append((y, "Additional Data"))
            sectionPos.append((y + h, "Additional Data"))

    objects.sort(key=lambda x: x[1], reverse = True)

    sectionPos.append((0, "Start"))
    sectionPos.append((objects[0][1] - 2, "End")) # Not always valid
    sectionPos.sort(key=lambda x: x[0])
    # print(bah)

    print(sectionPos)

    cv2.imshow("Image", im2)
    cv2.waitKey(0)
