# -*- coding: utf-8 -*-
#########################################################
# 고정영역
#########################################################
# python
import os
import sys
import traceback
import json
import re

# third-party
import requests
from flask import Blueprint, request, Response, render_template, redirect, jsonify, url_for, send_from_directory
from flask_login import login_required
from flask_socketio import SocketIO, emit, send

# sjva 공용
from framework.logger import get_logger
from framework import app, db, scheduler, socketio, path_app_root
from framework.util import Util, AlchemyEncoder
from system.logic import SystemLogic
            
# 패키지
package_name = __name__.split('.')[0]
logger = get_logger(package_name)

from .logic import Logic
from .model import ModelSetting


blueprint = Blueprint(package_name, package_name, url_prefix='/%s' %  package_name, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

def plugin_load():
    Logic.plugin_load()

def plugin_unload():
    Logic.plugin_unload()

plugin_info = {
    'version' : '0.1.0.4',
    'name' : 'xTeVe',
    'category_name' : 'launcher',
    'icon' : '',
    'developer' : 'soju6jan',
    'description' : 'xTeVe 런처<br><a href="https://xteve.de" target="_blank">xTeVe 홈페이지</a>',
    'home' : 'https://github.com/soju6jan/launcher_xteve',
    'more' : '',
}
#########################################################

# 메뉴 구성.
menu = {
    'main' : [package_name, 'xTeVe'],
    'sub' : [
        ['setting', '설정'], ['log', '로그']
    ], 
    'category' : 'launcher',
}  

#########################################################
# WEB Menu
#########################################################
@blueprint.route('/')
def home():
    return redirect('/%s/setting' % package_name)


@blueprint.route('/<sub>')
@login_required
def first_menu(sub): 
    if sub == 'setting':
        arg = ModelSetting.to_dict()
        arg['package_name']  = package_name
        arg['status'] = str(Logic.current_process is not None)
        return render_template('%s_%s.html' % (package_name, sub), arg=arg)
    elif sub == 'log':
        return render_template('log.html', package=package_name)
    return render_template('sample.html', title='%s - %s' % (package_name, sub))


@blueprint.route('/ajax/<sub>', methods=['GET', 'POST'])
@login_required
def ajax(sub):
    try:
        if sub == 'setting_save':
            ret = ModelSetting.setting_save(request)
            return jsonify(ret)
        elif sub == 'status':
            todo = request.form['todo']
            if todo == 'true':
                if Logic.current_process is None:
                    Logic.scheduler_start()
                    ret = 'execute'
                else:
                    ret = 'already_execute'
            else:
                if Logic.current_process is None:
                    ret = 'already_stop'
                else:
                    Logic.scheduler_stop()
                    ret =  'stop'
            return jsonify(ret)
    except Exception as e: 
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())

