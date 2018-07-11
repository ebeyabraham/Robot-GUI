from tkinter import *
import cv2
from threading import Thread
from botutils.video import VideoStream
from botutils.video import FPS
from botutils import resize
from botutils.sensors import Sonar
import PIL.Image, PIL.ImageTk
#import RPi.GPIO as GPIO
import time
from datetime import datetime
import os

class App:
    def __init__(self, window, fps, window_title, video_source = 0):
        #Creating the Window
        self.window = window
        self.window.title(window_title)
        self.window.config(bg = "#eaeae1")
        
        #Video source
        self.video_source = video_source
        self.vid = VideoFeed()
        self.center = [200, self.vid.height//2]

        #path to save snapshots
        self.path = "Snapshots/snapshot-"

        #sensor
        self.sonar = SonarData().start()
        self.angle = 360//self.sonar.num_sensors
        #Layout
        self.left = Frame(self.window, borderwidth = 2, relief = "solid", bg = "#ccccb3")
        self.right = Frame(self.window, borderwidth = 2, relief = "solid", bg = "#ccccb3")
        self.buttons_left = Frame(self.window, borderwidth = 2, relief = "solid", bg = "#e0e0d1")
        self.buttons_right = Frame(self.window, borderwidth = 2, relief = "solid", bg = "#e0e0d1")

        self.box_left = Frame(self.left, borderwidth = 2, relief = "solid", bg = "#e0e0d1")
        self.box_right = Frame(self.right, borderwidth = 2, relief = "solid", bg = "#e0e0d1")
        self.camera_buttons = Frame(self.buttons_left, borderwidth = 2, relief = "solid", bg = "#e0e0d1")
        self.app_buttons = Frame(self.buttons_right, borderwidth = 2, relief = "solid", bg = "#e0e0d1")

        self.canvas_left = Canvas(self.box_left, width = self.vid.width, height = self.vid.height, bg = "#e0e0d1")
        self.label_left = Label(self.left, text = "Camera Feed", font = ("MS Sans", 12, "bold"), bg = "#ccccb3")
        self.canvas_right = Canvas(self.box_right, height = self.vid.height, bg = "#e0e0d1")
        self.label_right = Label(self.right, text = "Sensor Data", font = ("MS Sans", 12, "bold"), bg = "#ccccb3")
        
        #Buttons
        self.snap_button = Button(self.camera_buttons, text = "Snapshot", command = self.snapshot, font = ("MS Sans", 12,"bold"), bg = "#004080", fg = "#ffffff")
        self.exit_button = Button(self.app_buttons, text = "Exit", command = self.exit, font = ("MS Sans", 12,"bold"), bg = "#ff3333", fg = "#ffffff")

        self.left.grid(row = 0, column = 0, padx = 2, pady = 2 )
        self.right.grid(row = 0, column = 1, padx = 2, pady = 2)
        self.buttons_left.grid(row = 1, column = 0, padx = 2, pady = 2)
        self.buttons_right.grid(row = 1, column = 1, padx = 2, pady = 2)
        self.box_left.grid(row = 0, column = 0, padx = 10, pady = 10)
        self.box_right.grid(row = 0, column = 0, padx = 10, pady = 10)
        
        self.camera_buttons.grid(row = 0, column = 0, padx = 278, pady = 10)
        self.app_buttons.grid(row = 0, column = 1, padx = 170, pady = 10)

        self.snap_button.grid(row = 0, column = 4)
        self.exit_button.grid(row = 0, column = 0)

        self.canvas_left.grid(row = 0, column = 0)
        self.label_left.grid(row = 1, column = 0)
        self.canvas_right.grid(row = 0, column = 0)
        self.label_right.grid(row = 1, column = 0)

        self.delay = 5
        self.update(fps)

    def snapshot(self):
        '''
        Callback function for the snapshot button
        Saves the image to path
        '''
        ret, frame = self.vid.get_frame()
        snap = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        timestamp = "{:%Y%m%d-%H%M%S}".format(datetime.now())
        snap_path = self.path + timestamp + ".png"
        cv2.imwrite(snap_path, snap)
        print("[INFO] Saved Snapshot", snap_path)

    #the two funtions below update the Canvas class to allow to easily draw circles
    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    
    Canvas.create_circle = _create_circle

    def _create_circle_arc(self, x, y, r, **kwargs):
        if "start" in kwargs and "end" in kwargs:
            kwargs["extent"] = kwargs["end"] - kwargs["start"]
            del kwargs["end"]
        return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)
    
    Canvas.create_circle_arc = _create_circle_arc

    def update(self,fps):
        '''
        Updates the canvas in the window
        Also the FPS is updated after each execution of this function
        '''
        ret, frame = self.vid.get_frame()
        #sensor_data = self.sensor.get_data()
        self.canvas_left.delete("all")
        self.canvas_right.delete("all")
        if ret:
            fps.update()
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas_left.create_image(0, 0, image = self.photo, anchor = NW)
            self.canvas_right.create_circle(self.center[0], self.center[1], 150, outline="black", width=4)
            readings = self.sonar.readings
            num_sensors = self.sonar.num_sensors
            #print(readings)
            color = {'g':"#00cc00", 'r':"#ff3333"}
            for i in range(num_sensors):
                c = color[readings[i]]
                self.canvas_right.create_circle_arc(self.center[0], self.center[1], 150, fill=c, outline="black", width = 2, start=self.angle*i, end=self.angle*(i+1))

        self.window.after(self.delay, self.update, fps)
    
    def exit(self):
        self.vid.close()
        self.sonar.close()
        time.sleep(0.1)
        self.window.destroy()

