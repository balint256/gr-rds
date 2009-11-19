#!/usr/bin/env python

"""
This code detects any USRPs and USRP2s connected,
identifies their daughterboards and prints their frequency range
"""

from gnuradio import usrp, usrp2
from usrpm import usrp_dbid
import subprocess

def detect_usrp1():
	print "\033[1;33mdetecting usrp's...\033[1;m"
	for i in [0,1,2,3]:
		try:
			u = usrp.source_c(i)
			print "usrp found, serial:", u.serial_number()
			a = usrp.selected_subdev(u, (0,0))
			if(a.dbid()!=-1):
				print "daughterboard a:", a.name(), "(0x%04X)" % (a.dbid())
				print "freq range: ", a.freq_min()/1e6, "MHz -", a.freq_max()/1e6, "MHz"
				print "gain rainge: ", a.gain_min(), "dB -", a.gain_max(), "dB"
			else:	print "no daughterboard on side a"
			b = usrp.selected_subdev(u, (1,0))
			if(b.dbid()!=-1):
				print "daughterboard b:", b.name(), "(0x%04X)" % (b.dbid())
				print "freq range: ", b.freq_min()/1e6, "MHz -", b.freq_max()/1e6, "MHz"
				print "gain rainge: ", b.gain_min(), "dB -", b.gain_max(), "dB"
			else:	print "no daughterboard on side b"
		except:
			print "\033[1;31mno more usrp's found\033[1;m"
			break

def detect_usrp2():
	print "\033[1;33mdetecting usrp2's...\033[1;m"
	interface = 'eth0'
	args = ['find_usrps', '-e', interface]
	p = subprocess.Popen(args=args,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			shell=False,
			universal_newlines=True)
	msg = p.stdout.read()
	usrp2_macs = sorted(map(lambda l: l.split()[0], filter(lambda l: l.count(':') >= 5, msg.strip().splitlines())))
	for usrp2_mac in usrp2_macs:
		print "usrp2 found, mac address:", usrp2_mac
		u2 = usrp2.source_32fc(interface, usrp2_mac)
		db = u2.daughterboard_id()
		if(db!=-1):
			db_name = [k for k, v in usrp_dbid.__dict__.iteritems() if v == db][0]
			print "daughterboard id:", db_name, "(0x%04X)" % (db,)
			print "freq range: ", u2.freq_min()/1e6, "MHz -", u2.freq_max()/1e6, "MHz"
		else:	print "no daughterboard connected"
	print "\033[1;31mno more usrp2's found\033[1;m"

detect_usrp1()
detect_usrp2()

