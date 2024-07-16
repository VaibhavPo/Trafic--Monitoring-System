from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Button, PhotoImage
from ultralytics import YOLO
import cv2
from sort.sort import *
from util import get_car, get_time, parseNo, output_Result
from readPlateImg2 import *
from check_cross import check_vehicle_crossing
import tkinter as tk
from queue import Queue
import threading
from PIL import Image, ImageTk
import numpy as np  # Make sure to import numpy
from Setfirebase import update_data

# Global variable to control the main loop
ret = True
# value=0
def open_file(rel_path):
    full_path = os.path.abspath(os.path.join(os.getcwd(), rel_path))
    if os.path.exists(full_path):
        os.startfile(full_path)
    else:
        tk.messagebox.showerror("Error", f"File not found: {rel_path}")


def mainFun(value,table_update_queue, frame_update_queue):
    global ret  # Declare ret as global to modify it inside the function
    # global file_get
    results = {}
    result_ = {}
    Number_Plate = {}
    mot_tracker = Sort()
    print(value)
    # load models
    coco_model = YOLO('yolov8n.pt')
    license_plate_detector = YOLO('NumberPlate02/automatic-number-plate-recognition-python-yolov8-main/models/best2.pt')

    # load video
    cap = cv2.VideoCapture(f'{value}')

    vehicles = [2, 3, 5, 7]

    VIRTUAL_LINE_Y = [100,300, 310, 320, 330,360, 380]

    # read frames
    frame_nmr = -1
    
    while ret:
        frame_nmr += 1
        ret, frame = cap.read()
        if ret :
            results[frame_nmr] = {}
            # detect vehicles
            detections = coco_model(frame)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    detections_.append([x1, y1, x2, y2, score])
            # Check detections before tracking
            if len(detections_) == 0:
                detections_ = np.empty((0, 5))
            # track vehicles
            track_ids = mot_tracker.update(np.asarray(detections_))
            # print(f"Frame {frame_nmr}: Detected {len(track_ids)} vehicles")

            for line in range(len(VIRTUAL_LINE_Y)):
                cv2.line(frame, (0, VIRTUAL_LINE_Y[line]), (1600, VIRTUAL_LINE_Y[line]), color=(255, 255, 255), thickness=1)
                crossed, at, byId = check_vehicle_crossing(track_ids, frame_nmr, VIRTUAL_LINE_Y[line], line, len(VIRTUAL_LINE_Y))

                # detect license plates
                if crossed:
                    print('Yes')
                    plateDetected = False
                    license_plates = license_plate_detector(frame)[0]
                    for license_plate in license_plates.boxes.data.tolist():
                        x1, y1, x2, y2, score, class_id = license_plate
                        
                        # assign license plate to car
                        xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
                        
                        if car_id != -1 and car_id == byId:
                            # crop license plate
                            license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]
                            # process license plate
                            print('Plate detected')
                            time_ = get_time()
                            # table_update_queue.put(Number_Plate.copy())
                            frame_update_queue.put(license_plate_crop.copy())  # Send frame to queue for update in GUI
                            
                            if (int(car_id)) in Number_Plate:  
                                get = Number_Plate[int(car_id)] 
                                get[4] = 'Number Plate Detected' 
                            else:
                                Number_Plate[int(car_id)] = ['']*5
                                get = Number_Plate[int(car_id)] 
                                get[4] = 'Number Plate Detected' 


                            cv2.imwrite(f"NumberPlate02/NumberC/{time_}_{frame_nmr}_{car_id}.png", license_plate_crop)
                            a_id, b_data = process_image(license_plate_crop, car_id, line, f"NumberPlate02/NumberC/{time_}_{frame_nmr}_{car_id}.png")
                            result_ = output_Result(b_data, result_)
                            Number_Plate[car_id] = parseNo(result_, car_id)
                            # print(Number_Plate)

                            # Number_Plate[int(car_id)] = get
                            plateDetected = True
                    
                        if not plateDetected:
                            time_ = get_time()
                            cv2.imwrite(f"NumberPlate02/NotDetected/{time_}_{frame_nmr}.png", frame)
                            print('Number plate not detected.')
                            if (int(car_id)) in Number_Plate:  
                                get = Number_Plate[int(car_id)] 
                                get[4] = 'Number Plate Not Detected' 
                            else:
                                Number_Plate[int(car_id)] = ['']*5
                                get = Number_Plate[int(car_id)] 
                                get[4] = 'Number Plate Not Detected' 
                            Number_Plate[int(car_id)] = get
                        

            # frame_update_queue.put(frame.copy())  # Send frame to queue for update in GUI
            # Display or save the frame with visualizations
            table_update_queue.put(Number_Plate.copy())
            update_data(Number_Plate)
            # Create a named window with the option to resize
            cv2.namedWindow('Video Feed', cv2.WINDOW_NORMAL)
            # Set the window size
            cv2.resizeWindow('Video Feed', 600, 300)  # Width = 800, Height = 600
            # Display the image in the resized window
            cv2.imshow('Video Feed', frame)
            # cv2.imshow('Frame', frame)
            cv2.waitKey(1)  # Adjust waitKey value as needed for display speed

    print(result_)
    print("\n", Number_Plate)

