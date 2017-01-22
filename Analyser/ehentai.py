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
        self.page = 0
        self.filename = arg_dict["o"]
        try:
            os.mkdir(self.filename)
            
        except FileExistsError as e:
            if not os.path.isdir(self.filename):
                raise e
            
        return
        
    def first_analyse_callback(self, task, url, page):
        '''
            analyser.first_analyse_callback(task, url, page) -> [new_tasks]
            
            First analyse callback. Analyse the page and return new tasks.
            Returns None if falied.
        '''
        
        task.finish(None, None, False)
        
        if url[-9 :] != "nw=always" and "p=" not in url:
            url += "?nw=always"
            return [AnalyserTask(url, self.first_analyse_callback)]

        page = page.decode(encoding='utf-8', errors='ignore')
                   
        pic_begin_exp = re.compile("<div\s*?class=\"gdtm\"")
        a_begin_exp = re.compile("<a href=\"")
        a_end_exp = re.compile("\"")
        next_page_exp = re.compile("<td\\s*?onclick=\"document.location=this.firstChild.href\">\\s*?<a href=\".*?\"\\s*?onclick=\"return false\">&gt;</a></td>")
        nextpage_a_exp = re.compile("<a href=\"\\S*?p=%d\" onclick=\"return false\">&gt;</a>"%(self.page + 1))
        
        #Get picture page addresses
        tasks = []
        i = 0
        while True:
            #Begin of div
            pos = pic_begin_exp.search(page)
            
            if pos == None:
                break
                
            page = page[pos.start() :]
            
            #url
            pos = a_begin_exp.search(page)
            if pos == None:
                break
                
            page = page[pos.end() :]
            pos = a_end_exp.search(page)
            if pos == None:
                break
            
            pic_page_url = page[: pos.end()]
                
            page = page[pos.end() :]
            tasks.append(AnalyserTask(pic_page_url, self.__picture_page_callback))
                    
        #Get next index page
        pos = next_page_exp.search(page)
        if pos == None:
            return tasks
            
        page = page[pos.start() : pos.end()]
        
        pos = nextpage_a_exp.search(page)
        if pos == None:
            return tasks
            
        page = page[pos.start() : pos.end()]
        
        pos = a_begin_exp.search(page)
        if pos == None:
            return tasks
            
        page = page[pos.end() :]
        pos = a_end_exp.search(page)
        if pos == None:
            return tasks
        
        next_url = page[: pos.end()]
        self.page += 1
        tasks.append(AnalyserTask(next_url, self.first_analyse_callback))
        return tasks

    def __picture_page_callback(self, task, url, page):
        task.finish(None, None, False)
        page = page.decode(encoding='utf-8', errors='ignore')
        img_exp = re.compile("<img id=\"img\" src=\"")
        img_end_exp = re.compile("\"")
        pos = img_exp.search(page)
        page = page[pos.end() :]
        pos = img_end_exp.search(page)
        pic_url = page[: pos.start()]
        return [AnalyserTask(pic_url, self.__picture_callback)]
        
    def __picture_callback(self, task, url, page):
        pic_name = url.split("/")[-1]
        pic_name = self.filename + os.sep + pic_name
        task.finish(pic_name, page, True)
        return []
        
    def get_usages():
        '''
            Analyser.get_usages() -> [[argname, desctiption]]
            
            Return the usage.
        '''
        return []
