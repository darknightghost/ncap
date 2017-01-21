#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright 2017,暗夜幽灵 <darknightghost.cn@gmail.com>

#   his program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import html.parser
import re
import sys
import _thread

g_print_lock = _thread.allocate_lock()

def html_translate(s):
    '''Unescape html text.'''
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
        decoded = html.parser.unescape(encoded)
        
        if encoded == decoded:
            s = s.replace(encoded,"")
        else:
            s = s.replace(encoded,decoded)

    return s

def print_str(s):
    '''
        Print string.
    '''
    global g_print_lock
    g_print_lock.acquire()
    print(s)
    g_print_lock.release()
	
def print_err(e):
    '''
        Print exception.
    '''
    global g_print_lock
    g_print_lock.acquire()
    print(str(e))
    g_print_lock.release()
    
def save_file(name, data, overwrite):
    '''
        Save file.
    '''
    if overwrite:
        f = open(name, "wb")
        
    else:
        f = open(name, "ab")
        
    f.write(data)
    
    f.close()