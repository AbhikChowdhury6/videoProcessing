import sys
import cv2
import pandas as pd
import os
from datetime import datetime

#set these in /etc/enviroment by adding the line DEVICE_NAME="testCam" for example
deviceName = os.getenv("DEVICE_NAME", "notSet")
if deviceName == "notSet":
    print("no device name set")
    sys.stdout.flush()

user = os.getenv("USER", "pi")
sys.stdout.flush()
# what do we need to do
    # keep track of how many frames there are and save a video every 1.8k frames  
    # save to a folder called deviceName-date in a folder called collectedData


# the chron job can come in and send off that folder to 
# /home/{remoteUsername}/Documents/videoData/{year-month}/ in the storage and processing server
# open chrontab for editing with chrontab -e
# run the script at 3 am ngl I'm pretty sure everyone in the house will be pretty asleep
# add the line
# 0 3 * * * /home/pi/Documents/videoProcessing/send.sh


# Define the codec and create a VideoWriter object
def writer_worker(input_queue, output_queue):
    print("in writer worker")
    sys.stdout.flush()
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    timestamps = []
    frames = []
    frameWidth = 0
    frameHeight = 0
    first = True
    startNewVideo = True
    numAddedFrames = 0
    while True:
        if startNewVideo:
            output = cv2.VideoWriter(pathToFile + "new.mp4", 
                        fourcc, 
                        30.0, 
                        (frameWidth, frameHeight))
            pathToFile = "/home/" + user + "/Documents/collectedData/" + \
                deviceName + "_" + timestamps[0].strftime('%Y-%m-%d') + "/"
            os.makedirs(pathToFile, exist_ok=True)
            
            startNewVideo = False

        newTimestmaps, newFrames = input_queue.get()  # Get frame from the input 
        timestamps.extend(newTimestmaps)
        # print(newTimestmaps)
        print(f"recived {len(newFrames)} new frames!")
        print(f"recived {len(newTimestmaps)} new timestamps!")
        sys.stdout.flush()


        if newFrames is None:  # None is the signal to exit
            print("exiting writer worker")
            sys.stdout.flush()
            output.release()
            break
        
        if len(newFrames) != len(newTimestmaps):
            continue

        if first:
            first = False
            frameWidth = int(newFrames[0].shape[1])
            frameHeight = int(newFrames[0].shape[0])
        
        if timestamps[0].tz_convert("UTC").day < timestamps[-1].tz_convert("UTC").day:
            crossesMidnight = True
            print(f"crossed midnight!")
            sys.stdout.flush()
        else:
            crossesMidnight = False

        # here add the relevant number of new frames to the output
        # and to do that we have to check if midnight has passed and how many frames we've already written
        if crossesMidnight

        timestamps.extend(newTimestmaps)
        del newFrames
        del newTimestmaps
        print(f"have {len(numAddedFrames)} total frames!")
        print(f"have {len(timestamps)} total timestamps!")
        sys.stdout.flush()

        

        if frame >= 1800 or crossesMidnight:

            if crossesMidnight:
                endIndex = len(timestamps)-1
                while timestamps[0].tz_convert("UTC").day < timestamps[endIndex-1].tz_convert("UTC").day:
                    endIndex -= 1
            else:
                endIndex = 1800
            
            print(f"attempting to write {endIndex} frames")
            sys.stdout.flush()

            
            fileName = deviceName + "_" + \
                        timestamps[0].strftime('%Y-%m-%dT%H%M%S-%f%z') + "_" + \
                        timestamps[endIndex-1].strftime('%Y-%m-%dT%H%M%S-%f%z')

            print(f"wrote {endIndex} frames to the name " + fileName)
            sys.stdout.flush()


            #save frames to a video
            writeStartTime = datetime.now()
            for frame in frames[:endIndex]:
                output.write(frame)
            output.release()
            print(f"writing took {datetime.now() - writeStartTime}")
            sys.stdout.flush()
            del writeStartTime

            leftoverFrames = frames[endIndex:]
            del frames
            frames = leftoverFrames
            del leftoverFrames
            print(f"{len(frames)} is the number of frames left")
            sys.stdout.flush()

            # also save timestamps
            tsdf = pd.DataFrame(data=timestamps[:endIndex], columns=['sampleDT'])
            tsdf = tsdf.set_index('sampleDT')
            tsdf.to_parquet(pathToFile + fileName + ".parquet")
            leftoverTimestamps = timestamps[endIndex:]
            del timestamps
            timestamps = leftoverTimestamps
            del leftoverTimestamps
            # sys.stdout.flush()


        
