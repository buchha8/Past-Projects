#Alexander Buchholz
#CPE645
#Final Project
#ObjectCapture.py

#This program takes a screenshot of the monitor, attempts to match a template with the screenshot, and displays all locations that
#are likely to be a match. In this case, the program searches the screenshot for the letters "h" and "H". The program will continue to
#capture, template match, and display results in real time. I chose this project for myself because I was interested in creating a toolset
#for real-time object detection with real-time feedback, but I also wanted to try and match objects that would result in many false positives, 
#such as letters of the alphabet. The program can still be improved in several ways, since it runs a bit slow, sometimes misses objects, and
#still sometimes captures false positives, but overall I learned a lot and I am satisfied with the results.

#To write this code, I referenced Adrian Rosebrook's tutorial on multi-scale template matching, as well as the OpenCV Python Documentation.
#Adrian Rosebrook: https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
#OpenCV documentation: https://docs.opencv.org/3.1.0/index.html

import mss
import cv2
import numpy
from win32api import GetSystemMetrics
import os


def captureMatches(img, img_threshhold, template, threshhold, color):
	#Template matching of the template and threshholded image based on correlation
	match = cv2.matchTemplate(img_threshhold, template, cv2.TM_CCOEFF)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)

	#Template matching of the template with itself
	self_match = cv2.matchTemplate(template, template, cv2.TM_CCOEFF)
	self_min_val, self_max_val, self_min_loc, self_max_loc = cv2.minMaxLoc(self_match)
	
	min_thresh= max_val * threshhold

	#Takes locations where match template had a high correlation with the threshholded image
	match_locations = numpy.where(match>=min_thresh)

	w, h = template.shape[::-1]

	#if the highest correlation is almost as high as the self correlation, assume that the match is not a false positive
	if(max_val>self_max_val*0.90):
		#For each match with high correlation, draw a colored rectangle onto the original screenshot
		for (x, y) in zip(match_locations[1], match_locations[0]):
			cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
	return

#Returns a new image scaled by a factor of scale
def resizeImg(img, scale):
	w, h = img.shape[::-1]
	img_resized = cv2.resize(img, (int(w*scale),int(h*scale)))
	return img_resized

if __name__ == "__main__":
	with mss.mss() as sct:
		#Defines the locations where screenshot should be grabbed, based on system resolution
		monitor = {"top": 0, "left": 0, "width": GetSystemMetrics(0), "height": GetSystemMetrics(1)}

		lowerH = cv2.imread('lowerH.png',0)
		upperH = cv2.imread('upperH.png',0)
		lowerH_inv = cv2.bitwise_not(lowerH)
		upperH_inv = cv2.bitwise_not(upperH)
		lower_template = lowerH
		upper_template = upperH

		while True:
			#Takes screenshot, converts to grayscale, then threshholds the image to black-and-white.
			img = numpy.array(sct.grab(monitor))
			img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			_, thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)

			#Inverts the colors of the template if screen is bright
			if cv2.mean(img_gray)[0] > 127:
				lower_template = lowerH_inv
				upper_template = upperH_inv
			else:
				lower_template = lowerH
				upper_template = upperH

			#scale each template to 20 different sizes, ranging from 0.4 times the template size to a 1.0 template size
			for scale in numpy.linspace(0.4, 1, 20)[::-1]:
				#for each scale, resize the template and use the "thresh" image to find matches. Draw rectangles onto the original image
				captureMatches(img, thresh, resizeImg(lower_template, scale), .95, (255,0,0))
				captureMatches(img, thresh, resizeImg(upper_template, scale), .90, (0,255,0))

			#Display the original screenshot with rectangles drawn on top
			cv2.imshow("H Capture", img)

			#Closes the program if "q" is pressed
			if cv2.waitKey(10) & 0xFF == ord("q"):
				cv2.destroyAllWindows()
				break