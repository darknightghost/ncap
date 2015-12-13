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


class analyser:
	def __init__(self,first_page,args):
		'''
		  Initialize the analyser.
		'''
		pass

	def allow_multi_thread(self):
		'''
		  Return if the analyser allow multithread-download.
		'''
		return False

	def analyse_page(self,page):
		'''
		  Transfer the page which the analyser should analyse.
		'''
		pass
	
	def	get_next_page(self):
		'''
		  Return the next page which the spider should download
		'''
		return None
		
	def	get_data(self,index):
		'''
		  Get data from the page.
		'''
		return ""
