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


import re
from encode import html_translate
from encode import out
import analyser

class analyser(analyser.analyser):
	def __init__(self,first_page,args):
		self.page = first_page
		self.args = args
	
	def analyse_page(self,page):
		self.page = page
	
	def	get_next_page(self):
		regexp = re.compile("<a href=\"\\S+\">下一页</a>",re.I|re.S)
		a = regexp.search(self.page)
		if a == None:
			return None
		regexp = re.compile("\"\\S+\"",re.I|re.S)
		ret = self.page[a.start() : a.end()]
		a = regexp.search(ret)
		ret = ret[a.start() + 1 : a.end() - 1]
		return "http://tieba.baidu.com" + ret;
		
	def	get_data(self,index):
		ret = ""
		next = self.page
		cc = re.compile("<cc>",re.I|re.S)
		cc_end = re.compile("</cc>",re.I|re.S)
		div = re.compile("<div.*?>",re.I|re.S)
		div_end = re.compile("</div>",re.I|re.S)
		a = re.compile("<a.*?>",re.I|re.S)
		a_end = re.compile("</a>",re.I|re.S)
		
		#Get data
		while True:
            #cc
			start = cc.search(next)
			if start == None:
				break
			next = next[start.end() + 1 :]
            #div
			start = div.search(next)
			if start != None:
				next = next[start.end() + 1 :]

			#/cc
			end = cc_end.search(next)
			if end == None:
				ret = ret + next
				break
			ret = ret + "<br>"
			ret = ret + next[0 : end.start() - 1]
			next = next[end.end() + 1:]

			#/div
			end = div_end.search(ret)
			if end != None:
				ret = ret[0 : end.start()]
				
			#a
			place = a.search(ret)
			if place != None:
				ret = ret.replace(ret[place.start() : place.end()],"")
			
			#/a
			place = a_end.search(ret)
			if place != None:
				ret = ret.replace(ret[place.start() : place.end()],"")
		out.printstr("Decoding...")
		ret = html_translate.translate(ret)
		return ret
