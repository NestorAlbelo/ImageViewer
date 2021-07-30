from ImageData import ImageData

class LoadFits():
    def __init__(self):
        print("Loading Fits file")
        self.createImageData()

    def createImageData(self):
        self.imageData = ImageData()