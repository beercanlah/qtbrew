
# For now path to ardumashtun is hard coded, sorry
import sys
sys.path.append('../ardumashtun/python')

from ardumashtun import UnoMashtun


import sys
import glob
import serial
from PyQt5 import QtGui, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
import datetime

form_class = uic.loadUiType("qt_brewery.ui")[0]                 # Load the UI

def serial_ports():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except serial.SerialException:
            pass
    return result

def logic_reader(value):
    if value == False:
        a = 'Off'
    else:
        a = 'On'
    return a

class MyWindowClass(QtGui.QMainWindow, form_class):
    connected = bool(False)
    mashtun = None
    time = 0
    #setpoint = textSetTemp.text()
    #p_value = 1
    #i_value = 1
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.ButtonPID.clicked.connect(self.ButtonPID_clicked)# Bind the event handlers
        self.ButtonHeater.clicked.connect(self.ButtonHeater_clicked)  #   to the buttons
        self.ButtonPump.clicked.connect(self.ButtonPump_clicked)
        self.ButtonConnect.clicked.connect(self.ButtonConnect_clicked)
        self.comboSerialBox.addItems(serial_ports()) #Gets a list of avaliable serial ports to connect to and adds to combo box
        #self.comboSerialBox.activated['QString'].connect(self.comboBoxActivated)
        self.label_logo.setPixmap(QPixmap("BeerCanLah_logo_red_resize.png"))
        self.textSetTemp.textChanged[str].connect(self.update_setpoint)
        self.textSetP.textChanged[str].connect(self.update_P)
        self.textSetI.textChanged[str].connect(self.update_I)
        self.plotWidget.setLabel('left', 'Temp', 'C')
        self.plotWidget.setLabel('bottom', 'Time', 'Sec')
        self.temperature_samples = []
        self.temperature_set = []
        self.timedata = []

#    def getdata(self):
#        frequency = 0.5
#        noise = random.normalvariate(0., 1.)
#        new = 10.*math.sin(time.time()*frequency*2*math.pi) + noise
#        return new
#
#    def updateplot(self):
#        self.databuffer.append( self.getdata() )
#        self.y[:] = self.databuffer
#        self.curve.setData(self.x, self.y)
#        self.app.processEvents()
#

    def update(self):
        self.plt = self.plotWidget
        self.time = self.time + 1
        #self.timedata.append(self.time)
        self.temperature_samples.append(self.mashtun.temperature)
        self.temperature_set.append(self.mashtun.setpoint)
        self.temperature = self.mashtun.temperature
        self.heater_status = self.mashtun.heater
        self.pump_status = self.mashtun.pump
        self.pid_status = self.mashtun.pid
        self.setpoint = self.mashtun.setpoint
        self.p_value = self.mashtun.p_value
        self.i_value = self.mashtun.i_value
        self.dutycycle = self.mashtun.dutycycle
        self.label_time_update.setText(str(datetime.timedelta(seconds=self.time)))
        self.label_pvalue.setText(str(self.p_value))
        self.label_ivalue.setText(str(self.i_value))
        self.label_temp_set.setText(str(self.setpoint))
        self.label_temp.setText(str(self.temperature))
        self.label_heater_status.setText(str(logic_reader(self.heater_status)))
        self.label_pump_status.setText(str(logic_reader(self.pump_status)))
        self.label_dutycycle.setText(str(self.dutycycle))
        self.plt.plot(self.temperature_samples,clear=True)
        self.plt.plot(self.temperature_set,pen='r')




        #self.iteration += 1

    def update_setpoint(self):
        setattr(self.mashtun, 'setpoint',float(self.textSetTemp.text()))

    def update_P(self):
        setattr(self.mashtun, 'p_value',float(self.textSetP.text()))

    def update_I(self):
        setattr(self.mashtun, 'i_value',float(self.textSetI.text()))

    def on_text_changed(self, string):
            QtGui.QMessageBox.information(self,"Hello!","Current String is:\n"+string)

    def update_parameter(self, parameter, value):
        setattr(self.mashtun, parameter, value)

    def ButtonPID_clicked(self):        #Event handlers for buttons
         print('clicked PID')
         self.mashtun.pid = not self.mashtun.pid



    def ButtonHeater_clicked(self):
         print('clicked Heater')
         # Turn off pid control
         if self.mashtun.pid:
            self.mashtun.pid = False

        # If heater is on turn it off by setting dutycycle to 0
        # otherwise turn it on by setting it to 100
         dutycycle = 0 if self.heater_status else 100
         self.update_parameter('dutycycle', dutycycle)

    def ButtonPump_clicked(self):
         self.mashtun.pump = not self.mashtun.pump
         print('clicked Pump')

    def textInput(self,setTemp,setP,setI):
        print(float(self.textSetTemp.text()))

    def ButtonConnect_clicked(self,connection):
        if not self.connected:
            self.mashtun = UnoMashtun(str(self.comboSerialBox.currentText()))
            self.timer = QTimer()
            self.connected = True
            self.timer.timeout.connect(self.update)
            self.timer.start(1000)
            self.control_label.setText('connected to ' + str(self.comboSerialBox.currentText()))





#print serial_ports()
app = QtGui.QApplication(sys.argv)
#plot = pg.PlotWidget()
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
