import cv2
import numpy as np
import os
import re
import time

def find_image_in_image(template, target):

    # Initialize a list of scales to consider for template matching
    scales = np.linspace(0.2, 1.0, 20)[::-1]

    best_match = None
    best_scale = 0
    best_top_left = (0, 0)
    best_bottom_right = (0, 0)

    for scale in scales:
        resized_template = cv2.resize(template, None, fx=scale, fy=scale)
        h, w = resized_template.shape[:2]

        # Perform template matching
        result = cv2.matchTemplate(target, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if best_match is None or max_val > best_match:
            best_match = max_val
            best_scale = scale
            best_top_left = max_loc
            best_bottom_right = (best_top_left[0] + w, best_top_left[1] + h)

    return best_top_left, best_bottom_right

def generate_frames_from_region(image, middleimage, top_left, bottom_right, num_frames,output_video):
    height, width, _ = image.shape

    # Calculate step sizes for x and y
    step_x1 = top_left[0] / (num_frames+1)
    step_x2 = (width - bottom_right[0]) / (num_frames+1)
    step_y1 = top_left[1] / (num_frames+1)
    step_y2 = (height - bottom_right[1]) / (num_frames+1)

    
    for i in range(num_frames ):
        x1 = max(0, int(top_left[0] - (i+1) * step_x1))
        y1 = max(0, int(top_left[1] - (i+1) * step_y1))
        x2 = min(width, int(bottom_right[0] + (i+1) * step_x2))
        y2 = min(height, int(bottom_right[1] + (i+1) * step_y2))
        
        frame = cv2.resize(image[y1:y2, x1:x2], (width, height))

        #calulate a new top_left and new bottom_right that fit with previous zoom we apply to frame

     
        """
        if (middleimage is not None):

            # Calculate scaling factors
            scale_x = width / (x2 - x1)
            scale_y = height / (y2 - y1)
            

            # Calculate new coordinates in the resized frame
            sx1 = int((top_left[0]-x1) * scale_x)
            sy1 = int((top_left[1]-y1) * scale_y)
            sx2 = int((bottom_right[0]-x1) * scale_x)
            sy2 = int((bottom_right[1]-y1) * scale_y)

            middleimage = cv2.resize(middleimage, (sx2 -sx1, sy2 - sy1), interpolation=cv2.INTER_AREA)

            #copy middleimage to frame at sx1,sy1
          

            frame[sy1:sy2, sx1:sx2] = middleimage
        """



       
        output_video.write(frame)
        
        cv2.imshow('Generated Frame', frame)
        cv2.waitKey(100)  #

    


def get_image_filenames_sorted(directory):
    image_files = [os.path.join(root, filename) for root, dirs, files in os.walk(directory) for filename in files if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    def extract_number(filename):
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else -1

    sorted_images = sorted(image_files, key=extract_number)

    return sorted_images


files = get_image_filenames_sorted('project_9')

image = cv2.imread(files[0], cv2.IMREAD_COLOR)
height, width, _ = image.shape
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_video = cv2.VideoWriter('output_video_9.mp4', fourcc, 30, (width, height))

previous_image = None
for file in files:
    image = cv2.imread(file, cv2.IMREAD_COLOR)
    if previous_image is not None:
        top_left, bottom_right = find_image_in_image(previous_image, image)
    else: #first image ... make same zoom out as the next one
        tempiamge = cv2.imread(files[1], cv2.IMREAD_COLOR)
        top_left, bottom_right = find_image_in_image(image, tempiamge) 
    

    generate_frames_from_region(image, previous_image, top_left, bottom_right,60,output_video)
    previous_image = image
    print('Generated frames for {}'.format(file))

output_video.release()

#ffmpeg -i output_video_4.mp4 -vf reverse -af areverse output_video_4_r.mp4



