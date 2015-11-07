from lidar import Lidar
from landmark_identifier import LandmarkIdentifier
from graph_canvas import GraphCanvas

gc = GraphCanvas(800)
lidar = Lidar()
ldk = LandmarkIdentifier(gc)

def live():
    while True:
        readDistances = lidar.read()
        if readDistances:
            distances = lidar.getLatestDistance()
            gc.clear()
            #find walls relative to current position
            walls = ldk.identifyWalls(distances,0,0)

def test():
    f = open("data.json")
    data_str = f.readline()
    data_list = data_str.split(",")
    data_list = [int(e) for e in data_list]

    ldk.identifyWalls(data_list,0,0)

    from time import sleep
    while True:
        sleep(.1)
        pass

if __name__ == "__main__":
    live()
    #test()
