from sklearn import linear_model
from lidar import Lidar
from graph_canvas import GraphCanvas
import math

class LandmarkIdentifier(object):
    "handle series of transforms from raw data to walls and landmarks"

    T = 5
    INTERCEPT_THRESHOLD = 1
    SLOPE_THRESHOLD = .1
    min_points = 2

    def __init__(self, gc):
        self.gc = gc
        self.lines = []
        self.reg = linear_model.LinearRegression()

    def identifyWalls(self,radius, x, y):
        #note where we are in the world frame
        self.x = x
        self.y = y
        # recursively split data into "walls"

        #first turn polar into x,y
        angles = range(360)

        xs = []
        ys = []

        #reset some stuff
        self.lines = []

        for i in range(360):
            d = radius[i]
            t = angles[i] * math.pi / 180
            if (d != Lidar.INVALID_DISTANCE):
                x = math.cos(t)*d
                y = math.sin(t)*d
                xs.append(x)
                ys.append(y)

                #scale for displaying
                x *= 0.2
                y *= 0.2

        self.data = zip(xs,ys) # gives us list of tuples
        self.split(self.data)

#        for line in self.lines:
#            self.graph_trendline(line)

        self.merge()

        for line in self.lines:
            self.graph_trendline(line)

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
                line = (self.reg.coef_[0], self.reg.intercept_, current_data)
                self.lines.append(line)

    def merge(self):
        print "starting with ", len(self.lines), "lines"
        l = len(self.lines)
        i = 0
        while (i<l-1):
            line1 = self.lines[i]
            line2 = self.lines[i+1]

            d_slope = line1[0] - line2[0]
            d_intercept = line1[1] - line2[1]

            if abs(d_slope) < self.SLOPE_THRESHOLD and abs(d_intercept) < self.INTERCEPT_THRESHOLD:
                #merge da lines
                merged_data = line1[2] + line2[2]
                self.fitPoints(merged_data)
                index, distance = self.farthestPointFromLine(merged_data)

                if (distance < self.T):
                    merged_line = (self.reg.coef_[0],
                            self.reg.intercept_,
                            merged_data)
                    self.lines[i] = merged_line
                    self.lines.remove(line2)
                    break;
            i+=1

        for j in range(i,l-1):
            self.lines.pop()

        print "trimmed down to ", len(self.lines), "lines"

    def graph_trendline(self, line):
        lx1 =line[2][0][0]*.2
        ly1 = (line[0]*line[2][0][0] + line[1])*0.2
        lx2 = line[2][-1][0]*.2
        ly2 = (line[0]*line[2][-1][0] + line[1])*0.2
        self.gc.add_line(lx1,ly1,lx2,ly2)

    def createLandmark(self):
        m1 = self.reg.coef_[0]
        b1 = self.reg.intercept_

        b2 = self.y + 1/m1 * self.x
        x2 = (b2 - b1)/(m1 + 1/m1)
        y2 = m1 * x2 + b1
        return (x2,y2)

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

        x = max_p[0]*0.2
        y = max_p[1]*0.2
        #self.gc.add_point(x,y)
        return max_i, max_error
