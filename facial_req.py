from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import datetime
import cv2
import openpyxl

# Open the Excel workbook using openpyxl
workbook = openpyxl.load_workbook(r'D:\MINI B 1\Face recognization on attendance\attendance.xlsx')
sheet = workbook.active

# Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
# Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

# load the known faces and embeddings along with OpenCV's Haar cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

# Initialize video stream and allow the camera sensor to warm up
vs = VideoStream(src=0, framerate=10).start()
time.sleep(2.0)

# Start the FPS counter
fps = FPS().start()

# Dictionary to store the last recorded time for each face
last_recorded_time = {}

# Loop over frames from the video file stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to 500px (to speed up processing)
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    # Detect the face boxes
    boxes = face_recognition.face_locations(frame)
    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"  # if face is not recognized, then print Unknown

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)

            # If someone in your dataset is identified, print their name on the screen
            if currentname != name:
                currentname = name
                print("name", currentname)

                # Get the current time
                current_time = datetime.datetime.now()

                # Check if 24 hours have passed since the face was last recorded
                if (
                    name not in last_recorded_time
                    or (current_time - last_recorded_time[name]).total_seconds() >= 24 * 60 * 60
                ):
                    # Append data to the sheet
                    row = [name, current_time.strftime("%Y-%m-%d"), current_time.strftime("%H:%M:%S")]
                    sheet.append(row)

                    # Update the last recorded time for the face
                    last_recorded_time[name] = current_time

        # update the list of names
        names.append(name)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image - color is in BGR
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # display the image to our screen
    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF

    # quit when 'q' key is pressed
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()
    workbook.save(r'D:\MINI B 1\Face recognization on attendance\attendance.xlsx')


# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