def update_frame(frame):
    # Convert the image from OpenCV to PIL format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)

    # Update the image in the label
    frame_label.imgtk = imgtk
    frame_label.configure(image=imgtk)

def update_table(data):
    # Clear existing table content
    for widget in table_frame.winfo_children():
        widget.destroy()

    # Create headers
    col_widths = [5, 12, 23, 10, 30]
    headers = ['ID', 'Number', 'Time&Frame', 'Path', 'Remark']

    header_frame = tk.Frame(table_frame, bg="#B17DBA")
    header_frame.pack(fill=tk.X)

    for col, header in enumerate(headers):
        header_label = tk.Label(header_frame, text=header, bg="#B17DBA", bd=0, relief=tk.SOLID, width=col_widths[col])
        header_label.pack(side=tk.LEFT, padx=1)


    # Display data rows
    for key, values in data.items():
        row_frame = tk.Frame(table_frame, bg="#C9BAE5")
        row_frame.pack(fill=tk.X)

        id_label = tk.Label(row_frame, text=key, bd=0, relief=tk.SOLID, width=col_widths[0])
        id_label.pack(side=tk.LEFT)

        for col, value in enumerate(values, start=0):
            if col == 3:  # Path column
                path_label = tk.Label(row_frame, text='OpenFile', bg="#C7BAE5", bd=1, relief=tk.SOLID, width=col_widths[col], cursor="hand2")
                path_label.pack(side=tk.LEFT, pady=2)
                # path_val= 
                path_label.bind("<Button-1>", lambda event, path=value: open_file(path))
            elif col == 0:
                value_label = tk.Label(row_frame, text=value, bd=0, relief=tk.SOLID, width=3)
                # value_label.pack(side=tk.LEFT, padx=0,pady=2)
            else:
                value_label = tk.Label(row_frame, text=value, bd=0, relief=tk.SOLID, width=col_widths[col])
                value_label.pack(side=tk.LEFT, pady=2)

    # Update window layout

    # Update window layout
    table_frame.grid(row=1, column=0, sticky='nsew')
    window.update_idletasks()  # Ensure tkinter updates the window

def start_main_process():
    global file_get
    global ret
    ret = True
    get_entry_value()
    value = file_get.get()
    table_update_queue = Queue()
    frame_update_queue = Queue()  # Create the frame update queue
    # Create a thread for mainFun
    thread = threading.Thread(target=mainFun, args=(value,table_update_queue, frame_update_queue))
    thread.start()

    # Start checking the queue for updates in GUI
    window.after(1000, check_queues, table_update_queue, frame_update_queue)

def stop_main_process():
    global ret
    ret = False

# Function to retrieve and print the value
def get_entry_value():
    global value 
    value= file_get.get()
    print("Entered Value:", value)

