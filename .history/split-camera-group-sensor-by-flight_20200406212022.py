import Metashape
from PySide2 import QtGui, QtCore, QtWidgets

import datetime
import shapefile
import os


# Checking compatibility
compatible_major_version = "1.6"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(
        found_major_version, compatible_major_version))


class SplitCameraGroupSensorByFlightDlg(QtWidgets.QDialog):

    wgs = Metashape.CoordinateSystem("EPSG::4326")

    lambert = Metashape.CoordinateSystem("EPSG::26191")

    def __init__(self, parent):

        QtWidgets.QDialog.__init__(self, parent)

        self.setWindowTitle(
            "SPLIT CEMARAS CALIBRATION GROUP SENSOR BY FLIGHT , BY CMG")
        self.resize(300, 150)

        self.spinX = QtWidgets.QSpinBox()
        self.spinX.setMinimum(1)
        self.spinX.setValue(15)

        self.chkMerge = QtWidgets.QCheckBox("Merge Chunk")
        self.spinX.setFixedSize(75, 25)

        self.btnQuit = QtWidgets.QPushButton("Cancel")
        self.btnQuit.setFixedSize(200, 23)

        self.btnP1 = QtWidgets.QPushButton("OK")
        self.btnP1.setFixedSize(200, 23)

        layout = QtWidgets.QGridLayout()  # creating layout
        layout.addWidget(self.spinX, 1, 1)
        layout.addWidget(self.chkMerge, 2, 1)

        layout.addWidget(self.btnP1, 3, 1)
        self.setLayout(layout)

        def proc_split(): return self.splitCemarasSensor()

        QtCore.QObject.connect(
            self.btnP1, QtCore.SIGNAL("clicked()"), proc_split)

        QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL(
            "clicked()"), self, QtCore.SLOT("reject()"))

        self.exec()

    def create_new_sensor(self, initialSensor, chunk, label):

        sensor = chunk.addSensor()
        sensor.label = label
        sensor.bands = camera.sensor.bands
        sensor.type = Metashape.Sensor.Type.Frame
        sensor.focal_length = camera.sensor.focal_length
        sensor.height = camera.sensor.height
        sensor.width = camera.sensor.width
        sensor.pixel_size = camera.sensor.pixel_size
        calibration = Metashape.Calibration()
        calibration.width = sensor.width
        calibration.height = sensor.height

        return sensor

    def splitCemarasSensor(self):

        print("Import Cameras Script started...")

        path_sahpe = '//Desktop-cmg-ws1/data_1/D_LPS/programme_PVA/projet_total.kml'
        chunk = Metashape.app.document.chunk
        shapes = chunk.shapes
        doc = Metashape.app.document
        previous_date = chunk.cameras[0].photo.meta['Exif/DateTime']
        previous_date = datetime.datetime.strptime(
            previous_date, '%Y:%m:%d %H:%M:%S')
        image_list_by_battery = []
        for c in chunk.cameras:

            date_camera = c.photo.meta['Exif/DateTime']
            date = datetime.datetime.strptime(
                date_camera, '%Y:%m:%d %H:%M:%S')

            sec = (date-previous_date).total_seconds()

            if(sec < 300):
                image_list_by_battery.append(c.photo.path)

            else:
                new_chunk = doc.addChunk()
                print(image_list_by_battery)
                new_chunk.addPhotos(image_list_by_battery)
                new_chunk.importShapes(path_sahpe)
                image_list_by_battery = []

            previous_date = date

        # print(image_list_by_battery)

        print("Script finished!")
        return True


def splitCemarasSensor():
    global doc

    doc = Metashape.app.document

    app = QtWidgets.QApplication.instance()
    parent = app.activeWindow()

    dlg = SplitCameraGroupSensorByFlightDlg(parent)


label = "Custom menu/Split Cameras group sensor by Flights"
Metashape.app.addMenuItem(label, splitCemarasSensor)
print("To execute this script press {}".format(label))
