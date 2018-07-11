# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import time

from imutils.video import FPS

class PiVideoStream:
	def __init__(self, resolution=(640, 480), framerate=32):
		# initialize the camera and stream
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		#time.sleep(0.1)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)
		print("[INFO] Initialised Camera")
		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frameCaptured = False
		self.frame = None
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		print("[Start Camera Thread]")
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		print("[INFO] Waiting for Feed")
		fps = FPS().start()
		for f in self.stream:
			#print("[INFO] Reading Feed")
			self.frameCaptured = True
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			fps.update()
			self.rawCapture.truncate(0)
			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				fps.stop()
				#print("Thread FPS: {: .2f}".format(fps.fps()))
				return
		

	def isOpened(self):
		return self.frameCaptured

	def release(self):
		self.stop()
	
	def get(self, prop):
		res = self.camera.resolution
		if prop == cv2.CAP_PROP_FRAME_WIDTH:
			return res[0]
		else:
			return res[1]

	def read(self):
		# return the frame most recently read
		return (True,self.frame)

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
