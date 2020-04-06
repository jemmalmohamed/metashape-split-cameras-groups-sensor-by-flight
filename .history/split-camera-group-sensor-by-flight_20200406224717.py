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

        self.label_time = QtWidgets.QLabel(
            'Minimum time between flights (min): ')
        self.spinX = QtWidgets.QSpinBox()
        self.spinX.setMinimum(1)
        self.spinX.setValue(10)

        self.chkMerge = QtWidgets.QCheckBox("Merge Chunk")
        self.spinX.setFixedSize(100, 25)

        self.btnQuit = QtWidgets.QPushButton("Cancel")
        self.btnQuit.setFixedSize(100, 23)

        self.btnP1 = QtWidgets.QPushButton("OK")
        self.btnP1.setFixedSize(100, 23)

        layout = QtWidgets.QGridLayout()  # creating layout
        layout.addWidget(self.label_time, 1, 1)
        layout.addWidget(self.spinX, 1, 2)
        layout.addWidget(self.chkMerge, 2, 1)

        layout.addWidget(self.btnP1, 3, 1)
        layout.addWidget(self.btnQuit, 3, 2)
        self.setLayout(layout)

        def proc_split(): return self.splitCamerasSensor()

        QtCore.QObject.connect(
            self.btnP1, QtCore.SIGNAL("clicked()"), proc_split)

        QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL(
            "clicked()"), self, QtCore.SLOT("reject()"))

        self.exec()

    def add_new_chunk(self, images, nb):
        doc = Metashape.app.document
        new_chunk = doc.addChunk()
        new_chunk.label = 'flight ' + str(nb)
        new_chunk.addPhotos(images)

    def splitCamerasSensor(self):
        time_between_flight = self.spinX.value() * 60
        print(time_between_flight)

        print("Import Cameras Script started...")

        # path_sahpe = '//Desktop-cmg-ws1/data_1/D_LPS/programme_PVA/projet_total.kml'

        chunk = Metashape.app.document.chunk

        print(list.count(chunk.cameras))

        shapes = chunk.shapes
        doc = Metashape.app.document
        previous_date = chunk.cameras[0].photo.meta['Exif/DateTime']
        previous_date = datetime.datetime.strptime(
            previous_date, '%Y:%m:%d %H:%M:%S')
        image_list_by_battery = []

        sorted_cameras = sorted(chunk.cameras,
                                key=lambda camera: camera.photo.meta['Exif/DateTime'])
        i = 0
        for c in sorted_cameras:

            date_camera = c.photo.meta['Exif/DateTime']
            date = datetime.datetime.strptime(
                date_camera, '%Y:%m:%d %H:%M:%S')

            sec = (date-previous_date).total_seconds()

            if(sec < time_between_flight):
                image_list_by_battery.append(c.photo.path)
                if c == sorted_cameras[-1]:
                    print('last flight')
                    i = i+1
                    self.add_new_chunk(image_list_by_battery, i)

            else:
                i = i + 1
                self.add_new_chunk(image_list_by_battery, i)
                image_list_by_battery = []

            previous_date = date

        print("Script finished!")
        self.close()
        return True


def splitCamerasSensor():
    global doc

    doc = Metashape.app.document

    app = QtWidgets.QApplication.instance()
    parent = app.activeWindow()

    dlg = SplitCameraGroupSensorByFlightDlg(parent)


label = "Custom menu/Split Cameras group sensor by Flights"
Metashape.app.addMenuItem(label, splitCamerasSensor)
print("To execute this script press {}".format(label))
