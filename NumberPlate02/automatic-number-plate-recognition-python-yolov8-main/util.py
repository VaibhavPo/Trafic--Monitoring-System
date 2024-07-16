
import time
# import pandas as pd



def get_car(license_plate, vehicle_track_ids):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break

    if foundIt:
        return vehicle_track_ids[car_indx]

    return -1, -1, -1, -1, -1

def get_time():  

    # Get the current time as a timestamp
    timestamp = time.time()
    # Convert the timestamp to a formatted time string
    time_=time.strftime("%Y%m%d-%H_%M_%S", time.localtime(timestamp))
    print(time_)
    return time_

def output_Result(new_data,Input_data):
    if new_data[0] not in Input_data:
        Input_data[new_data[0]] = new_data

    else:
        
        old_data = Input_data[new_data[0]] 
        for j in range (2,21,2):
            try:
                if int(old_data[j]) <= int(new_data[j]) or old_data[j] == '':
                    old_data[j] = new_data
                    old_data[j-1] = new_data[j-1]
            except:
                if old_data[j] == '':
                    old_data[j] = new_data
                    old_data[j-1] = new_data[j-1]

        if 'At line:' in new_data[22]:
            old_data[23] = new_data[23]
            # old_data[22] = new
        Input_data[new_data[0]] = old_data
    return Input_data

def parseNo (Input_data, id):
    data = Input_data[f'{id}']
    res_ = [""]*5
    res_[0] = id
    number=''
    for j in range (1,20,2):
        number = number + data[j]
    res_[1] = number

    # Extract the timestamp part from the filename
    timestamp_str = (data[23]).split('.')[0].split('/')[2]
    res_[2] = parse_timestamp(timestamp_str)
    res_[3] = data[23]
    res_[4]= data[22]

    
    return res_


def parse_timestamp(timestamp_str):
    # print(timestamp_str)
    # Split the timestamp string into date, time, and frame rate components
    date_str, rest = timestamp_str.split('-', 1)  # Split at first dash only
    time_str, frame_rate = rest.rsplit('_', 1)    # Split at last underscore
    
    time_str = time_str.replace('_', ':')  # Replace underscores with colons for time part
    
    # Construct a time struct
    time_struct = time.strptime(date_str + '-' + time_str, '%Y%m%d-%H:%M:%S:%f')
    
    # Format the time struct as per the desired format, adding the frame rate
    formatted_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time_struct) + f'Frame: {frame_rate}'
    
    return formatted_timestamp


# print(parse_timestamp('20240716-00_02_50_36_3'))

