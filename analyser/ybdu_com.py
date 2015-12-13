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
		self.base = args["u"]
		self.current_chapter = 0
		self.chapters = []

	def allow_multi_thread(self):
		return True

	def analyse_page(self,page):
		self.page = page
	
	def	get_next_page(self):
		self.current_chapter = self.current_chapter + 1
		if self.current_chapter > len(self.chapters):
			return None
		return self.base + self.chapters[self.current_chapter - 1];
		
	def	get_data(self,index):
		if self.current_chapter == 0:
			#Analyse index
			ret = self.analyse_index()
			return ret
		else:
			#Analyse chapter
			ret = self.analyse_chapter(index)
			return ret
		
	def analyse_index(self):
		ret = ""
		
		out.printstr("Analysing index...\n")
		
		#Get links
		url_exp = re.compile("<li><a href=\"\\S+?\">",re.I|re.S)
		page = self.page
		
		while True:
			m = url_exp.search(page)
			if m == None:
				break
			link = page[m.start() : m.end()]
			page = page[m.end() :]
			link = link[13 : -2]
			self.chapters.append(link)
		
		#Get title
		title_exp = re.compile("articlename='\\S+?'",re.I|re.S)
		page = self.page
		m = title_exp.search(page)
		if m != None:
			ret = page[m.start() + 13 : m.end() - 1]
			ret = ret.decode('gbk','ignore').encode('utf-8')
			out.printstr("Novel title : " + ret + "\n")
			ret = ret + "<br/>"
		
		return html_translate.translate(ret)
	def analyse_chapter(self,index):
		ret = ""
		page = self.page
		
		#Get title
		title_exp = re.compile("<h1>.+?</h1>",re.I|re.S)
		m = title_exp.search(page)
		if m == None:
			return None
		title = page[m.start() + 4 : m.end() - 5]
		ret = title.decode('gbk','ignore').encode('utf-8')
		out.printstr("Chapter title : " + ret + "\n")
		ret = "第%i章 "%(index) + ret
		ret = ret + "<br/>"
		ret = ret.replace(" ","&nbsp;")
		page = page[m.end() :]
		
		#Get chapter
		chapter_exp = re.compile("<div id=\"htmlContent\" class=\"contentbox\">",re.I|re.S)
		m = chapter_exp.search(page)
		page = page[m.end() :]
		chapter_exp = re.compile("<div class=\"ad00\"><script>show_style()",re.I|re.S)
		m = chapter_exp.search(page)
		page = page[0 : m.start()]
		ret = ret + page.decode('gbk','ignore').encode('utf-8')
		ret = ret + "<br/>"

		out.printstr("Decoding...")
		ret = ret.replace("&nbsp;&nbsp;&nbsp;&nbsp;","");
		ret = html_translate.translate(ret)
		
		return ret