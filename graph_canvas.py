import Tkinter

class GraphCanvas(object):

    scale = 0.25

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
        a = self.scale
        self.canvas.create_rectangle(s+x*a, s-y*a, s+x*a+1, s-y*a+1)
        self.update();

    def add_line(self,x1,y1,x2,y2):
        s = self.size/2
        a = self.scale
        self.canvas.create_line(s+x1*a, s-y1*a, s+x2*a, s-y2*a, fill="red")
        self.update();

    def clear(self):
        self.canvas.delete('all')

