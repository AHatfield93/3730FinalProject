import socket
import sys
import threading
import time
import signal
import ssl

target_ip = ''
target_port = 0
listen_on = 0
msgs_to_send = []
msgs_lock = threading.Lock()
cacert=''
keyfilecert=''
certfilecert=''

shutdownFlag = False

def sighandler(signum, frame):
	print 'Signal Handler called with signal: %s ' % signum
	global shutdownFlag
	shutdownFlag = True

def usage():
	print 'Usage: python chat.py target_ip target_port listen_on certfile keyfile cacert'
	sys.exit()

def prompt():
	print "< You >: ",

def server_socket():
	global target_port
	global listen_on
	global shutdownFlag

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('0.0.0.0',target_port))
		s.listen(listen_on)

	except:
		print 'Unable to setup local socket. Port in use'
		return

	current_chat_ip = ''

	while not shutdownFlag:
		newsocket, addr = s.accept()

		connstream = ssl.wrap_socket(newsocket, server_side=True, certfile=certfilecert, keyfile=keyfilecert, ssl_version=ssl.PROTOCOL_TLSv1)
		data=connstream.recv(1024)
	
		incoming_ip = str(addr)
		if current_chat_ip == '':
			current_chat_ip = incoming_ip

#		if incoming_ip != current_chat_ip:
#			continue
		if data and data != "\n":
			print "\n< Them >: " + data
			prompt()

	connstream.close
	s.close()

def client_send_message(msg):
	global target_port
	global target_ip

	c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssl_sock = ssl.wrap_socket(c, ca_certs=cacert, cert_reqs=ssl.CERT_REQUIRED)
	ssl_sock.connect((target_ip, target_port))

	addr = (target_ip, target_port)

	c.sendto(msg, addr)
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

	if(len(sys.argv) != 7):
		usage()

	signal.signal(signal.SIGTERM, sighandler)
	signal.signal(signal.SIGINT, sighandler)

	target_ip = sys.argv[1]
	target_port = int(sys.argv[2])
	listen_on = int(sys.argv[3])
	
	certfilecert=sys.argv[4]
	keyfilecert=sys.argv[5]
	cacert=sys.argv[6]

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
