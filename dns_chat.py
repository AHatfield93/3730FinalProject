#!/usr/bin/python

import socket
import sys
import threading
import time
import signal
import base64
from scapy.all import *
from scapy.layers.dns import *

target_ip = ''
target_port = 0
listen_on = 0
msgs_to_send = []
msgs_lock = threading.Lock()

#uncomment if testing on localhost
conf.L3socket=L3RawSocket

shutdownFlag = False

def sighandler(signum, frame):
	print 'Signal Handler called with signal: %s ' % signum
	global shutdownFlag
	shutdownFlag = True
	sys.exit()

def usage():
	print 'Usage: python chat.py target_ip target_port listen_on'
	sys.exit()

def prompt():
	print "< You >: ",
	

def server_socket():
	global listen_on
	global target_port
	global shutdownFlag

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind(('0.0.0.0',listen_on))
	except:
		print 'Unable to setup local socket. Port in use'
		return

	current_chat_ip = ''

	while not shutdownFlag:
		pkts = sniff(count=1, filter='udp and (port '+str(target_port)+' or '+str(listen_on)+')')
		for packet in pkts:
			str_packet = str(packet)[96:str(packet).index('\x01',96)]
			print "\n< Them >: " + str_packet
		prompt()

	s.close()

def client_send_message(msg):
	global target_port
	global target_ip
	global listen_on

	c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	addr = (target_ip, target_port)

	pkt = Ether()/IP(src='127.0.0.1', dst=target_ip)/UDP(sport=listen_on, dport=target_port)/DNS(rd=1, qd=DNSQR(qname=msg+".i.donot.exist.com"))

	c.sendto(pkt.build(), addr)
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
