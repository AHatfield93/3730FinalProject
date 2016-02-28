import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
import socket
import sys
import threading
import time
import signal

target_ip = ''
msgs_to_send = []
msgs_lock = threading.Lock()
last_sent = ''

shutdownFlag = False

def sighandler(signum, frame):
	print 'Signal Handler called with signal: %s ' % signum
	global shutdownFlag
	shutdownFlag = True

def usage():
	print 'Usage: python chat.py target_ip'
	sys.exit()

def prompt():
	print "< You >: ",

def packet_callback(packet):
	global last_sent
	if packet[ICMP].payload:
		print "PACKET_CALLBACK"
		packet.summary()
		msg = str(packet[ICMP].payload)
		try:
			msg = msg[0:msg.index('\x00')]
		except:
			msg = msg
		finally:
			if msg != "\n" and msg != last_sent:
				print "\n< Them >: " + msg
			prompt()

def server_socket():
	global target_ip
	global shutdownFlag

	filt = "host %s and icmp" % target_ip
	sniff(filter=filt, prn=packet_callback)

	while True:
		if shutdownFlag:
			break

	sys.exit(0)

def client_send_message(msg):
	global target_ip
	global last_sent

	ping = IP(dst=target_ip)/ICMP()/msg
	send(ping)
	last_sent = msg

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

	if(len(sys.argv) != 2):
		usage()

	signal.signal(signal.SIGTERM, sighandler)
	signal.signal(signal.SIGINT, sighandler)

	target_ip = sys.argv[1]

	conf.verb = 0

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
