import serial, sys, time
from subprocess import PIPE, Popen
from threading import Thread
from math import sqrt

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names


#Define relevant variables
controller_port = 'COM14'
controller_rate = 9600
printer_port = 'COM5'
printer_rate = 250000

sleep_time = 0.5

home = 500
dead = 25
#define convenience methods

def enqueue_output(out, queue):
    """used to prevent blocking on reading from an empty process stdout"""
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def read_stdout(queue):
	"""to read from stdout on a process without blocking on no output"""
	try:  
		line = queue.get_nowait() # or q.get(timeout=.1)
	except Empty:
		return False
	else: # got line
		return line

def run_command(proc,command,delay):
	command = "\n" + command + "\n"
	proc.stdin.write(command)
	proc.stdin.flush()
	time.sleep(delay)

def pronsole_healthcheck(proc):
	"""Runs a m105 (temperature check) and checks all output for an "ok", returns false if ok is not found """
	run_command(proc,"m105",1)
	proc_line = 1
	while proc_line:
		proc_line = read_stdout(q)
		if "ok" in proc_line.lower():
			return True
	return False

def basic_parse(line):
	"""simple line parser for giving basic instructions, testing"""
	raw_x,raw_y = line.split(";")
	x = int(raw_x.strip())
	y = int(raw_y.strip())

	output = (0,0,0)

	if (previosvaluered - fudfactor ) < sensorvaluered < (previosvaluered + dead):
		pass
	elif x > (home + dead):
		output[0] = 10
	elif x < (output - dead):
		output[0] = -10
		
	if (home - dead ) < y < (home + dead):
		pass
	elif y > (home + dead):
		output[1] = 10
	elif y < (output - dead):
		output[1] = -10

	return output

def parse_input(line):
	"""takes a line, parses it and returns a tuple of (x,y,move_speed)"""
	raw_x,raw_y = line.split(";")

	x = float(raw_x.strip()) - 500
	y = float(raw_y.strip()) - 500

	ratio = y/x
	magnitude = sqrt(x**2 + y**2)

	#TODO this depends on indended behavior of the joystick

	#this is wrong, but only here for demonstration purposes
	return (x,y,magnitude)

def setup_printer(proc):
	run_command(proc,"G28",30) # home the printer
	run_command(proc,"G0 Z100 F5000", 30)
	run_command(proc,"G91")

#setup serial connections

#set up controller read loop
try:
	conn = serial.Serial(controller_port, controller_rate)
except serial.serialutil.SerialException:
	print "Failed to open Controller com port (%s)" % controller_port
	sys.exit(1)

#set up pronsole subprocess and non-blocking pipes
proc = Popen(['pronsole\pronsole.exe']
	 ,stdout=PIPE
	 ,stdin=PIPE
	 ,bufsize=1
	 ,close_fds=ON_POSIX)
time.sleep(5)

q = Queue()
t = Thread(target=enqueue_output, args=(proc.stdout, q))
t.daemon = True # thread dies with the program
t.start()
run_command(proc,"connect %s %s"%(port,rate))
time.sleep(3)

setup_printer()
#main loop
while True:
	if conn.isAvailible() > 0:
		line = conn.readline()
		moves = basic_parse(line)
		run_command(proc,"G0 X%d Y%d Z%d F 5000" % moves)
		time.sleep(0.25)
	else:
		time.sleep(0.25)
		

#clean up before exit
run_commmand(proc,"disconnect",0.5)
run_commmand(proc,"exit",0.5)
conn.close()
sys.exit(0)
