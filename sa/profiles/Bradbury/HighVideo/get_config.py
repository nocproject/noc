__author__ = 'FeNikS'
# -*- coding: utf-8 -*-

import urllib2
import json

import noc.sa.script
from noc.sa.interfaces import IGetConfig

datas = ['load-Servers', 'load-Channels', 'load-Profiles', 'load-Multiplexes']

def get_response_json(url, req_data):
    req = urllib2.Request(url, req_data)
    response = urllib2.urlopen(req)
    data = response.read()
    return json.loads(data)

def json2xml(obj, line_padding=''):
    result_list = list()
    obj_type = type(obj)

    if obj_type is list:
        for sub_elem in obj:
            result_list.append(json2xml(sub_elem, line_padding))
        return '\n\n'.join(result_list)

    if obj_type is dict:
        for tag_name in obj:
            sub_obj = obj[tag_name]

            if have_sub_elements(sub_obj):
                result_list.append('%s<%s>' % (line_padding, tag_name))
                result_list.append(json2xml(sub_obj, '\t' + line_padding))
                result_list.append('%s</%s>' % (line_padding, tag_name))
            else:
                result_list.append('%s<%s>%s</%s>' %\
                                   (line_padding, tag_name, sub_obj, tag_name))
        return '\n'.join(result_list)

def have_sub_elements(obj):
    obj_type = type(obj)
    if obj_type is list:
        return True
    if (obj_type is dict):
        if len(obj) > 1:
            return True
    return False

class Script(noc.sa.script.Script):
    name = "Bradbury.HighVideo.get_config"
    implements = [IGetConfig]
    TIMEOUT = 240
    CLI_TIMEOUT = 240

    def execute(self):
        result = ''

        url = 'http://' + self.access_profile.address + '/upload/'
        user = self.access_profile.user
        password = self.access_profile.password

        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, user, password)
        auth_manager = urllib2.HTTPBasicAuthHandler(password_manager)
        opener = urllib2.build_opener(auth_manager)
        urllib2.install_opener(opener)

        try:
            for data in datas:
                result += json2xml(get_response_json(url, data))
                result += "\n"
        except Exception as why:
            raise BaseException(why)

        result = '\n'.join(['<root>', result, '</root>'])
        return result