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

        self.chkMerge = QtWidgets.QCheckBox("Merge Flights Chunks")
        self.chkMerge.stateChanged.connect(self.toggleChkRemove)
        self.spinX.setFixedSize(100, 25)

        self.chkRemove = QtWidgets.QCheckBox("Remove Flights Chunks")
        self.chkRemove.setEnabled(False)
        self.spinX.setFixedSize(100, 25)

        self.btnQuit = QtWidgets.QPushButton("Cancel")
        self.btnQuit.setFixedSize(100, 23)

        self.btnP1 = QtWidgets.QPushButton("OK")
        self.btnP1.setFixedSize(100, 23)

        layout = QtWidgets.QGridLayout()  # creating layout

        layout.addWidget(self.label_time, 1, 1)
        layout.addWidget(self.spinX, 1, 2)
        layout.addWidget(self.chkMerge, 2, 1)
        layout.addWidget(self.chkRemove, 2, 2)

        layout.addWidget(self.btnP1, 3, 1)
        layout.addWidget(self.btnQuit, 3, 2)

        self.setLayout(layout)

        def proc_split(): return self.splitCamerasSensor()

        QtCore.QObject.connect(
            self.btnP1, QtCore.SIGNAL("clicked()"), proc_split)

        QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL(
            "clicked()"), self, QtCore.SLOT("reject()"))

        self.exec()

    def toggleChkRemove(self, state):

        if state > 0:
            self.chkRemove.setEnabled(True)
        else:
            self.chkRemove.setEnabled(False)

    def add_new_chunk(self, images, nb):
        doc = Metashape.app.document
        new_chunk = doc.addChunk()
        new_chunk.label = 'flight ' + str(nb)
        new_chunk.addPhotos(images)
        return new_chunk

    def splitCamerasSensor(self):
        print("Import Cameras Script started...")
        time_between_flight = self.spinX.value() * 60

        list_of_keys_new_chunk = []
        list_of_new_chunk = []

        chunk = Metashape.app.document.chunk
        print('Total photos {} : '.format(len(chunk.cameras)))

        date_previous = chunk.cameras[0].photo.meta['Exif/DateTime']
        date_previous = datetime.datetime.strptime(
            date_previous, '%Y:%m:%d %H:%M:%S')
        image_list_by_battery = []

        sorted_cameras = sorted(chunk.cameras,
                                key=lambda camera: camera.photo.meta['Exif/DateTime'])

        print('Sorted Photos by time : {}'.format(
            len(sorted_cameras)))
        i = 0
        for c in sorted_cameras:

            date_current = c.photo.meta['Exif/DateTime']
            date_current = datetime.datetime.strptime(
                date_current, '%Y:%m:%d %H:%M:%S')

            sec = (date_current-date_previous).total_seconds()

            if(sec < time_between_flight):
                image_list_by_battery.append(c.photo.path)
                if c == sorted_cameras[-1]:
                    print('last flight')
                    i = i+1
                    print('Flight {} : {} Photos'.format(
                        i, len(image_list_by_battery)))
                    new_chunk = self.add_new_chunk(image_list_by_battery, i)
                    list_of_new_chunk.append(new_chunk)
                    list_of_keys_new_chunk.append(new_chunk.key)

            else:
                image_list_by_battery.append(c.photo.path)
                i = i + 1
                print('Flight {} : {} Photos'.format(
                    i, len(image_list_by_battery)))
                new_chunk = self.add_new_chunk(image_list_by_battery, i)
                list_of_new_chunk.append(new_chunk)
                list_of_keys_new_chunk.append(new_chunk.key)
                image_list_by_battery = []

            date_previous = date_current

        if self.chkMerge.isChecked():
            print('merging flights ....')
            doc.mergeChunks(chunks=list_of_keys_new_chunk)

        if self.chkRemove.isChecked():
            print('Flights chunks removing...')
            doc.remove(list_of_new_chunk.append(new_chunk))
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
