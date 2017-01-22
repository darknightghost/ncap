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

import os
import time
import Common
import _thread
import importlib

def get_analyser(name, arg_dict):
    '''
        get_analyser(name, arg_dict) -> analyser
        
        Get analyser object by name.
    '''

    module = importlib.import_module("Analyser." + name)
    return module.Analyser(arg_dict)
        
def get_usages():
    '''
        get_usages() -> [[analyser name, usage]]
        
        Get usages of analysers.
    '''
    file_list = os.listdir(os.path.dirname(__file__))
    ret = []
    for f in file_list:
        name, ext = os.path.splitext(f)
        if ext ==  ".py" and f != "__init.py":
            try:
                module = importlib.import_module("Analyser." + name)
                ret.append([name, module.Analyser.get_usages()])
                
            except Exception:
                continue
    
    return ret

class AnalyserTask:
    '''
        AnalyserTask(url, analyse_callback) -> task
        
        Create a new task.
    '''
    cur_order = 0
    total_order = 0
    total_order_lck = _thread.allocate_lock()
    def __init__(self, url, analyse_callback, additional_info = None):
        #Set attributes
        self.__url = url
        self.__analyse_callback = analyse_callback
        self.__additional_info = additional_info
        
        #Get order
        AnalyserTask.total_order_lck.acquire()
        self.__order = AnalyserTask.total_order
        AnalyserTask.total_order += 1
        AnalyserTask.total_order_lck.release()
        
    def get_url(self):
        '''
            task.get_url() -> url
            
            Get url of the task.
        '''
        return self.__url
        
    def get_additional_info(self):
        '''
            task.get_additional_info -> object
            
            Get additional info.
        '''
        return self.__additional_info
    
    def analyse(self, page):
        '''
            task.analyse(page) -> [tasks]
            
            Analyse page, returns new tasks.
        '''
        return self.__analyse_callback(self, self.__url, page)
    
    def finish(self, filename, data, overwrite = True):
        '''
            task.finish(filename, data, overwrite = True)
            
            Finish a task and write data to file. If filename == None, The data
            will not be written. If overwrite == True, the file will be
            overwrite. If not, the data will be append to the file.
        '''
        if filename == None:
            AnalyserTask.cur_order += 1
            return
 
        else:
            while AnalyserTask.cur_order < self.__order:
                time.sleep(0.5)     
            
            Common.save_file(filename, data, overwrite)
            AnalyserTask.cur_order += 1

            return
            
class Analyser:
    def __init__(self, arg_dict):
        '''
            Analyser(arg_dict) -> analyser
            
            Create an analyser.
        '''
        raise NotImplementedError()
        
    def first_analyse_callback(self, task, url, page):
        '''
            analyser.first_analyse_callback(task, url, page) -> [new_tasks]
            
            First analyse callback. Analyse the page and return new tasks.
            If data is incorrect, return None and the page will be redownloaded.
        '''
        raise NotImplementedError()
        
    def after(self):
        '''
            analyser.after()
            
            This method will be called after finishing all tasks.
        '''
        return
        
    def get_usages():
        '''
            Analyser.get_usages() -> [[argname, desctiption]]
            
            Return the usage.
        '''
        raise NotImplementedError()