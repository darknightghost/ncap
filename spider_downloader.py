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
import gc
import threading

class spider_downloader:
	"""
		  This class is used to download web pages from the internet.
	"""
	def __init__(self,thread_num,agent,timeout,max_buffered):
		'''
		  Initialize the downloader.
		'''
		self.thread_num = thread_num
		self.agent = agent
		self.max_buffered = max_buffered
		if max_buffered <= thread_num:
			self.max_buffered = thread_num + 1
		self.timeout = timeout
		self.active_thread = 0
		self.last_url = 0
		self.url_num = 0
		#[[url,data,status]]
		self.url_list = []
		self.thread_num_lock = thread.allocate_lock()
		self.buffered_sem = threading.Semaphore(self.max_buffered)
		self.list_cond  = threading.Condition()
		self.free = 0
		self.downloading = 1

	def add_url(self,url):
		'''
		  Add a url to download.
		'''
		self.list_cond.acquire()
		self.url_list.append([url,None,self.free])
		self.list_cond.release()

	def get_data(self):
		'''
		  Get downloaded data from self.url_list.
		'''
		if len(self.url_list) == 0:
			return None
		else:
			self.list_cond .acquire()
			while self.url_list[0][1] == None:
				#Create download threads if self.active_thread < self.thread_num
				while self.active_thread  < self.thread_num:
					thread.start_new_thread(self.download,())
					self.thread_num_lock.acquire()
					self.active_thread = self.active_thread + 1
					self.thread_num_lock.release()
				self.list_cond.wait()
			self.list_cond.release()
			return self.url_list[0][1]

	def pop(self):
		'''
		  Remove the first url.
		'''
		self.list_cond.acquire()
		self.url_list.pop(0)
		self.last_url = self.last_url - 1
		self.list_cond.release()
		self.buffered_sem.release()
		gc.collect()

	def redownload(self):
		'''
		  Redownload first url.
		'''
		self.list_cond.acquire()
		self.url_list[0][1] = None
		self.url_list[0][2] = self.free
		self.last_url = 0
		self.list_cond.release()

	def download(self):
		'''
		Private function
		  Download thread.
		'''
		out.printstr("Download thread started.\n")
		while True:
			url = self.get_url()
			if url == None:
				break

			#Download url
			while True:
				request = urllib2.Request(url[0])
				request.add_header('User-Agent', self.agent)
				try:
					try:
						out.printstr("\nGetting %s"%(url[0]))
						response = urllib2.urlopen(request,timeout = self.timeout)
					except urllib2.URLError,e:
						out.printerr(e)
						out.printstr("Download failed retrying...\n")
						continue
					data = response.read()
					if len(data) == 0:
						out.printstr("Download failed retrying...\n")
						continue
				except Exception:
					out.printstr("Download failed retrying...\n")
					continue
				break
			out.printstr("%i bytes downloaded.\n"%(len(data)))

			#Add downloaded data
			
			url[1] = data
			url[2] = self.free

			self.list_cond.acquire()
			self.list_cond.notifyAll()
			self.list_cond.release()
		self.thread_num_lock.acquire()
		self.active_thread = self.active_thread - 1
		if self.thread_num > 1:
			self.thread_num = self.thread_num - 1
		self.thread_num_lock.release()
		out.printstr("Download thread exited.\n")
		return

	def get_url(self):
		'''
		Private function
		  Get next url to download.
		'''
		self.list_cond.acquire()
		i = self.last_url
		while i < len(self.url_list):
			if self.url_list[i][1] == None and self.url_list[i][2] == self.free:
				self.url_list[i][2] = self.downloading
				self.last_url = i + 1
				ret = self.url_list[i]
				self.list_cond.release()
				if i != 0:
					self.buffered_sem.acquire()
				return ret
			i = i + 1
		self.list_cond.release()
		return None