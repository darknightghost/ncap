#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2015,暗夜幽灵 <darknightghost.cn@gmail.com>

#	his program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	at your option) any later version.

#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.

#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
from spider import *
from encode import out

analyser = ""
url = ""
output = ""

agent = "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"


def usage():
	out.printstr("Usage:")
	out.printstr("\tncap.py -u url -a analyser -o output [-t timeout] [-h thread-num] [-g agent] [analyser_parameters]")


def arg_scanner(arg_list):
	ret = {}
	new_arg = "";
	
	type = sys.getfilesystemencoding()
	
	for s in arg_list:
		if s == "--help":
			usage()
			exit(0)
		elif s[0] == "-":
			new_arg = s[1:]
		else:
			ret[new_arg] = s.decode(type).encode('utf-8')
	return ret

out.init_lock()
	
#Get args	
args = arg_scanner(sys.argv)

try:
	analyser = args["a"]
	url = args["u"]
	output = args["o"]
except KeyError:
	usage()
	exit(-1)
	
try:
	agent = args["g"]
except KeyError:
	pass

out.printstr("url = %s\nanalyser = %s\noutput = %s"%(url,analyser,output))

type = sys.getfilesystemencoding()
#Call spider
try:
	file = os.open(output.decode('utf-8').encode(type),os.O_CREAT|os.O_RDWR)
except Exception:
	out.printstr("Cannot open output file!")
	exit(-1)
	
s = spider(url,analyser,args,agent)

len = 0

while True:
	data = s.get_data()
	if data == None:
		break
	size = os.write(file,data)
	len = len + size
	out.printstr("%i bytes of data written."%(size))

out.printstr("\nTotal : %i bytes written."%(len))
os.close(file);



