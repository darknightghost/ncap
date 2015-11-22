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
		self.buff_lock = thread.allocate_lock()
		self.work_thread = thread.start_new_thread(self.analyse,())
		time.sleep(0)
		
	def analyse(self):
		'''
		  Thread function.It will be called in __init__().Don't call it manually.
		'''
		exec "from analyser.%s import *"%(self.analyser)
		
		self.buff_lock.acquire()
		
		#Get first page
		request = urllib2.Request(self.url)
		request.add_header('User-Agent', self.agent)
		try:
			out.printstr("\nGetting %s"%(self.url))
			response = urllib2.urlopen(request,timeout=30)
		except urllib2.URLError,e:
			out.printerr(e)
			self.end = True
			self.buff_lock.release()
			return
		
		#Initialize analyser
		data = response.read()
		out.printstr("%i bytes downloaded.\nAnalysing..."%(len(data)))
		try:
			analy = analyser(data,self.args)
		except Exception,e:
			out.printerr(e)
			self.end = True
			self.buff_lock.release()
			return
		
		#Analyse
		while True:
			gc.collect()
			while self.buff != None:
				self.buff_lock.release()
				time.sleep(0)
				self.buff_lock.acquire()
			try:
				self.buff = analy.get_data()
			except Exception,e:
				out.printerr(e)
				self.end = True
				self.buff_lock.release()
				return
			self.buff_lock.release()
			try:
				url = analy.get_next_page()
			except Exception,e:
				out.printerr(e)
				self.end = True
				return
							
			if url == None:
				break
			
			#Get pages
			while True:
				request = urllib2.Request(url)
				request.add_header('User-Agent', self.agent)
				try:
					try:
						out.printstr("\nGetting %s"%(url))
						response = urllib2.urlopen(request,timeout=30)
					except urllib2.URLError,e:
						out.printerr(e)
						out.printstr("Download failed retrying...\n")
						continue

					data = response.read()
				except Exception:
					out.printstr("Download failed retrying...\n")
					continue
				if len(data) == 0:
					out.printstr("Download failed retrying...\n")
					continue
				break
			out.printstr("%i bytes downloaded.\nAnalysing..."%(len(data)))
			try:
				analy.analyse_page(data)
			except Exception,e:
				out.printerr(e)
				self.end = True
				return
			
			self.buff_lock.acquire()
			
		self.end = True;
		return
		
	def get_data(self):
		'''
		  Get analysed data.If there's no more data to get, it returns
		None.
		'''
		while self.end == False:
			self.buff_lock.acquire()
			if self.buff == None:
				self.buff_lock.release()
				time.sleep(0)
				continue
			else:
				ret = self.buff
				self.buff = None
				self.buff_lock.release()
				return ret
		return None
