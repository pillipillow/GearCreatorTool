from maya import cmds
from maya import OpenMayaUI as opui
from Qt import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance


def GetMayaMainWindow():
    win = opui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr


class GearCreatorUI(QtWidgets.QDialog):
    def __init__(self):
        parent = GetMayaMainWindow()

        super(GearCreatorUI, self).__init__(parent = parent)
        self.setWindowTitle("Gear Creator")

        self.BuildUI()
        self.gear = None

    def BuildUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        gearLabel = QtWidgets.QLabel("Gear Creator")
        gearLabel.setFont(QtGui.QFont("Times", weight = QtGui.QFont.Bold))
        layout.addWidget(gearLabel)

        createBtn = QtWidgets.QPushButton("Create Gear")
        createBtn.clicked.connect(self.CreateGear)
        layout.addWidget(createBtn)

        teethBox = QtWidgets.QGroupBox("Teeth")
        teethHLayout = QtWidgets.QHBoxLayout()

        self.teethSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.teethSlider.setMinimum(5)
        self.teethSlider.setMaximum(30)
        self.teethSlider.setValue(10)
        self.teethSlider.setSingleStep(1)
        self.teethSlider.valueChanged.connect(self.ModifyTeeth)
        teethHLayout.addWidget(self.teethSlider)

        self.teethNumber = QtWidgets.QLabel("10")
        teethHLayout.addWidget(self.teethNumber)

        resetbtnT = QtWidgets.QPushButton("Reset")
        resetbtnT.clicked.connect(self.ResetTeeth)
        teethHLayout.addWidget(resetbtnT)

        teethBox.setLayout(teethHLayout)
        layout.addWidget(teethBox)

        lengthBox = QtWidgets.QGroupBox("Length")
        lenghtHLayout = QtWidgets.QHBoxLayout()

        self.lengthSpinBox = QtWidgets.QDoubleSpinBox()
        self.lengthSpinBox.setMinimum(0.05)
        self.lengthSpinBox.setMaximum(1)
        self.lengthSpinBox.setValue(0.3)
        self.lengthSpinBox.setSingleStep(0.01)
        self.lengthSpinBox.valueChanged.connect(self.ModifyLength)
        lenghtHLayout.addWidget(self.lengthSpinBox)

        resetbtnL = QtWidgets.QPushButton("Reset")
        resetbtnL.clicked.connect(self.ResetLength)
        lenghtHLayout.addWidget(resetbtnL)

        lengthBox.setLayout(lenghtHLayout)
        layout.addWidget(lengthBox)

        setBtn = QtWidgets.QPushButton("Set Gear")
        setBtn.clicked.connect(self.Set)
        layout.addWidget(setBtn)

    def CreateGear(self):
        self.gear = Gear()
        self.gear.CreateGear(teeth = self.teethSlider.value())
        cmds.select(self.gear.transform)

    def ModifyTeeth(self, teeth):
        if self.gear:
            self.gear.ChangeTeeth(teeth = teeth)

        self.teethNumber.setText(str(teeth))

    def ResetTeeth(self):
        self.ModifyTeeth(10)
        self.teethSlider.setValue(10)

    def ModifyLength(self, length):
        if self.gear:
            self.gear.ChangeLength(length = length)

    def ResetLength(self):
        self.ModifyLength(length = 0.3)
        self.lengthSpinBox.setValue(0.3)

    def Set(self):
        cmds.select(clear = True)
        self.gear = None
        self.teethSlider.setValue(10)
        self.lengthSpinBox.setValue(0.3)


class Gear(object):
    def __init__(self):
        self.transform = None
        self.node = None
        self.extrude = None

    def CreateGear(self, teeth = 10, length = 0.3):
        self.transform, self.node = cmds.polyPipe(subdivisionsAxis = teeth * 2)
        cmds.select(clear =True)

        faces = self.GetTeethFaces(teeth)
        for face in faces:
            cmds.select("%s.%s" % (self.transform, face), add = True)

        self.extrude = cmds.polyExtrudeFacet(localTranslateZ = length)[0]
        cmds.select(clear = True)

    def GetTeethFaces(self,teeth):
        spans = teeth * 2
        sideFaces = range(spans * 2, spans * 3, 2)

        faces = []
        for face in sideFaces:
            faces.append("f[%s]" % face)
        return faces

    def ChangeTeeth(self, teeth = 10):
        cmds.polyPipe(self.node, edit = True, subdivisionsAxis = teeth * 2)

        faces = self.GetTeethFaces(teeth)
        cmds.setAttr("%s.inputComponents" % self.extrude, len(faces), * faces, type = "componentList")

    def ChangeLength(self, length = 0.3):
        cmds.polyExtrudeFacet(self.extrude, edit = True, localTranslateZ = length)
