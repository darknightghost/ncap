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

import thread
from encode import out
import urllib2
import time
import analyser
import gc
import threading
from spider_downloader import *

class spider:
	"""
		  This class is used to get things from website.It downloads pages
		and calls the analyser to analyse them.And then, the caller can get
		the analysed data from it.
		  Example:
		------------------------------------------------------------------
			data = ""
			s = spider.spider(url,analyser,args,agent)
			while True:
				t = s.get_data()
				if t == None:
					break
				data = data + t
		------------------------------------------------------------------
	"""
	def __init__(self,url,analyser,args,agent):
		'''
		  Initialize the spider an create a new thread to download and analyse
		web pages.
		'''
		self.url = url
		self.analyser = analyser
		self.args = args
		self.buff = None
		self.end = False;
		self.agent = agent
		self.buff_lock = threading.Condition()
		self.work_thread = thread.start_new_thread(self.analyse,())
		time.sleep(0)
		
	def analyse(self):
		'''
		Private function
		  Thread function.It will be called in __init__().Don't call it manually.
		'''
		exec "from analyser.%s import *"%(self.analyser)

		#Get first page
		request = urllib2.Request(self.url)
		request.add_header('User-Agent', self.agent)
		try:
			out.printstr("\nGetting %s"%(self.url))
			response = urllib2.urlopen(request,timeout=5)
		except urllib2.URLError,e:
			out.printerr(e)
			self.end = True
			return
		
		#Initialize analyser
		data = response.read()
		out.printstr("%i bytes downloaded.\nAnalysing..."%(len(data)))
		try:
			analy = analyser(data,self.args)
		except Exception,e:
			out.printerr(e)
			self.end = True
			return
		try:
			data = analy.get_data(0)
		except Exception,e:
			out.printerr(e)
			self.end = True
			self.buff_lock.acquire()
			self.buff_lock.notifyAll()
			self.buff_lock.release()
			return
		self.write_buf(data)
		#Analyse
		if analy.allow_multi_thread():
			#The analyser support multi-thread download
			#Get args
			try:
				timeout = self.args["t"]
			except KeyError:
				timeout = 5
			try:
				thread_num = self.args["h"]
			except KeyError:
				thread_num = 5
			try:
				max_buffered = self.args["b"]
			except KeyError:
				max_buffered = 5

			#Initialize downloader
			downloader = spider_downloader(thread_num,self.agent,timeout,max_buffered)

			#Add urls
			while True:
				url = analy.get_next_page()
				if url == None:
					break
				else:
					downloader.add_url(url)

			#Analyse pages
			i = 0
			while True:
				gc.collect()
				page = downloader.get_data()
				if page == None:
					break
				i = i + 1
				analy.analyse_page(page)
				data = analy.get_data(i)
				if data == None:
					i = i - 1
					downloader.redownload()
					out.printstr("Analyzation failed redownload the page.\n")
				else:
					downloader.pop()
					self.write_buf(data)
		else:
			#The analyser does not support multi-thread download
			#Get args
			try:
				timeout = self.args["t"]
			except KeyError:
				timeout = 5

			#Initialize downloader
			downloader = spider_downloader(1,self.agent,timeout,1)

			#Analyse pages
			i = 0
			while True:
				gc.collect()
				url = analy.get_next_page()
				if url == None:
					break
				else:
					downloader.add_url(url)
				page = downloader.get_data()
				if page == None:
					break
				i = i + 1
				analy.analyse_page(page)
				data = analy.get_data(i)
				if data == None:
					i = i - 1
					downloader.redownload()
					out.printstr("Analyzation failed redownload the page.\n")
				else:
					downloader.pop()
					self.write_buf(data)

		self.end = True;
		return

	def write_buf(self,data):
		self.buff_lock.acquire()
		if self.buff != None:
			self.buff = self.buff + data
		else:
			self.buff = data
		self.buff_lock.notifyAll()
		self.buff_lock.release()

	def get_data(self):
		'''
		  Get analysed data.If there's no more data to get, it returns
		None.
		'''
		while self.end == False:
			self.buff_lock.acquire()
			if self.buff == None:
				self.buff_lock.wait()
				continue
			else:
				ret = self.buff
				self.buff = None
				self.buff_lock.release()
				return ret
		return None
