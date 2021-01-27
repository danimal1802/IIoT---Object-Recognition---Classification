# USAGE
# python classify_video.py --model mobilenet_v2/mobilenet_v2_1.0_224_quant_edgetpu.tflite --labels mobilenet_v2/imagenet_labels.txt

# import the necessary packages
from edgetpu.classification.engine import ClassificationEngine
from imutils.video import VideoStream
from PIL import Image
import argparse
import imutils
import time
import cv2
import time
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

# Define the scope for google sheets
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
# Import the authentication credentials for access to the google sheet
creds = ServiceAccountCredentials.from_json_keyfile_name("IIoT-Lab7-17e55d980359.json", scope)
client = gspread.authorize(creds)  # Define the google sheets client
sheet = client.open("lineartrack").sheet1 # Open the spreadsheet
num_cols = sheet.col_count         # Get column count
row = sheet.row_values(13)          # get row 3 - get a specific row
col = sheet.col_values(1)          # get column 2 - get specific column
cell = sheet.cell(10,2).value       # get row 1 and column 2 - get cell
# Write Column Headers to spreadsheet
sheet.update_cell(10,1, "DATE-TIME")
sheet.update_cell(10,2, "Detect time (ms)")
sheet.update_cell(10,3, "Object")
sheet.update_cell(10,4, "Score")
sheet.update_cell(10,5, "CE Detect Time (ms)")
sheet.update_cell(10,6, "CE Object")
sheet.update_cell(10,7, "CE Score")
for col in range(10,8):
    sheet.update_cell(2,col, "********************")

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
	help="path to TensorFlow Lite classification model")
ap.add_argument("-l", "--labels", required=True,
	help="path to labels file")
args = vars(ap.parse_args())

# initialize the labels dictionary
print("[INFO] parsing class labels...")
labels = {}

# loop over the class labels file
for row in open(args["labels"]):
	# unpack the row and update the labels dictionary
	(classID, label) = row.strip().split(" ", maxsplit=1)
	label = label.strip().split(",", maxsplit=1)[0]
	labels[int(classID)] = label

# load the Google Coral classification model
print("[INFO] loading Coral model...")
model = ClassificationEngine(args["model"])

# initialize the video stream and allow the camera sensor to warmup
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
#vs = VideoStream(usePiCamera=False).start()
time.sleep(2.0)


last_time = time.time()
# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 500 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=500)                             
	orig = frame.copy()

	frame_canny = cv2.Canny(frame, 250,255)
	#frame_canny = cv2.medianBlur(frame_canny,3) 
	orig_canny = frame_canny.copy()

	# prepare the frame for classification by converting (1) it from
	# BGR to RGB channel ordering and then (2) from a NumPy array to
	# PIL image format
	frame       = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	frame_canny = cv2.cvtColor(frame_canny, cv2.COLOR_BGR2RGB)           # Canny frame
	frame       = Image.fromarray(frame)
	frame_canny = Image.fromarray(frame_canny)                           # Canny frame

	# make predictions on the input frame
	start = time.time()
	#results = model.ClassifyWithImage(frame, top_k=1)                   # depreciated
	results = model.classify_with_image(frame, top_k=1)
	end = time.time()
	duration = (end - start)*1000					     # Calc duration	

	start_canny = time.time()                                            # Canny start
	results_canny = model.classify_with_image(frame_canny, top_k=1)      # Canny results
	end_canny = time.time()						     # Canny end 
	duration_canny = (end_canny - start_canny)*1000			     # calc Duration Canny


	# ensure at least one result was found
	if len(results) > 0:
		# draw the predicted class label, probability, and inference
		# time on the output frame
		(classID, score) = results[0]
		(classID_canny, score_canny) = results_canny[0]              # Canny ID and score
		text = "{}: {:.2f}% ({:.4f} sec)".format(labels[classID],
			score * 100, end - start)
		cv2.putText(orig, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (0, 0, 255), 2)
		current_time = time.time()
		if (classID == 2) or (classID == 3) or (classID == 4) or (classID == 5) or (classID == 6) or (classID ==7):
			#if (score > .85) and (score_canny > 0.80) and (classID == classID_canny) :		     # Lets find successes	
			if (score > .75) and ((current_time - last_time) > 2.2):		     # Lets find successes	
				
				#print("RGB Image classification", "{:.6f}".format(duration),classID,"{:.3f}".format(score),"    Canny Edge classification {:.6f}".format(duration_canny),classID_canny,"{:.3f}".format(score_canny)) 
				print("RGB Image classification", "{:.6f}".format(duration),classID,"{:.3f}".format(score))
				dt_object = str(datetime.datetime.now())
				score = float(str(score)); score_canny = float(str(score_canny)); 
				#insert_row_data = [dt_object,duration,int(str(classID)),score,duration_canny,int(str(classID_canny)),score_canny]
				insert_row_data = [dt_object,duration,int(str(classID)),score]
				sheet.insert_row(insert_row_data, 13)
				last_time = time.time()

	# show the output frame and wait for a key press
	cv2.imshow("Frame", orig)
	cv2.imshow("Frame Canny Edge", orig_canny)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
