import serial,sys

port = 'COM5'
rate = 9600

try:
	conn = serial.Serial(port,rate)
except serial.serialutil.SerialException: 
	print "failed to open COM port: %s" % port
	sys.exit(1)

while con.inWaiting() > 0:
	print conn.readline()

conn.close()
