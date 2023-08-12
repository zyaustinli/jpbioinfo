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

To-Do:
- Two images in one file
- Special cases (6 on left col) 
- Other format
"""

import os
import cv2
import pytesseract
import numpy as np
import pandas as pd
import argparse
from difflib import SequenceMatcher
import win32com.client as win32
from PIL import ImageGrab

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
labels = {
    "Request": ["Request ID", "Request Set ID", "J&J Batch ID", "J&J Salt", "Submitter", "CS", "Project", "Request Type", "Molecular Formula", "Molecular Weight", "Batch Molecular Weight", "Comments"],
    "Additional Data": ["Type of Study", "Sex", "Strain", "Anti-coagulant", "Any expected side effects and safety data?"],
    "Dosing": ["Dose group", "Number of animals", "Route of admin", "Dose mg/kg", "Dose volume ml/kg, Dosing solution concentration mg/ml", "Timepoints", "Formulations", "Matrix"],
    "AnalytesTable": ["JNJ Number", "JNJ Batch", "JNJ Salt", "MW", "BMW", "CF", "Type", "Quantitated", "Comment"],
    "AnalytesText": ["Is this a Prodrug?", "Does this compound have a carboxylic acid group?", "Regimen"]
}
data = {}

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def read_excel(path):
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    # workbook = excel.Workbooks.Open(r'C:\Users\eddie\Documents\jp-bioinfo\files\ADME-1062480_JNJ-75055045_2AG_Mouse-PKPD-DL_MGL.xlsx')
    workbook = excel.Workbooks.Open(path)

    for sheet in workbook.Worksheets:
        if sheet.Name == "Study Design Summary":
            imgs = []
            for shape in sheet.Shapes:
                if shape.Name.startswith('Picture'):  # or try 'Image'
                    shape.Copy()
                    pil_image = ImageGrab.grabclipboard().convert('RGB')
                    open_cv_image = np.array(pil_image)
                    open_cv_image = open_cv_image[:, :, ::-1].copy()

                    imgs.append(open_cv_image)
                    # cv2.imshow("Image", open_cv_image)
                    # cv2.waitKey(0)

    # if len(imgs) == 0:
    #     print("bad 23")
    #     return 0
    # elif len(imgs) == 1:
    #     return imgs[0]
    # else:
    #     print("bad 24")
    #     return 0
    imgs.sort(key=lambda x: x.shape[0])
    return imgs[0]

def preprocess(img):
    if img.shape[0] < 1000: # 1000 is arbitrary, probably adjust later
        kernel = np.array([[0, -1, 0],
                        [-1, 5,-1],
                        [0, -1, 0]])
        img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
    return img

def processText(text):
    text = text.replace("\n", "")
    text = text.replace(r"’", "")
    text = text.replace(r"‘", "")
    text = text.replace(r"'", "")
    text = text.replace(r"|", "")

    text = text.strip()
    return text

def divideSections(img):
    size = img.shape[0] // 300 * 2 + 1
    # Find the contours 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    # rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    im2 = img.copy()
    objects = []
    sectionPos = []
    headers = ["Request", "Additional Data", "Dosing", "Analytes", "Comments"]
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        objects.append((x, y, w, h))
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cropped = img[y:y + h, x:x + w]
        text = pytesseract.image_to_string(cropped, lang='eng', config='--psm 7')

        text = processText(text)

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

    # Check for error
    for i in range(1, len(sectionPos) - 1, 2):
        if sectionPos[i][1] != sectionPos[i + 1][1]:
            print("bad 1")

    sections = []
    for i in range(0, len(sectionPos), 2):
        sections.append(img[sectionPos[i][0]:sectionPos[i + 1][0], 0:im2.shape[1]])

    # for sec in sections:
    #     cv2.imshow("Image", sec)
    #     cv2.waitKey(0)

    requestObj = []
    for obj in objects:
        if obj[1] > sectionPos[2][0] and obj[1] + obj[3] < sectionPos[3][0]:
            requestObj.append(obj)

    requestObj.sort(key=lambda x: x[3], reverse = True)
    chemStructLeft = requestObj[0][0]

    return objects, sectionPos, chemStructLeft

def readNoLineTable(img, type, section):
    size = img.shape[0] // 300 * 2 + 1
    if type == "Request":
        leftCount = 9
        rightCount = 3
    elif type == "Additional Data":
        leftCount = 3
        rightCount = 2
    elif type == "Analytes":
        type += "Text"
        leftCount = 2
        rightCount = 1
    else:
        print("bad 2")
    expLabels = labels[type]

    gray = cv2.cvtColor(section, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    blurred = cv2.GaussianBlur(thresh1, (7, 7), 0)
    contours, hierarchy = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    leftLabelIm = section.copy()
    wordBoxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        wordBoxes.append((x, y, w, h))

    # Find the leftmost labels (should be 9)
    wordBoxes.sort(key=lambda x: x[0])
    # print(wordBoxes)
    leftLabels = wordBoxes[:leftCount]

    # Sort by their y-coordinate
    leftLabels.sort(key=lambda x: x[1])
    y_vals = [0] # Divide them into rows    
    for i in range(leftCount - 1):
        y_vals.append(int((leftLabels[i][1] + leftLabels[i][3] + leftLabels[i + 1][1]) / 2))
    y_vals.append(leftLabelIm.shape[0])

    labelImg = []
    secondHalf = img.shape[1]
    for i in range(len(y_vals) - 1):
        cropped = leftLabelIm[y_vals[i]:y_vals[i + 1], 0:leftLabelIm.shape[1]]
        cv2.imshow("Image", cropped)
        cv2.waitKey(0)
        # First three have two columns
        if i < rightCount:
            # Find the location of the right column and crop it
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
            blurred = cv2.GaussianBlur(thresh1, (size, size), 0)
            contours, hierarchy = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            words = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                words.append((x, y, w, h))
            #     rect = cv2.rectangle(cropped, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # cv2.imshow("Image", cropped)
            # cv2.waitKey(0)
            # Should divide into label, value, label, value
            words.sort(key=lambda x: x[0])
            if len(words) == 4:
                secondHalf = words[2][0] - 10
            elif len(words) == 3:
                if words[1][0] - (words[0][0] + words[0][2]) > words[2][0] - (words[1][0] + words[1][2]):
                    secondHalf = words[1][0] - 10
                else:
                    secondHalf = words[2][0] - 10
            elif len(words) == 2:
                secondHalf = words[1][0] - 10
            else:
                print("bad 3")
            words.sort(key=lambda x: x[0])
            secondHalf = min(secondHalf, words[2][0] - 10)
        
        # Add everything to a list called labels
        if i < rightCount:
            label1 = cropped[0:cropped.shape[0], 0:secondHalf]
            label2 = cropped[0:cropped.shape[0], secondHalf:cropped.shape[1]]
            labelImg.append(label1)
            labelImg.append(label2)
            # cv2.imshow("Label 1", label1)
            # cv2.waitKey(0)
            # cv2.imshow("Label 2", label2)
            # cv2.waitKey(0)
        else:
            labelImg.append(cropped)
            # cv2.imshow("Label", cropped)
            # cv2.waitKey(0)

    if len(labelImg) != leftCount + rightCount:
        print("bad 4")

    # Read text from each label
    labelText = []
    for label in labelImg:
        label = cv2.cvtColor(label, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(label, lang='eng', config='--psm 7 --oem 3')

        # print(text)
        labelText.append(text)

        # cv2.imshow("Label", label)
        # cv2.waitKey(0)

    # Process the text (get rid of random symbols)
    # for label in labelText:
    #     label = processText(label)
    labelText = [x.replace(r'‘', '') for x in labelText]
    labelText = [x.replace(r',', '') for x in labelText]
    labelText = [x.replace('\'', '') for x in labelText]
    labelText = [x.replace('\n', '') for x in labelText]
    labelText = [x.replace(r'’', '') for x in labelText]

    true_labels = []

    for label in labelText:
        highest_sim = 0
        highest_label = ""
        for possible_match in expLabels:
            possible_sim = similar(label[:len(possible_match)].lower(), possible_match.lower())
            # print("%s and %s have %f" % (label[:len(possible_match)], possible_match, possible_sim))
            if possible_sim > highest_sim:
                highest_label = possible_match
                highest_sim = possible_sim
        true_labels.append(highest_label)
        # print("%s matches with %s" % (label, highest_label))

    values = []
    for i in range(len(true_labels)):
        # print(labelText[i][0:len(expLabels[i])].lower(), expLabels[i])
        # if labelText[i][0:len(expLabels[i])].lower() != expLabels[i]:
        #     print("AHHHHHH")
        # else:
        values.append(labelText[i][len(true_labels[i]):])

    values = [x.replace(':', '') for x in values]
    values = [x.strip() for x in values]

    # Print the results
    for i in range(len(values)):
        if not(true_labels[i] in data):
            data[true_labels[i]] = []
        data[true_labels[i]].append(values[i])

def readTable(img, type, section):
    size = img.shape[0] // 300 * 2 + 1
    if type == "Analytes":
        type += "Table"

    # cv2.imshow("Section %s" % type, section)
    # cv2.waitKey(0)

    expCols = 9
    expLabels = labels[type]

    # threshold section
    gray = cv2.cvtColor(section, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    # cv2.imshow("Thresholding", thresh)

    # vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, img.shape[1] // 100))
    vertical_kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    vertical_kernel_2 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
    vertical_eroded = cv2.erode(thresh, vertical_kernel_1, iterations=3)
    # cv2.imshow("Eroded", vertical_eroded)
    vertical_lines = cv2.dilate(vertical_eroded, vertical_kernel_2, iterations=3)
    # cv2.imshow("Vertical Lines", vertical_lines)
    # cv2.waitKey(0)

    rows, cols = vertical_lines.shape
    colSpots = []
    for i in range(cols):
        if vertical_lines[rows // 2, i] == 255:
            colSpots.append(i)

    colBoxes = []
    for i in range(len(colSpots) - 1):
        if colSpots[i + 1] - colSpots[i] > 1:
            colBoxes.append((colSpots[i] + 1, colSpots[i + 1] - 1))

    if len(colBoxes) != expCols:
        print("bad 5")
    # print(img[rows // 2, cols // 2])
    # for i in range(cols):

    hor_kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    hor_kernel_2 = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    hor_eroded = cv2.erode(thresh, hor_kernel_1, iterations=3)
    # cv2.imshow("Eroded", hor_eroded)
    hor_lines = cv2.dilate(hor_eroded, hor_kernel_2, iterations=3)
    # cv2.imshow("Horizontal Lines", hor_lines)
    # cv2.waitKey(0)

    rowSpots = []
    for i in range(rows):
        if hor_lines[i, cols // 2] == 255:
            rowSpots.append(i)

    rowBoxes = []
    for i in range(len(rowSpots) - 1):
        if rowSpots[i + 1] - rowSpots[i] > 1:
            rowBoxes.append((rowSpots[i] + 1, rowSpots[i + 1] - 1))

    table = []
    for i in range(len(rowBoxes)):
        row = []
        for j in range(len(colBoxes)):
            # Goes through each of the boxes in the table
            box = section[rowBoxes[i][0] + 1:rowBoxes[i][1] - 1, colBoxes[j][0] + 1:colBoxes[j][1]-1]
            if i == 0:
                # First row always sideways
                box = cv2.rotate(box, cv2.ROTATE_90_CLOCKWISE)
            box = cv2.copyMakeBorder(box, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
            # cv2.imshow("Box", box)
            # cv2.waitKey(0)
            if type == "Dosing":
                if i == 0 or j == len(colBoxes) - 1:
                    wordConfig = '--psm 6'
                else:
                    wordConfig = '--psm 7'
            else:
                if i == 0:
                    wordConfig = '--psm 7'
                else:
                    wordConfig = '--psm 6'
                

            text = pytesseract.image_to_string(box, lang='eng', config=wordConfig)
            if type == "Dosing":
                text = text.replace('\n', ' ')
            else:
                text = text.replace('\n', '')
            text = text.strip()
            row.append(text)
        table.append(row)

    table[0] = expLabels
    if type == "Dosing":
        for i in range(len(table[0])):
            if not(table[0][i] in data):
                data[table[0][i]] = []
            for j in range(1, len(table)):
                data[table[0][i]].append(table[j][i])

def readText(img, secStart, secEnd):
    section = img[secStart:secEnd, 0:img.shape[1]]

    text = pytesseract.image_to_string(section, lang='eng', config='--psm 6')
    text = processText(text)
    if not("Overall Comments" in data):
        data["Overall Comments"] = []
    data["Overall Comments"].append(text)

def extractData(img):
    objects, sectionPos, chemStructLeft = divideSections(img)
    for i in range(2, len(sectionPos), 2):
        title = sectionPos[i][1]
        section = img[sectionPos[i][0]:sectionPos[i+1][0], 0:img.shape[1]]
        if title == "Request" or title == "Additional Data":
            section = img[sectionPos[i][0]:sectionPos[i+1][0], 0:chemStructLeft]
            readNoLineTable(img, title, section)
        elif title == "Dosing":
            readTable(img, title, section)
        elif title == "Analytes":
            secStart = sectionPos[i][0]
            secEnd = sectionPos[i + 1][0]
            
            analytesObjects = []
            for obj in objects:
                if obj[1] > secStart and obj[1] + obj[3] < secEnd:
                    analytesObjects.append(obj)
            if len(analytesObjects) == 0:
                continue
            analytesObjects.sort(key=lambda x: x[2], reverse = True)
            tableBox = analytesObjects[0]
            sectionTable = img[tableBox[1]:tableBox[1] + tableBox[3], tableBox[0]:tableBox[0] + tableBox[2]]
            sectionTable = cv2.copyMakeBorder(sectionTable, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])

            readTable(img, title, sectionTable)

            sectionText = img[tableBox[1] + tableBox[3] + 2:sectionPos[i + 1][0], 0:img.shape[1]]
            readNoLineTable(img, title, sectionText)

        elif title == "Comments":
            readText(img, sectionPos[i][0], sectionPos[i + 1][0])
        else:
            print("bad 6")

    maxLen = 0
    for key in data:
        maxLen = max(maxLen, len(data[key]))
    for key in data:
        if len(data[key]) < maxLen:
            for i in range(maxLen - len(data[key])):
                data[key].append(data[key][-1])
    
def main():
    # Output files in files folder
    files = os.listdir("files")
    excel_files = []
    for file in files:
        if file.endswith(".xlsx") and not(file.startswith("~")):
            excel_files.append(file)

    # In the other format, third is PDF
    bad_files = ['ADME-1627071_JNJ-86639813_Rat-BBB_GluN2A NAM.xlsx', 'ADME-1627072_JNJ-87193353_Rat-BBB_GluN2A NAM.xlsx', 'ADME-1046660_JNJ-71070844_Mouse_CIA_multi-dose-PO_IL-17a.xlsx']

    for file in excel_files:
        if not(file in bad_files):
            print(file)
            img = read_excel(r'D:\BioInformatics Program Code\bio-info files\\' + file)
            # img = read_excel(r'C:\Users\eddie\Documents\jp-bioinfo\files\ADME-1062480_JNJ-75055045_2AG_Mouse-PKPD-DL_MGL.xlsx')
            img = preprocess(img)
            extractData(img)

    df = pd.DataFrame(data)
    print(df)
    df.to_csv("data.csv")

main()

#file = 'ADME-1046660_JNJ-71070844_Mouse_CIA_multi-dose-PO_IL-17a.xlsx'
#img = read_excel(r'D:\BioInformatics Program Code\bio-info files\\' + file)
#img = preprocess(img)
#extractData(img)
#df = pd.DataFrame(data)
#print(df)
#get-image.py
