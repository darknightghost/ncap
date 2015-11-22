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


import HTMLParser
import re
import sys

def translate(s):
	'''Unescape html text.'''
	html_parser = HTMLParser.HTMLParser()
	regexp = re.compile("&\W?\w+?;")
	s = s.replace(" ","")
	s = s.replace("\n","")
	s = s.replace("\r","")
	s = s.replace("\t","")
	s = s.replace("<br>","\n")
	s = s.replace("<br/>","\n")
	s = s.replace("<br />","\n")

	while True:
		match = regexp.search(s)
		if match == None:
			break
		encoded = s[match.start() : match.end()]
		decoded = html_parser.unescape(encoded)
		
		if encoded == decoded:
			s = s.replace(encoded,"")
		else:
			try:
				s = s.replace(encoded,decoded)
			except UnicodeDecodeError:
				s = s.replace(encoded,decoded.encode('utf-8'))

	return s
