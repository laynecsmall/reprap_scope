import serial

conn = serial.Serial('COM5',9600)
while con.inWaiting() > 0:
	print conn.readline()

conn.close()
