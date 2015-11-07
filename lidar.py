import serial

class Lidar(object):
    'class to represent vx-11 lidar'

    distances = [0] * 360
    packet = [0] * 22

    startReading = False
    packetNumber = 0
    speed = 0
    packetIndex = 0
    distanceIndex = 0

    def __init__(self, port="/dev/ttyUSB0"):
        self.port = port
        self.ser = serial.Serial(port, 115200)

    def read(self):
        if self.ser.inWaiting() > 0:
            byte = self.ser.read()
            byte = int(ord(byte))

            if self.startReading:
                if self.packetIndex == 21:
                    self.startReading = False
                    self.processEndOfPacket()
                    # let the calling function know we're done
                    return self.distanceIndex >= 359
                else:
                    self.packet[self.packetIndex] = byte
                    self.packetIndex += 1
                    return False

            if not self.startReading and byte == 0xFA:
                self.startReading = True
                self.packetIndex = 0
                self.packet[self.packetIndex] = byte
                self.packetIndex += 1
                return False

    def processEndOfPacket(self):
        newPacketNumber = self.packet[1]

        if (newPacketNumber - self.packetNumber) == 1:
            for i in range(22):
                if i == 2:
                    self.speed = self.packet[3] << 8 | self.packet[2]
                    self.speed /= 64
                elif self.isDataIndex(i):
                    self.distanceIndex = (newPacketNumber - 0xA0) * 4 + i/4 - 1
                    if self.distanceIndex >= 0 and self.distanceIndex < 360:
                        if (self.packet[i+1] & 0x80) >> 7:
                            self.distances[self.distanceIndex] = 0
                        else:
                            d = self.packet[i] | ((self.packet[i+1] & 0x3F) << 8)

                            # cap between limits
                            if d < 0 or d > 6000:
                                d = 0

                            # finally, store valid data
                            self.distances[self.distanceIndex] = d

                else:
                    #checksum, packet num, and start bit go here
                    pass

        self.packetNumber = newPacketNumber

        if self.packetNumber >= 0xF9:
            self.packetNumber = 0x9F

    def isDataIndex(self, index):
        return index == 4 or index == 8 or index == 12 or index == 16

    def checksum(self, data):
        """Compute and return the checksum as an int."""
        # group the data by word, little-endian
        data_list = []
        for t in range(10):
            data_list.append(data[2*t] + (data[2*t+1]<<8))

            # compute the checksum on 32 bits
            chk32 = 0
            for d in data_list:
                chk32 = (chk32 << 1) + d

            # return a value wrapped around on 15bits
            # and truncated to still fit into 15 bits
            # then wrap around to fit into 15 bits
            checksum = (chk32 & 0x7FFF) + (chk32 >> 15)

            # truncate to 15 bits
            checksum = checksum & 0x7FFF

            return int(checksum)

    def getLatestPacket(self):
        return self.packet

    def getLatestDistance(self):
        return self.distances
