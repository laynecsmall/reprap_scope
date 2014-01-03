import sys,time
from subprocess import PIPE, Popen
from threading  import Thread

port = 'COM14'
rate = 250000
sleep_time = 0.5

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def run_command(proc,command):
	command = "\n" + command + "\n"
	print "*****\n%s\n*******" % command

	proc.stdin.write(command)
	proc.stdin.flush()
	time.sleep(sleep_time)

p = Popen(['pronsole\pronsole.exe']
	 ,stdout=PIPE
	 ,stdin=PIPE
	 ,bufsize=1
	 ,close_fds=ON_POSIX)
time.sleep(5)

q = Queue()
t = Thread(target=enqueue_output, args=(p.stdout, q))
t.daemon = True # thread dies with the program
t.start()
run_command(p,"connect %s %s"%(port,rate))
time.sleep(3)
run_command(p,"m105")

# read line without blocking
while True:
	try:  
		line = q.get_nowait() # or q.get(timeout=.1)
	except Empty:
		break
	else: # got line
		print(line)

run_command(p,"disconnect")
run_command(p,"exit")
