import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import os
import csv

# https://chatgpt.com/share/f9509eb3-a41d-46d6-8c79-d45e96715504


# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Mapping dictionaries for character conversion
dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'A': '4', 'G': '6', 'S': '5', 'E':'8'}
dict_int_to_char = {'0': 'O', '1': 'I', '3': 'J', '4': 'A', '6': 'G', '5': 'S', '8':'E'}
dict_char_to_char ={'O': 'D','D':'O'}

# Append data to CSV file
headers = ["Car ID", "N1", "Conf1", "N2", "Conf2", "N3", "Conf3", "N4", "Conf4", "N5", "Conf5",
            "N6", "Conf6", "N7", "Conf7", "N8", "Conf8", "N9", "Conf9", "N10", "Conf10","Length of valid countour", "Remark", "Path"]
csv_filename = "test3.csv"

with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the headers
    writer.writerow(headers)

output_dir="NumberPlate02/Result_get"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def format_license(text,dict):
    """
    Format the license plate text by converting characters using the mapping dictionaries.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text.
    """
    if (dict):
        if (text not in dict_int_to_char) and (text not in dict_char_to_char):
            return text
        if text in dict_int_to_char:
            corrected = dict_int_to_char.get(text)
        else:
           corrected= dict_char_to_char.get(text)
    else:
        if text not in dict_char_to_int:
            return text        
        corrected = dict_char_to_int.get(text)

    return corrected

def process_image(image,count,line,Path_):
    data = [""]*24
    # print(data)

    # image=cv2.imread(license_plate_crop)

    # cv2.imshow("Plate",image)

    # Step 1: Resize the image
    resized = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(os.path.join(output_dir, '1_resized.png'), resized)

    # Step 2: Convert to grayscale if the input is not already grayscale
    if len(resized.shape) == 3:
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    else:
        gray = resized
    cv2.imwrite(os.path.join(output_dir, '2_gray.png'), gray)

    # Step 3: Apply Gaussian Blur
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.imwrite(os.path.join(output_dir, '3_blur.png'), blur)

    # Step 4: Apply median blur
    median_blurred = cv2.medianBlur(blur, 3)
    cv2.imwrite(os.path.join(output_dir, '4_median_blur.png'), median_blurred)

    # edges = cv2.Canny(median_blurred, 50, 150)
    # cv2.imwrite(os.path.join(output_dir, '4_cannyedge.png'), edges)

    # Step 5: Perform Otsu's thresholding
    ret, thresh = cv2.threshold(median_blurred, 127, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    cv2.imwrite(os.path.join(output_dir, '5_threshold.png'), thresh)

    # Step 6: Apply dilation
    rect_kern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilation = cv2.dilate(thresh, rect_kern, iterations=1)
    erosion = cv2.erode(dilation, rect_kern, iterations=1)
    cv2.imwrite(os.path.join(output_dir, '6_dilation.png'), erosion)
    

    # Step 7: Find contours
    try:
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        ret_img, contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # sorted_contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
    sorted_contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])

    # Divide contours into two rows (upper and lower)
    rows = []
    row_threshold = 15  # Adjust this threshold as needed
    current_row = [sorted_contours[0]]

    for i in range(1, len(sorted_contours)):
        x, y, w, h = cv2.boundingRect(sorted_contours[i])
        prev_x, prev_y, prev_w, prev_h = cv2.boundingRect(sorted_contours[i-1])
        
        # Check if the current contour is in the same row as the previous one
        if abs(y - prev_y) < row_threshold:
            current_row.append(sorted_contours[i])
        else:
            # Sort the current row by x-coordinates and add to rows list
            rows.append(sorted(current_row, key=lambda ctr: cv2.boundingRect(ctr)[0]))
            current_row = [sorted_contours[i]]

    # Add the last row
    rows.append(sorted(current_row, key=lambda ctr: cv2.boundingRect(ctr)[0]))

    # Flatten the list of rows to get the final sorted list of contours
    final_sorted_contours = [contour for row in rows for contour in row]
    # Create a copy of the image for drawing rectangles
    
    im2 = gray.copy()

    contour_Valid =[]
    # print (len(sorted_contours))
    for i, cnt in enumerate(final_sorted_contours):
        # print (len(sorted_contours))
        # print(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        
        height, width = im2.shape
        
        # Filtering conditions
        if height / float(h) > 4: continue
        ratio = h / float(w)
        if ratio < 1.40: continue
        area = h * w
        # if width / float(w) > 15: continue
        # if w==0 and h==0 and x==0 and y==0 : continue
        # if area < 100: continue
        # if cnt==NU: continue

        # Draw the rectangle
        # print(f"x: {x} y: {y} w: {w} h: {h}")
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi=0
        roi = thresh[y - 5:y + h + 5, x - 5:x + w + 5]
        roi = cv2.bitwise_not(roi)
        try:
            roi = cv2.medianBlur(roi, 5)
            # Save the region of interest (ROI)
            roi_filename = os.path.join(output_dir, f'{count}_roi_{i}.png')
            cv2.imwrite(roi_filename, roi)
            contour_Valid.append(roi)
        except:
             continue
    print(len(contour_Valid))
    # roi_filename = os.path.join(output_dir, f'roi_{count}.png')
    # cv2.imwrite(roi_filename,roi)
    if len(contour_Valid)>=9 and len(contour_Valid)<11:
        # readCounter(data, contour_Valid, count)
        fir_countourRec(data, contour_Valid[0])
        sec_countourRec(data, contour_Valid[1])
        third_countourRec(data, contour_Valid[2])
        last4_countourRec(data, contour_Valid[-1], 19)
        last4_countourRec(data, contour_Valid[-2], 17)
        last4_countourRec(data, contour_Valid[-3], 15)
        last4_countourRec(data, contour_Valid[-4], 13)
        last5_countourRec(data, contour_Valid[-5])
        # cv2.imwrite('Hi.jpg',contour_Valid[-5])

        if len(contour_Valid) == 9:
            middle_countourRec(data, contour_Valid[3], 9)
        elif len(contour_Valid) == 10:
            middle_countourRec(data, contour_Valid[3], 9)
            middle_countourRec(data, contour_Valid[4], 11)
        data[22]=f"At Line: {line}"
    else:
        Detect_Num(data, dilation)
        data[22]=f"Unable to read a valid license plate correctly at Line: {line}."
    
    data[0]=f"{count}"
    data[23]= Path_
    data[21]=(len(contour_Valid))
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)   
        writer.writerow(data)
    print (data)
    return  id,data


