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
            distances = lidar.getLaliveDistance()
            gc.clear()
            #find walls relative to current position
            walls = ldk.identifyWalls(distances,0,0)

if __name__ == "__main__":
    live()
