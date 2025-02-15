# -*- coding: utf-8 -*-
#########################################################
# python
import os
import sys
import traceback
import logging
import threading
import subprocess
import platform
# third-party

# sjva 공용
from framework import path_app_root, db
from framework.logger import get_logger
from framework.util import Util

# 패키지
from .plugin import package_name, logger
from .model import ModelSetting


#########################################################
import requests
import urllib
import time
import threading
from datetime import datetime

class Logic(object):
    db_default = {
        'auto_start' : 'False',
        'url' : 'http://localhost:34400/web',
        'arm_bit' : '0'
    }
    current_process = None

    @staticmethod
    def db_init():
        try:
            for key, value in Logic.db_default.items():
                if db.session.query(ModelSetting).filter_by(key=key).count() == 0:
                    db.session.add(ModelSetting(key, value))
            db.session.commit()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def plugin_load():
        try:
            if platform.system() != 'Windows':
                custom = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')    
                os.system("chmod 777 -R %s" % custom)

            logger.debug('%s plugin_load', package_name)
            # DB 초기화 
            Logic.db_init()

            # 편의를 위해 json 파일 생성
            from plugin import plugin_info
            Util.save_from_dict_to_json(plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))

            # 자동시작 옵션이 있으면 보통 여기서 
            if ModelSetting.query.filter_by(key='auto_start').first().value == 'True':
                Logic.scheduler_start()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def plugin_unload():
        try:
            Logic.kill()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def scheduler_start():
        try:
            logger.debug('%s scheduler_start', package_name)
            
            os_ = platform.system()
            cpu = 'Intel'
            if os_ == 'Linux':
                if platform.platform().find('x86_64') == -1:
                    cpu = 'ARM64'
                    #if platform.architecture()[0]=='32bit':
                    #    cpu = 'ARM32'
                    if ModelSetting.get('arm_bit') == '1':
                        cpu = 'ARM32'
            path_ = os.path.join(os.path.dirname(__file__), 'bin', cpu, os_, 'xteve')
            if os_ == 'Windows':
                path_ += '.exe'
            logger.debug('PATH : %s', path_)
            Logic.current_process = subprocess.Popen(path_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def scheduler_stop():
        try:
            Logic.kill()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    # 기본 구조 End
    ##################################################################
    

    @staticmethod
    def kill():
        try:
            if Logic.current_process is not None and Logic.current_process.poll() is None:
                import psutil
                process = psutil.Process(Logic.current_process.pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
            Logic.current_process = None
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
