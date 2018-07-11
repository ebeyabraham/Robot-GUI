# Robot-GUI
GUI made as part of internship at Genrobotics
![screenshot](https://user-images.githubusercontent.com/15849927/42568367-807b6a14-852a-11e8-9c7f-73389a429e4c.png)

## Dependencies
- OpenCV 3.4.0
- Tkinter 8.6
- Raspbery Pi 3

## Usage
- Before running the code, connect a picamera to your Pi and connect a HC-SR04 sensor with echo pin at pin number 24 and trigger at pin number 23

- Execute the main program
```bash
python main.py
```

## References
The botutils package that is used to interface the camera and the sensor is based on the [imutils](https://github.com/jrosebr1/imutils) package by Adrian Rosebrock