def fir_countourRec(data,roi):

        config = '-c tessedit_char_whitelist=ABCDGHJKLMNOPRSTUW --psm 6 --oem 3'
        result_data = pytesseract.image_to_data(roi, config=config, output_type=pytesseract.Output.DICT)
        
        for i in range(len(result_data['text'])):
            if int(result_data['conf'][i]) > 0:  # Filter out results with confidence '-1'
                data[1]=result_data['text'][i]
                data[2]=result_data['conf'][i]
            elif int(result_data['conf'][i]) == 0:
                data[1]=format_license(result_data['text'][i],True)
                data[2]=0

def sec_countourRec(data,roi):

        config = '-c tessedit_char_whitelist=PRSHDGLNAJKZBY --psm 6 --oem 3'

        result_data = pytesseract.image_to_data(roi, config=config, output_type=pytesseract.Output.DICT)
        # confidences.append(result_data['conf'][0])  
        # print(result_data)
        for i in range(len(result_data['text'])):
            if int(result_data['conf'][i]) >= 0:  # Filter out results with confidence '-1'
                data[3]=result_data['text'][i]
                data[4]=result_data['conf'][i]
            elif int(result_data['conf'][i]) == 0:
                data[3]=format_license(result_data['text'][i],True)
                data[4]=0

def last4_countourRec(data,roi,index):

        config = '-c tessedit_char_whitelist=0123456789 --psm 6 --oem 3'        
        result_data = pytesseract.image_to_data(roi, config=config, output_type=pytesseract.Output.DICT)
        for i in range(len(result_data['text'])):
            if int(result_data['conf'][i]) >= 0:  # Filter out results with confidence '-1'
                data[index]=result_data['text'][i]
                data[index+1]=result_data['conf'][i]
            elif int(result_data['conf'][i]) == 0:
                data[index]=format_license(result_data['text'][i],False)
                data[index+1]=0

def middle_countourRec(data,roi,index):

        config = '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6 --oem 3'
        result = pytesseract.image_to_string(roi, config=config)
        result_data = pytesseract.image_to_data(roi, config=config, output_type=Output.DICT)
        for i in range(len(result_data['text'])):
            if int(result_data['conf'][i]) >= 0:  # Filter out results with confidence '-1'
                data[index]=result_data['text'][i]
                data[index+1]=result_data['conf'][i]
            elif int(result_data['conf'][i]) == 0:
                data[index]= result
                data[index+1]=0


def last5_countourRec(data,roi):

        config = '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 6 --oem 3'
        result_data = pytesseract.image_to_data(roi, config=config, output_type=pytesseract.Output.DICT)
        # print(result_data)
        for i in range(len(result_data['text'])):
            if int(result_data['conf'][i]) >= 0:  # Filter out results with confidence '-1'
                data[11]=result_data['text'][i]
                data[12]=result_data['conf'][i]
            elif int(result_data['conf'][i]) == 0:
                data[11]=format_license(result_data['text'][i],False)
                data[12]=0

def third_countourRec(data,roi):

        config = '-c tessedit_char_whitelist=0123456789 --psm 6 --oem 3'
        result_data = pytesseract.image_to_data(roi, config=config, output_type=pytesseract.Output.DICT)
        for i in range(len(result_data['text'])):
            if int(result_data['conf'][i]) >= 0:  # Filter out results with confidence '-1'
                data[5]=result_data['text'][i]
                data[6]=result_data['conf'][i]
            elif int(result_data['conf'][i]) == 0:
                data[5]=format_license(result_data['text'][i],False)
                data[6]=0

def Detect_Num(data,roi):

        config = '-c tessedit_char_whitelist=ABCDGHJKLMNOPRSTUW012345678 --psm 8 --oem 3'
        result = pytesseract.image_to_string(roi, config=config)
        result_data = pytesseract.image_to_data(roi, config=config, output_type=pytesseract.Output.DICT)
        print(result)
        print(result_data)
        data[1] = result
        # for i in range(len(result_data['text'])):
            # if int(result_data['conf'][i]) > 0:  # Filter out results with confidence '-1'
                # data[1] = result_data['text'][i]