def check_queues(table_queue, frame_queue):
    while table_queue.qsize() > 0:
        data = table_queue.get()
        update_table(data)
    while frame_queue.qsize() > 0:
        frame = frame_queue.get()
        update_frame(frame)
    window.after(1000, check_queues, table_queue, frame_queue)

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"D:\New folder (5)\xamp\htdocs\TrafficCongestion\GUI_Win\build\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()

window.geometry("1000x800")
window.configure(bg = "#2A2F4F")

canvas = Canvas(
    window,
    bg = "#2A2F4F",
    height = 750,
    width = 1000,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    335.0,
    497.0,
    image=image_image_1
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    819.0,
    333.0,
    image=image_image_2
)

image_image_3 = PhotoImage(
    file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    335.0,
    261.0,
    image=image_image_3
)

image_image_4 = PhotoImage(
    file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    56.0,
    261.0,
    image=image_image_4
)

canvas.create_text(
    85.0,
    244.0,
    anchor="nw",
    text="Detections",
    fill="#F2ECEC",
    font=("IstokWeb Bold", 24 * -1)
)

image_image_5 = PhotoImage(
    file=relative_to_assets("image_5.png"))
image_5 = canvas.create_image(
    819.0,
    261.0,
    image=image_image_5
)

image_image_6 = PhotoImage(
    file=relative_to_assets("image_6.png"))
image_6 = canvas.create_image(
    697.0,
    262.0,
    image=image_image_6
)

canvas.create_text(
    725.0,
    244.0,
    anchor="nw",
    text="Plate",
    fill="#F7EFEF",
    font=("IstokWeb Bold", 24 * -1)
)

image_image_7 = PhotoImage(
    file=relative_to_assets("image_7.png"))
# image_7 = canvas.create_image(
#     709.0,
#     163.0,
#     image=image_image_7
    
# )

image_image_8 = PhotoImage(
    file=relative_to_assets("image_8.png"))
image_8 = canvas.create_image(
    833.0,
    731.0,
    image=image_image_8
)

image_image_9 = PhotoImage(
    file=relative_to_assets("image_9.png"))
# image_9 = canvas.create_image(
#     873.0,
#     163.0,
#     image=image_image_9
# )

image_image_10 = PhotoImage(
    file=relative_to_assets("image_10.png"))
image_10 = canvas.create_image(
    182.0,
    163.0,
    image=image_image_10
)

image_image_11 = PhotoImage(
    file=relative_to_assets("image_11.png"))
image_11 = canvas.create_image(
    78.0,
    161.0,
    image=image_image_11
)

image_image_12 = PhotoImage(
    file=relative_to_assets("image_12.png"))
image_12 = canvas.create_image(
    442.0,
    163.0,
    image=image_image_12
)

image_image_13 = PhotoImage(
    file=relative_to_assets("image_13.png"))
image_13 = canvas.create_image(
    500.0,
    31.0,
    image=image_image_13
)

canvas.create_text(
    86.0,
    27.0,
    anchor="nw",
    text="DASHBOARD",
    fill="#000000",
    font=("Inter Bold", 32 * -1)
)

image_image_14 = PhotoImage(
    file=relative_to_assets("image_14.png"))
image_14 = canvas.create_image(
    43.0,
    34.0,
    image=image_image_14
)
window.resizable(False, False)

file_get=tk.StringVar()
# table_frame = tk.Frame(window)
# table_frame.grid(row=1, column=0, sticky='nsew')

table_frame = tk.Frame(window, bg="#C9BAE5", bd=0, relief=tk.SOLID)
table_frame.grid(row=0, column=0, sticky='nsew', padx=40, pady=280) 


file_entry= tk.Entry(window,  textvariable=file_get)
file_entry.place(x=350, y=150)

# Create a Label to display the video frames
frame_label = tk.Label(window, bg="#2A2F4F")
frame_label.place(x=700, y=310)  # Adjust the position as needed

# Create buttons for start and stop
start_button = Button(
    window,
    image=image_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=start_main_process,
    relief="flat"
)
start_button.place(x=640, y=150)

stop_button = Button(
    window,
    image=image_image_9,
    borderwidth=0,
    highlightthickness=0,
    command=stop_main_process,
    relief="flat"
)
stop_button.place(x=800, y=150)

window.mainloop()