class VideoFeed:
    '''
    Class for reading video stream
    Uses a seperate thread for the same by using the imutils library
    '''
    def __init__(self, video_source = 0):
        self.vid = VideoStream(usePiCamera = True).start()
        time.sleep(5)
        if not self.vid.isOpened():
            raise ValueError("Unable to Open Video Source", video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        '''
        Reads image from camera and returns in RGB format
        '''
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                frame = resize(frame, width = 640, height = 480)
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
        
    def close(self):
        if self.vid.isOpened():
            self.vid.release()

class SonarData:
    def __init__(self):
        self.num_sensors = 6
        self.sonars = []
        sensor1 = Sonar(echoPin = 24, trigPin = 23)
        self.sonars.append(sensor1)
        '''
        self.sonar = []
        
        #add sensors
        self.sonar.append(Sonar(echoPin = 24, trigPin = 23))
        self.sonar.append(Sonar(echoPin = 24, trigPin = 23))
        self.sonar.append(Sonar(echoPin = 24, trigPin = 23))
        self.sonar.append(Sonar(echoPin = 24, trigPin = 23))
        self.sonar.append(Sonar(echoPin = 24, trigPin = 23))
        self.sonar.append(Sonar(echoPin = 24, trigPin = 23))
        '''
        self.name = "SonarData"
        self.stopped = False
        self.readings = ['g' for i in range(self.num_sensors)]

    def start(self):
        t = Thread(target = self.getReadings, name = self.name, args = ())
        t.daemon = True
        t.start()
        return self
    
    def stop(self):
        self.stopped = True

    def getReadings(self):
        while True:
            if self.stopped:
                return
            else:    
                for i in range(0,self.num_sensors,1):
                    pos1 = i
                    #pos2 = self.num_sensors - 1 - i
                    #self.sonar[pos1].trigger()
                    #self.sonar[pos2].trigger()
                    sonar_reading1 = self.sonars[0].getDistance()
                    #sonar_reading2 = self.sonar[pos2].getDistance()
                    self.readings[pos1] = sonar_reading1
                    #self.readings[pos2] = sonar_reading2

    def close(self):
        for i in range(1):
            self.sonars[i].close()

def main():
    fps = FPS().start()
    root = Tk()
    App(root, fps, "Underwater Bot")
    root.mainloop()
    fps.stop()
    print("[INFO] elapsed time: {: .2f}".format(fps.elapsed()))
    print("[INFO] approx FPS: {: .2f}".format(fps.fps()))

if __name__ == "__main__":
    main()
