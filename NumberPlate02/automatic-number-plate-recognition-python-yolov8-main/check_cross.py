

previous_positions = {}
def crosses_virtual_line(y, y_prev, line_y):
    """
    Check if a vehicle crosses the virtual line between the current and previous frame.

    Args:
        y (int): The current y-coordinate of the vehicle's bounding box.
        y_prev (int): The previous y-coordinate of the vehicle's bounding box.
        line_y (int): The y-coordinate of the virtual line.

    Returns:
        bool: True if the vehicle crosses the line, False otherwise.
    """
    # print('called*****', y_prev ,":", line_y ,":", y)
    return (y_prev < line_y <= y) or (y_prev > line_y >= y)

# def get_car_details_across_frames(results, car_id):
#     car_details = {}
#     for frame_nmr, frame_data in results.items():
#         if car_id in frame_data:
#             car_details[frame_nmr] = frame_data[car_id]
#     return car_details

def check_vehicle_crossing(track_ids, frame_nmr, line_y,line,len_line):
    # print(line_y)
    for track in track_ids:
        track_id = int(track[4])
        x1, y1, x2, y2 = track[:4]
        y_current = ((y1 + y2) / 2) +20 # Current y-coordinate of the vehicle's center
        x_current = (x1 + x2) / 2 # Current x-cordinate of vehcile's center
        
        if track_id in previous_positions :
            y_previous = previous_positions[track_id]
            if crosses_virtual_line(y_current, y_previous, line_y):
                print(f"********************************Vehicle with car ID {track_id} crossed the line{line} at frame {frame_nmr}********************")
                previous_positions[track_id] = y_current
                return (True , frame_nmr, track_id)
        if(line==len_line-1):            
            previous_positions[track_id] = y_current
    return(False,frame_nmr, -1)