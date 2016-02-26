import socket
import sys
import threading
import time
import signal

target_ip = ''
target_port = 0
listen_on = 0
msgs_to_send = []
msgs_lock = threading.Lock()

shutdownFlag = False

def sighandler(signum, frame):
	print 'Signal Handler called with signal: %s ' % signum
	global shutdownFlag
	shutdownFlag = True

def usage():
	print 'Usage: python chat.py target_ip target_port listen_on'
	sys.exit()

def prompt():
	print "< You >: ",

def server_socket():
	global listen_on
	global shutdownFlag

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('0.0.0.0', listen_on))
		s.listen(1)
	except:
		print 'Unable to setup local socket. Port in use'
		return

	current_chat_ip = ''

	while not shutdownFlag:
		conn, addr = s.accept()

		incoming_ip = str(addr[0])
		if current_chat_ip == '':
			current_chat_ip = incoming_ip

		if incoming_ip != current_chat_ip:
			conn.close()
		else:
			data = conn.recv(4096)
			if data != "\n":
				print "\n< Them >: " + data
				prompt()
			conn.close()

	s.close()

def client_send_message(msg):
	global target_port
	global target_ip

	c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		c.connect((target_ip, target_port))
	except:
		print 'Connection Refused'
		return

	try:
		c.send(msg)
	except Exception, e:
		print 'Connection Refused. Endpoint not connected'

	c.close()


def read_stdin():
	global msgs_to_send
	global msgs_lock
	global shutdownFlag

	prompt()
	while not shutdownFlag:
		msg = raw_input('')
		msgs_lock.acquire()
		try:
			msgs_to_send.append(msg)
		finally:
			msgs_lock.release()
			prompt()

def main():
	global target_ip
	global target_port
	global listen_on

	if(len(sys.argv) != 4):
		usage()

	signal.signal(signal.SIGTERM, sighandler)
	signal.signal(signal.SIGINT, sighandler)

	target_ip = sys.argv[1]
	target_port = int(sys.argv[2])
	listen_on = int(sys.argv[3])

	server = threading.Thread(target=server_socket)
	reader = threading.Thread(target=read_stdin)

	server.start()
	reader.start()
	
	while not shutdownFlag:
		msgs_lock.acquire()
		try:
			if len(msgs_to_send):
				client_send_message(msgs_to_send.pop(0))
		finally:
			msgs_lock.release()
		time.sleep(1)

	print 'Exiting program'
	server.join()
	reader.join()

if __name__ == '__main__':
	main()
