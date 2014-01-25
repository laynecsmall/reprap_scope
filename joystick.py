import serial, sys, time
from subprocess import PIPE, Popen,check_call
from threading import Thread
from math import sqrt


try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names


#Define relevant variables
controller_port = 'COM7'
controller_rate = 9600
printer_port = 'COM5'
printer_rate = 250000

sleep_time = 0.5

home = 0
dead = 25
image_count = 0

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

def run_command(proc,command,delay=0.1):
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

def scale_function(number):
	return 0.003*number**2

def parse_input(line):
	"""simple line parser for giving basic instructions, testing"""
	raw_y,raw_x = line.split(";")
	x = int(raw_x.strip()) - 500
	y = int(raw_y.strip()) - 500

	output = [0,0,0]
	if x == -1 and y == -1:
		take_image()
		return output

	if ((home - dead ) < x < (home + dead)) and ((home - dead ) < y < (home + dead)):
		pass
	else:
		output = [scale_function(x),scale_function(y),0]

	return output

def take_image():
	global image_count
	image_path = "C:\\Image"
	image_name = "MicroscopeImage-%d" % image_count
	print "Taking snapshot: %s" % image_name
	image_count += 1
	command = "vlc.exe --dshow-vdev=\"Digital Microscope Camera\" --dshow-size=640x480 -V dummy --intf=dummy --dummy-quiet --video-filter=scene --no-audio --scene-path=%s --scene-format=jpeg --scene-prefix=%s --scene-replace --run-time=1 --scene-ratio=24 \"dshow://\" vlc://quit" % (image_path,image_name)
	proc = Popen(command,shell=True,cwd='C:\\Program Files (x86)\\VideoLAN\VLC\\')
	
def setup_printer(proc):
	run_command(proc,"G28",15) # home the printer
	run_command(proc,"G0 Z100 F5000", 15)
	run_command(proc,"G91",0.1)

#setup serial connections

#set up controller read loop
print "Setting up serial connections"
try:
	conn = serial.Serial(controller_port, controller_rate)
except serial.serialutil.SerialException:
	print "Failed to open Controller com port (%s)" % controller_port
	sys.exit(1)

#set up pronsole subprocess and non-blocking pipes
print "opening pronsole console"
proc = Popen(['pronsole\pronsole.exe']
	 ,stdout=PIPE
	 ,stderr=PIPE
	 ,stdin=PIPE
	 ,bufsize=1
	 ,close_fds=ON_POSIX)
time.sleep(5)

q = Queue()
t = Thread(target=enqueue_output, args=(proc.stdout, q))
t.daemon = True # thread dies with the program
t.start()
print "connecting to reprap via pronsole"
run_command(proc,"connect %s %s"%(printer_port,printer_rate),1)
time.sleep(3)

print "homing printer"
setup_printer(proc)
#main loop
print "entering main loop"
while True:
	if conn.inWaiting() > 0:
		line = conn.readline()
		moves = parse_input(line)
		run_command(proc,"G0 X%d Y%d Z%d F 2500" % (moves[0],moves[1],moves[2]))
		time.sleep(0.25)
	else:
		time.sleep(0.25)
		

#clean up before exit
print "exiting"
run_commmand(proc,"disconnect",0.5)
run_commmand(proc,"exit",0.5)
conn.close()
sys.exit(0)
