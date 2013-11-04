#!/usr/bin/env python

"""
This code detects any USRPs and USRP2s connected,
identifies their daughterboards and prints their frequency range
"""

from gnuradio import usrp, usrp2
from usrpm import usrp_dbid
import subprocess

def detect_usrp1():
	for i in range(3):
		try:
			u = usrp.source_c(i)
			print "\033[1;31mUSRP found, serial:", u.serial_number(), "\033[1;m"
			a = usrp.selected_subdev(u, (0,0))
			if(a.dbid()!=-1):
				print "\033[1;33mSide A, RX:", a.name(), "(dbid: 0x%04X)" % (a.dbid()), "\033[1;m"
				print "freq range: (", a.freq_min()/1e6, "MHz, ", a.freq_max()/1e6, "MHz )"
				print "gain rainge: (", a.gain_min(), "dB, ", a.gain_max(), "dB )"
			b = usrp.selected_subdev(u, (1,0))
			if(b.dbid()!=-1):
				print "\033[1;33mSide B, RX:", b.name(), "(dbid: 0x%04X)" % (b.dbid()), "\033[1;m"
				print "freq range: (", b.freq_min()/1e6, "MHz, ", b.freq_max()/1e6, "MHz )"
				print "gain rainge: (", b.gain_min(), "dB, ", b.gain_max(), "dB )"
			u = usrp.sink_c(i)
			a = usrp.selected_subdev(u, (0,0))
			if(a.dbid()!=-1):
				print "\033[1;33mSide A, TX:", a.name(), "(dbid: 0x%04X)" % (a.dbid()), "\033[1;m"
				print "freq range: (", a.freq_min()/1e6, "MHz, ", a.freq_max()/1e6, "MHz )"
				print "gain rainge: (", a.gain_min(), "dB, ", a.gain_max(), "dB )"
			b = usrp.selected_subdev(u, (1,0))
			if(b.dbid()!=-1):
				print "\033[1;33mSide B, TX:", b.name(), "(dbid: 0x%04X)" % (b.dbid()), "\033[1;m"
				print "freq range: (", b.freq_min()/1e6, "MHz, ", b.freq_max()/1e6, "MHz )"
				print "gain rainge: (", b.gain_min(), "dB, ", b.gain_max(), "dB )"
		except:
			if(i==0): print "\033[1;31mno USRPs found"
			break

def detect_usrp2():
	interface = 'eth0'
	args = ['find_usrps', '-e', interface]
	p = subprocess.Popen(args=args,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			shell=False,
			universal_newlines=True)
	msg = p.stdout.read()
	usrp2_macs = sorted(map(lambda l: l.split()[0], filter(lambda l: l.count(':') >= 5, msg.strip().splitlines())))
	if(len(usrp2_macs)==0):
		print "\033[1;31mno USRP2's found\033[1;m"
		return -1
	for usrp2_mac in usrp2_macs:
		print "\033[1;31mUSRP2 found, mac address:", usrp2_mac, "\033[1;m"
		u2 = usrp2.source_32fc(interface, usrp2_mac)
		db = u2.daughterboard_id()
		if(db!=-1):
			db_name = [k for k, v in usrp_dbid.__dict__.iteritems() if v == db][0]
			print "\033[1;33mRX daughterboard:", db_name, "(dbid: 0x%04X)" % (db,), "\033[1;m"
			print "freq range: (", u2.freq_min()/1e6, "MHz, ", u2.freq_max()/1e6, "MHz )"
		u2 = usrp2.sink_32fc(interface, usrp2_mac)
		db = u2.daughterboard_id()
		if(db!=-1):
			db_name = [k for k, v in usrp_dbid.__dict__.iteritems() if v == db][0]
			print "\033[1;33mTX daughterboard:", db_name, "(dbid: 0x%04X)" % (db,), "\033[1;m"
			print "freq range: (", u2.freq_min()/1e6, "MHz, ", u2.freq_max()/1e6, "MHz )"

detect_usrp1()
detect_usrp2()

