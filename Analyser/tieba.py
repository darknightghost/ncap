#! /usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2017, 暗夜幽灵 <darknightghost.cn@gmail.com>

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import Analyser
from Analyser import AnalyserTask
import Common
import re
import os
           
class Analyser(Analyser.Analyser):
    def __init__(self, arg_dict):
        '''
            Analyser(arg_dict) -> analyser
            
            Create an analyser.
        '''
        self.filename = arg_dict["o"]
        try:
            os.unlink(self.filename)
            
        except FileNotFoundError:
            pass
            
        self.__downloaded = 0
        self.__written = 0
            
        return
        
    def first_analyse_callback(self, task, url, page):
        '''
            analyser.first_analyse_callback(task, url, page) -> [new_tasks]
            
            First analyse callback. Analyse the page and return new tasks.
            Returns None if falied.
        '''
        self.__downloaded += len(page)
        if '#' in url:
            url = url.split("#")[0]
            task.finish(None, None, False)
            return [AnalyserTask(url, self.first_analyse_callback)]
            
        page = page.decode(encoding='utf-8', errors='ignore')
        data = (self.get_data(page) + "\n").encode(encoding='utf-8', errors='ignore')
        self.__written += len(data)
        task.finish(self.filename, data, False)
        
        next_url = self.get_next_page(page)
        if next_url == None:
            return []
            
        else:
            return [AnalyserTask(next_url, self.first_analyse_callback)]
        
    def get_usages():
        '''
            Analyser.get_usages() -> [[argname, desctiption]]
            
            Return the usage.
        '''
        return []
    
    def	get_data(self, page):
        ret = ""
        next = page
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
        Common.print_str("Decoding...")
        ret = Common.html_translate(ret)
        return ret
        
    def	get_next_page(self, page):
        regexp = re.compile("<a href=\"\\S+\">下一页</a>",re.I|re.S)
        a = regexp.search(page)
        if a == None:
            return None
        regexp = re.compile("\"\\S+\"",re.I|re.S)
        ret = page[a.start() : a.end()]
        a = regexp.search(ret)
        ret = ret[a.start() + 1 : a.end() - 1]
        return "http://tieba.baidu.com" + ret;
        
    def after(self):
        '''
            analyser.after()
            
            This method will be called after finishing all tasks.
        '''
        Common.print_str("%d byte(s) download.\n%d byte(s) written."%(self.__downloaded, self.__written))
        
        return