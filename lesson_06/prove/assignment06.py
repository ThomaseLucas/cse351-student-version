"""
Course: CSE 351
Assignment: 06
Author: Thomas Lucas

Instructions:

- see instructions in the assignment description in Canvas

""" 

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

# Folders
INPUT_FOLDER = "faces"
STEP1_OUTPUT_FOLDER = "step1_smoothed"
STEP2_OUTPUT_FOLDER = "step2_grayscale"
STEP3_OUTPUT_FOLDER = "step3_edges"

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(grayscale_queue, detect_edge_queue):
    while True:
        data = grayscale_queue.get()
        if data == 'STOP':
            grayscale_queue.put('STOP')
            break
        image = data[0]
        filename = data[1]

        if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
            detect_edge_queue.put((image, filename)) # Already grayscale
        else:
            detect_edge_queue.put((cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), filename))

    detect_edge_queue.put('STOP')

# ---------------------------------------------------------------------------
def task_smooth_image(smooth_queue, grayscale_queue, kernel_size):
    while True:
        data = smooth_queue.get()
        if data == 'STOP':
            smooth_queue.put('STOP')
            break

        image = cv2.GaussianBlur(data[0], kernel_size, 0)
        grayscale_queue.put((image, data[1]))

    grayscale_queue.put('STOP')

# ---------------------------------------------------------------------------
def task_detect_edges(detect_edge_queue, output_folder, threshold1, threshold2):
    while True: 
        data = detect_edge_queue.get()
        if data == 'STOP':
            detect_edge_queue.put('STOP')
            break
        
        processed_img = data[0]
        filename = data[1]
        output_image_path = os.path.join(output_folder, filename)

        if len(processed_img.shape) == 3 and processed_img.shape[2] == 3:
            print("Warning: Applying Canny to a 3-channel image. Converting to grayscale first for Canny.")
            processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(output_image_path, processed_img)

        elif len(processed_img.shape) == 3 and processed_img.shape[2] != 1 : # Should not happen with typical images
            print(f"Warning: Input image for Canny has an unexpected number of channels: {processed_img.shape[2]}")
            cv2.imwrite(output_image_path, processed_img)

        image = cv2.Canny(processed_img, threshold1, threshold2)
        cv2.imwrite(output_image_path, image)
        

# ---------------------------------------------------------------------------
def process_images_in_folder(input_folder, curr_queue): 
    # create_folder_if_not_exists(output_folder)
    # print(f"\nProcessing images from '{input_folder}' to '{output_folder}'...")
    # processed_count = 0
    for filename in os.listdir(input_folder):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            continue

        input_image_path = os.path.join(input_folder, filename) 
        # output_image_path = os.path.join(output_folder, filename) # Keep original filename

        try:
            img = cv2.imread(input_image_path)

            curr_queue.put((img, filename))

        except Exception as e:
            print(f"Error processing file '{input_image_path}': {e}")

    curr_queue.put('STOP') #add sentinal value to this. 

    #         if img is None:
    #             print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
    #             continue

    #         if next_queue:
    #             curr_queue.put((img))
    #         else:
    #             curr_queue.put((img))

            # Apply the processing function
            # if processing_args:
            #     processed_img = processing_function(img, *processing_args)
            # else:
            #     processed_img = processing_function(img)

        #     if processing_args:
        #         processed_img = process_pool.apply_async(processing_function, args=())

        #     # Save the processed image
        #     if next_queue is None:
        #         cv2.imwrite(output_image_path, processed_img)

        #     processed_count += 1
        
    

    
    #use the queue with the pool of processes
    #have it output nothing? because it puts it into a new queue?
    #if next_queue == None, then we return from that function into the folder. That might be done in the worker function logic anyways
    #print(f"Finished processing. {processed_count} images processed into '{output_folder}'.")

# ---------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")

    smooth_queue = mp.Queue()
    grayscale_queue = mp.Queue()
    edge_detection_queue = mp.Queue()

    smoothing_processes = []
    grayscale_processes = []
    edge_processes = []

    load_args=cv2.IMREAD_GRAYSCALE

    #Create workers for smoothing
    for _ in range(2):
        smoother = mp.Process(target=task_smooth_image, args=(smooth_queue, grayscale_queue, GAUSSIAN_BLUR_KERNEL_SIZE))
        grayscaler = mp.Process(target=task_convert_to_grayscale, args=(grayscale_queue, edge_detection_queue))
        edge_detector = mp.Process(target=task_detect_edges, args=(edge_detection_queue, STEP3_OUTPUT_FOLDER, CANNY_THRESHOLD1, CANNY_THRESHOLD2))

        smoother.start()
        grayscaler.start()
        edge_detector.start()

        smoothing_processes.append(smoother)
        grayscale_processes.append(grayscaler)
        edge_processes.append(edge_detector)

    # - create the three processes groups
    # - you are free to change anything in the program as long as you
    #   do all requirements.



    # --- Step 1: Smooth Images ---
    process_images_in_folder(INPUT_FOLDER, smooth_queue)

    # # --- Step 2: Convert to Grayscale ---
    # process_images_in_folder(STEP1_OUTPUT_FOLDER, STEP2_OUTPUT_FOLDER, task_convert_to_grayscale,
    #                          grayscale_pool, # pool of processes to handel task_convert_to_grayscale()
    #                          grayscale_queue, # queue that holds commands/data for the function
    #                          edge_detection_queue) # queue that holds commands/data for the next pool

    # # --- Step 3: Detect Edges ---
    # process_images_in_folder(STEP2_OUTPUT_FOLDER, STEP3_OUTPUT_FOLDER, task_detect_edges,
    #                          edge_detection_pool, #pool of processes to handle task_detect_edges()
    #                          edge_detection_queue, # queue that holds commands/data for the function
                            #  load_args=cv2.IMREAD_GRAYSCALE,        
    #                          processing_args=(CANNY_THRESHOLD1, CANNY_THRESHOLD2),)
    
    for process in smoothing_processes:
        process.join()

    for process in grayscale_processes:
        process.join()

    for process in edge_processes:
        process.join()

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Grayscale images are in: '{STEP1_OUTPUT_FOLDER}'")
    print(f"Smoothed images are in: '{STEP2_OUTPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print('Link to faces.zip:')
        print('   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing')
    else:
        run_image_processing_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')
