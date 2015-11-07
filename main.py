import pdb
import json
import Tkinter
import math
from sklearn import linear_model

class GraphCanvas(object):

    def __init__(self, size):
        self.size = size
        self.window = Tkinter.Tk()
        self.canvas = Tkinter.Canvas(self.window,width=size,height=size)
        self.canvas.create_line(0, self.size/2, self.size, self.size/2)
        self.canvas.create_line(self.size/2, 0, self.size/2, self.size)

    def update(self):
        self.canvas.pack()
        self.window.update()

    def add_point(self,x,y):
        s = self.size/2
        self.canvas.create_rectangle(s+x, s-y, s+x+1, s-y+1)
        self.update();

    def add_line(self,x1,y1,x2,y2):
        s = self.size/2
        self.canvas.create_line(s+x1, s-y1, s+x2, s-y2, fill="red")
        self.update();

class LandmarkIdentifier(object):
    "handle series of transforms from raw data to walls and landmarks"

    T = 15
    min_points = 3

    def __init__(self):
        self.lines = []
        self.reg = linear_model.LinearRegression()

    def identifyWalls(self,radius):
        # recursively split data into "walls"

        #first turn polar into x,y
        angles = range(360)

        xs = []
        ys = []

        for i in range(360):
            t = angles[i] * math.pi / 180
            d = radius[i]
            x = math.cos(t)*d
            y = math.sin(t)*d
            xs.append(x)
            ys.append(y)

            #scale for displaying
            x *= 0.2
            y *= 0.2

        self.data = zip(xs,ys) # gives us list of tuples
        self.split(self.data)

    def split(self, current_data):
        midpoint = len(current_data)/2

        # data is list of two-tuples
        if (len(current_data) > self.min_points):
            self.fitPoints(current_data)
            index, distance = self.farthestPointFromLine(current_data)

            if (abs(distance) > self.T):
                firstHalf = current_data[:midpoint]
                secondHalf = current_data[midpoint+1:]

                self.split(firstHalf)
                self.split(secondHalf)
            else:
                # cool, we found a good enough line
                self.lines.append(current_data)
                print "fit line to eq:", self.reg.coef_[0], self.reg.intercept_
                x1 = current_data[0][0]*.2
                y1 = current_data[0][1]*.2
                x2 = current_data[-1][0]*.2
                y2 = current_data[-1][1]*.2
                gc.add_line(x1,y1,x2,y2)

    def fitPoints(self, current_data):
        # data is list of two-tuples
        # return some form of a line
        x = [[p[0]] for p in current_data]
        y = [p[1] for p in current_data]

        self.reg.fit(x,y)

    def farthestPointFromLine(self,current_data):
        # data is list of two-tuples
        # takes some form of a line
        max_error = 0
        i = 0
        max_i = 9
        max_p = (0,0)
        for point in current_data:
            fy = self.reg.coef_[0] * point[0] + self.reg.intercept_
            error = point[1] - fy

            if (abs(error) > max_error):
                max_error = error
                max_i = i
                max_p = point

            i += 1

        print "max error:", max_error, max_i
        x = max_p[0]*0.2
        y = max_p[1]*0.2
        gc.add_point(x,y)
        return max_i, max_error

gc = GraphCanvas(800)

def test():

    f = open("data.json")
    data_str = f.readline()
    data_list = data_str.split(",")
    data_list = [int(e) for e in data_list]

    gc.update()

    ldk = LandmarkIdentifier()
    ldk.identifyWalls(data_list)

    from time import sleep
    while True:
        sleep(.1)
        pass

if __name__ == "__main__":
    test()
