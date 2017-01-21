#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#	Copyright 2017,暗夜幽灵 <darknightghost.cn@gmail.com>

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
import Spider
import Analyser

default_agent = "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"
default_thread_num = 5
default_timeout = 10

def main(argv):
    #Scan args
    global default_agent
    global default_thread_num
    global default_timeout
    
    #Get args	
    args = arg_scanner(argv)

    try:
        tmp = args["a"]
        tmp = args["u"]
        tmp = args["o"]
    except KeyError:
        usage()
        return -1
        
    try:
        tmp = args["g"]
    except KeyError:
        args["g"] = default_agent
        
    try:
        tmp = args["h"]
    except KeyError:
        args["h"] = default_thread_num
        
    try:
        tmp = args["t"]
    except KeyError:
        args["t"] = default_timeout
    
    #Get analyser
    analyser = Analyser.get_analyser(args["a"], args)
    
    #Call spider
    spider = Spider.Spider(args, analyser)
    spider.run()
    print("Finished")
    return 0


def usage():
    #Spider options
    print("Usage:")
    print("\tncap.py -u url -a analyser -o output [options] [analyser-options]\n"
        "Options :\n"
        "\t-t timeout           Connection timeout\n"
        "\t-h thread-num        Maxium thread num\n"
        "\t-g agent             User agent\n"
        "\t-http-proxy proxy    HTTP proxy")
        
    #Analyser options
    print("Analyser options :")
    options_list = Analyser.get_usages()
    for a in options_list:
        print("\t%s :"%(a[0]))
        for o in a[1]:
            print("\t\t%-21s%s"%(o[0], o[1]))
            
    print("")


def arg_scanner(arg_list):
    ret = {}
    new_arg = "";

    for s in arg_list:
        if s == "--help":
            usage()
            exit(0)
        elif s[0] == "-":
            new_arg = s[1:]
        else:
            ret[new_arg] = s
    return ret


ret = main(sys.argv)
exit(ret)

