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

import urllib
import _thread
import Analyser
import Common
import urllib.request
import time
import http.cookiejar

class Spider:
    def __init__(self, arg_dict, analyser):
        self.__analyser = analyser
        self.__tasks = []
        self.__task_lck = _thread.allocate_lock()
        self.__thread_count = 0
        self.__thread_count_lck = _thread.allocate_lock()
        self.__begin_url = arg_dict["u"]
        self.__output = arg_dict["o"]
        self.__max_thread_num = int(arg_dict["h"])
        self.__agent = arg_dict["g"]
        self.__timeout = int(arg_dict["t"])
        
        try:
            self.__http_proxy = arg_dict["http-proxy"]
            
        except KeyError:
            self.__http_proxy = None
            
        return
        
    def run(self):
        self.__tasks.append(Analyser.AnalyserTask(self.__begin_url,
            self.__analyser.first_analyse_callback))
            
        #Set proxy
        cj = http.cookiejar.CookieJar()
        if self.__http_proxy != None:
            proxy_handler = urllib.request.ProxyHandler({'http': self.__http_proxy})
            opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPCookieProcessor(cj))
            urllib.request.install_opener(opener)
            
        else:
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            urllib.request.install_opener(opener)
            
        #Create working threads
        while self.__thread_count > 0 or len(self.__tasks) > 0:
            #Create thread
            if self.__thread_count < self.__max_thread_num \
                and self.__thread_count < len(self.__tasks):
                self.__thread_count_lck.acquire()
                self.__thread_count += 1
                self.__thread_count_lck.release()
                _thread.start_new_thread(self.__work_thread, ())
                
            time.sleep(1)
        
        self.__analyser.after()
        return
        
    def __work_thread(self):
        try:
            Common.print_str("Thread started...")
            self.__do_work()
            
        except Exception as e:
            Common.print_err(e)
        
        finally:
            self.__thread_count_lck.acquire()
            self.__thread_count -= 1
            self.__thread_count_lck.release()
            Common.print_str("Thread exited...")
        
        return
        
    def __do_work(self):
        while True:
            #Get task
            task = self.__get_task()
            if task == None:
                break
            
            #Download page
            data = b''
            while True:
                try:
                    Common.print_str("Getting url \"%s\"..."%(task.get_url()))
                    request = urllib.request.urlopen(task.get_url(),
                        timeout = self.__timeout);
                    data = request.readall()
                                            
                except KeyboardInterrupt:
                    Common.print_str("Keyboard interrupted.\n")
                    return
                    
                except Exception as e:
                    Common.print_str("Get url failed, retrying....\n")
                    
                if len(data) == 0:
                    Common.print_str("Get url failed, retrying....\n")
                    continue
                               
                #Analyse page
                Common.print_str("%d byte(s) got."%(len(data)))
                tasks = task.analyse(data)
                if tasks == None:
                    Common.print_str("Failed to analyse the page, retrying....\n")
                    continue
            
                break
                
            #Add task
            self._append_task(tasks)
            
        return
        
    def __get_task(self):
        ret = None
        self.__task_lck.acquire()
        if len(self.__tasks) > 0:
            ret = self.__tasks.pop(0)
            
        self.__task_lck.release()
        return ret
        
    def _append_task(self, tasks):
        self.__task_lck.acquire()
        self.__tasks += tasks
        self.__task_lck.release()
        return