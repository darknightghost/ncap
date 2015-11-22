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
import thread

g_print_lock = None

def init_lock():
	global g_print_lock
	g_print_lock = thread.allocate_lock()

def printstr(s):
	global g_print_lock
	g_print_lock.acquire()
	type = sys.getfilesystemencoding()
	print s.decode('utf-8','ignore').encode(type)
	g_print_lock.release();
	
def printerr(e):
	global g_print_lock
	g_print_lock.acquire()
	print e
	g_print_lock.release();
