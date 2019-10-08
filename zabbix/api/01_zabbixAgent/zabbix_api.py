#!/usr/bin/python
# coding:utf-8
  
import json
import urllib2
from urllib2 import URLError
import sys, argparse
import xlrd

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
  
class zabbix_api:
    def __init__(self):
        self.url = 'http://127.0.0.1/zabbix/api_jsonrpc.php'  # 修改URL
        self.header = {"Content-Type":"application/json"}
        self.user_login()

    def user_login(self):
        data = json.dumps({
                           "jsonrpc": "2.0",
                           "method": "user.login",
                           "params": {
                                      "user": "Admin",  # web页面登录用户名
                                      "password": "zabbix"  # web页面登录密码
                                      },
                           "id": 0
                           })
        request = urllib2.Request(self.url, data, self.header)
        try:
            result = urllib2.urlopen(request, timeout = 2)
        except URLError as e:
            print u"\033[041m地址请求失败请检查!\033[0m \n\033[041m%s!\033[0m" % e
            sys.exit(1)
        else:
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                self.authID = response['result']
            elif response.get('error','') != '':
                print u"\033[041m用户认证失败请检查!\033[0m \n\033[041m%s\033[0m" % (response['error']['data'])
                sys.exit(1)
    #![01_创建模板]
    def template_get(self, templateName):
        data = json.dumps({
                            "jsonrpc":"2.0",
                            "method":"template.get",
                            "params":{
                                    "output": "extend",
                                    "filter": {
                                                "host": templateName
                                            }
                                    },
                            "auth":self.authID,
                            "id":1,
                        })
        request = urllib2.Request(self.url, data, self.header)     
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        if response.get('result','') != []:
            return response['result'][0]['templateid']
        else:
            return response['result']
                    
    def template_create(self, templateName):
        default_id = {}
        default_id['groupid'] = self.hostGroup_get('000_LocalTemplates')
        if default_id['groupid'] == []:
            self.hostGroup_create('000_LocalTemplates')
            default_id['groupid'] = self.hostGroup_get('000_LocalTemplates')
        name_list_1 = []
        for n_1 in templateName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in range(len(name_list_1)):
            name_2 = {}
            id_2 = {}
            name_2['name'] = name_list_1[n_2]['name']
            id_2['templateid'] = self.template_get(name_list_1[n_2]['name'])
            if id_2['templateid'] != []:
                print u"创建模板 : \033[041m%s\033[0m 失败!,模板重复创建" % name_list_1[n_2]['name']
                continue
            name_list_2.append(name_2)
        for n_3 in range(len(name_list_2)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "template.create",
                                "params": {
                                            "host": name_list_2[n_3]['name'],
                                            "groups": {
                                                        "groupid": default_id['groupid']
                                                    },
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"创建模板 : \033[042m%s\033[0m 成功!,模板ID为 : \033[042m%s\033[0m" % (name_list_2[n_3]['name'], ",".join(response['result']['templateids']))
            elif response.get('error','') != '':
                print u"创建模板 : \033[041m%s\033[0m 失败!\n\033[041m%s\033[0m" % (name_list_2[n_3]['name'], response['error']['data'])

    def template_delete(self, templateName):
        name_list_1 = []
        for n_1 in templateName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        id_list_2 = []
        for n_2 in range(len(name_list_1)):
            name_2 = {}
            id_2 = {}
            name_2['name'] = name_list_1[n_2]['name']
            id_2['templateids'] = self.template_get(name_list_1[n_2]['name'])
            if id_2['templateids'] == []:
                print u"删除模板 : \033[041m%s\033[0m 失败!,模板不存在!" % name_list_1[n_2]['name']
                continue
            name_list_2.append(name_2)
            id_list_2.append(id_2)
        for n_3 in range(len(name_list_2)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "template.delete",
                                "params": [
                                            id_list_2[n_3]['templateids']
                                        ],
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"删除模板 : \033[042m%s\033[0m 成功!,模板ID为 : \033[042m%s\033[0m" % (name_list_2[n_3]['name'], ",".join(response['result']['templateids']))
            elif response.get('error','') != '':
                print u"删除模板 : \033[041m%s\033[0m 失败!\n\033[041m%s\033[0m" % (name_list_2[n_3]['name'], response['error']['data'])
    #![02_为模板创建应用集]
    def application_get(self, templateName, applicationName):
        data = json.dumps({
                            "jsonrpc":"2.0",
                            "method":"application.get",
                            "params":{
                                    "output": "extend",
                                    "hostids": self.template_get(templateName),
                                    "filter":{
                                            "name": applicationName
                                        },
                                    },
                            "auth":self.authID,
                            "id":1,
                        })
        request = urllib2.Request(self.url, data, self.header)     
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        if response.get('result','') != []:
            return response['result'][0]['applicationid']
        else:
            return response['result']

    def application_create(self, templateName, applicationName):
        name_list_1 = []
        for n_1 in templateName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in applicationName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        if len(name_list_1) != len(name_list_2):
            print u"为模板删除应用集失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_3_1 = []
        name_list_3_2 = []
        id_list_3 = []
        for n_3 in range(len(name_list_1)):
            name_3_1 = {}
            name_3_2 = {}
            id_3 = {}
            name_3_1['name'] = name_list_1[n_3]['name']
            name_3_2['name'] = name_list_2[n_3]['name']
            id_3['templateid'] = self.template_get(name_list_1[n_3]['name'])
            if id_3['templateid'] == []:
                print u"为模板 : \033[041m%s\033[0m 创建应用集失败!,\033[041m模板不存在\033[0m" % name_list_1[n_3]['name']
                continue
            name_list_3_1.append(name_3_1)
            name_list_3_2.append(name_3_2)
            id_list_3.append(id_3)
        name_list_4_1 = []
        name_list_4_2 = []
        id_list_4_1 = []
        id_list_4_2 = []
        for n_4 in range(len(name_list_3_1)):
            name_4_1 = {}
            name_4_2 = {}
            id_4_1 = {}
            id_4_2 = {}
            name_4_1['name'] = name_list_3_1[n_4]['name']
            name_4_2['name'] = name_list_3_2[n_4]['name']
            id_4_1['templateid'] = id_list_3[n_4]['templateid']
            id_4_2['applicationid'] = self.application_get(name_list_3_1[n_4]['name'], name_list_3_2[n_4]['name'])
            if id_4_2['applicationid'] != []:
                print u"为模板 : \033[041m%s\033[0m 创建应用集 : \033[041m%s\033[0m 失败!,\033[041m应用集已存在!\033[0m" % \
                (name_list_3_1[n_4]['name'], name_list_3_2[n_4]['name'])
                continue
            name_list_4_1.append(name_4_1)
            name_list_4_2.append(name_4_2)
            id_list_4_1.append(id_4_1)
            id_list_4_2.append(id_4_2)
        for n_5 in range(len(name_list_4_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "application.create",
                                "params": {
                                            "name": name_list_4_2[n_5]['name'],
                                            "hostid": id_list_4_1[n_5]['templateid'],
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为模板 : \033[042m%s\033[0m 创建应用集 : \033[042m%s\033[0m 成功!,并且应用集ID为 : \033[042m%s\033[0m" % \
                (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], ",".join(response['result']['applicationids']))
            elif response.get('error','') != '':
                print u"为模板 : \033[041m%s\033[0m 创建应用集 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], response['error']['data'])

    def application_delete(self, templateName, applicationName):
        name_list_1 = []
        for n_1 in templateName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in applicationName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        if len(name_list_1) != len(name_list_2):
            print u"为模板删除应用集失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_3_1 = []
        name_list_3_2 = []
        id_list_3 = []
        for n_3 in range(len(name_list_1)):
            name_3_1 = {}
            name_3_2 = {}
            id_3 = {}
            name_3_1['name'] = name_list_1[n_3]['name']
            name_3_2['name'] = name_list_2[n_3]['name']
            id_3['templateid'] = self.template_get(name_list_1[n_3]['name'])
            if id_3['templateid'] == []:
                print u"为模板 : \033[041m%s\033[0m 删除应用集失败!,模板不存在" % name_list_1[n_3]['name']
                continue
            name_list_3_1.append(name_3_1)
            name_list_3_2.append(name_3_2)
            id_list_3.append(id_3)
        name_list_4_1 = []
        name_list_4_2 = []
        id_list_4 = []
        for n_4 in range(len(name_list_3_1)):
            name_4_1 = {}
            name_4_2 = {}
            id_4 = {}
            name_4_1['name'] = name_list_3_1[n_4]['name']
            name_4_2['name'] = name_list_3_2[n_4]['name']
            id_4['applicationid'] = self.application_get(name_list_3_1[n_4]['name'], name_list_3_2[n_4]['name'])
            if id_4['applicationid'] == []:
                print u"为模板删除应用集失败!,\033[041m应用集不存在\033[0m !"
                continue
            name_list_4_1.append(name_4_1)
            name_list_4_2.append(name_4_2)
            id_list_4.append(id_4)
        for n_5 in range(len(name_list_4_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "application.delete",
                                "params": [
                                            id_list_4[n_5]['applicationid']
                                        ],
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为模板 : \033[042m%s\033[0m 删除应用集 : \033[042m%s\033[0m 成功!,并且应用集ID为 : \033[042m%s\033[0m" % \
                (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], ",".join(response['result']['applicationids']))
            elif response.get('error','') != '':
                print u"为模板 : \033[041m%s\033[0m 删除应用集 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], response['error']['data'])
    #![03_为模板创建监控项]
    def item_get(self, templateName, itemName):
        data = json.dumps({
                            "jsonrpc":"2.0",
                            "method":"item.get",
                            "params":{
                                    "output": "extend",
                                    "hostids": self.template_get(templateName),
                                    "filter":{
                                            "name": itemName
                                        },
                                    },
                            "auth":self.authID,
                            "id":1,
                        })
        request = urllib2.Request(self.url, data, self.header)     
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        if response.get('result','') != []:
            return response['result'][0]['itemid']
        else:
            return response['result']
              
    def item_create(self, templateName, itemApplication, itemName, itemKey, itemValueType, itemDely):
        name_list_1 = []
        for n_1 in templateName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in itemApplication.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        name_list_3 = []
        for n_3 in itemName.split('//'):
            name_3 = {}
            name_3['name'] = n_3
            name_list_3.append(name_3)
        name_list_4 = []
        for n_4 in itemKey.split('//'):
            name_4 = {}
            name_4['name'] = n_4
            name_list_4.append(name_4)
        name_list_5 = []
        for n_5 in itemValueType.split('//'):
            name_5 = {}
            name_5['name'] = n_5
            name_list_5.append(name_5)
        name_list_6 = []
        for n_6 in itemDely.split('//'):
            name_6 = {}
            name_6['name'] = n_6
            name_list_6.append(name_6)  
        if len(name_list_1) != len(name_list_2) or \
        len(name_list_1) != len(name_list_3) or \
        len(name_list_1) != len(name_list_4) or \
        len(name_list_1) != len(name_list_5) or \
        len(name_list_1) != len(name_list_6):
            print u"为模板创建监控项失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_7_1 = []
        name_list_7_2 = []
        name_list_7_3 = []
        name_list_7_4 = []
        name_list_7_5 = []
        name_list_7_6 = []
        id_list_7 = []
        for n_7 in range(len(name_list_1)):
            name_7_1 = {}
            name_7_2 = {}
            name_7_3 = {}
            name_7_4 = {}
            name_7_5 = {}
            name_7_6 = {}
            id_7 = {}
            name_7_1['name'] = name_list_1[n_7]['name']
            name_7_2['name'] = name_list_2[n_7]['name']
            name_7_3['name'] = name_list_3[n_7]['name']
            name_7_4['name'] = name_list_4[n_7]['name']
            name_7_5['name'] = name_list_5[n_7]['name']
            name_7_6['name'] = name_list_6[n_7]['name']
            id_7['templateid'] = self.template_get(name_list_1[n_7]['name'])
            if id_7['templateid'] == []:
                print u"为模板 : \033[041m%s\033[0m 创建监控项失败!,模板不存在" % name_list_1[n_7]['name']
                continue
            name_list_7_1.append(name_7_1)
            name_list_7_2.append(name_7_2)
            name_list_7_3.append(name_7_3)
            name_list_7_4.append(name_7_4)
            name_list_7_5.append(name_7_5)
            name_list_7_6.append(name_7_6)
            id_list_7.append(id_7)
        name_list_8_1 = []
        name_list_8_2 = []
        name_list_8_3 = []
        name_list_8_4 = []
        name_list_8_5 = []
        name_list_8_6 = []
        id_list_8_1 = []
        id_list_8_2 = []
        for n_8 in range(len(name_list_1)):
            name_8_1 = {}
            name_8_2 = {}
            name_8_3 = {}
            name_8_4 = {}
            name_8_5 = {}
            name_8_6 = {}
            id_8_1 = {}
            id_8_2 = {}
            name_8_1['name'] = name_list_7_1[n_8]['name']
            name_8_2['name'] = name_list_7_2[n_8]['name']
            name_8_3['name'] = name_list_7_3[n_8]['name']
            name_8_4['name'] = name_list_7_4[n_8]['name']
            name_8_5['name'] = name_list_7_5[n_8]['name']
            name_8_6['name'] = name_list_7_6[n_8]['name']
            id_8_1['templateid'] = id_list_7[n_8]['templateid']
            id_8_2['applicationid'] = self.application_get(name_list_7_1[n_8]['name'], name_list_7_2[n_8]['name'])
            if id_8_2['applicationid'] == []:
                print u"为监控项 : \033[041m%s\033[0m 附加应用集 : \033[041m%s\033[0m 失败!,应用集不存在" % \
                (name_list_7_3[n_8]['name'], name_list_7_2[n_8]['name'])
                continue
            name_list_8_1.append(name_8_1)
            name_list_8_2.append(name_8_2)
            name_list_8_3.append(name_8_3)
            name_list_8_4.append(name_8_4)
            name_list_8_5.append(name_8_5)
            name_list_8_6.append(name_8_6)
            id_list_8_1.append(id_8_1)
            id_list_8_2.append(id_8_2)
        name_list_9_1 = []
        name_list_9_2 = []
        name_list_9_3 = []
        name_list_9_4 = []
        name_list_9_5 = []
        name_list_9_6 = []
        id_list_9_1 = []
        id_list_9_2 = []
        for n_9 in range(len(name_list_1)):
            name_9_1 = {}
            name_9_2 = {}
            name_9_3 = {}
            name_9_4 = {}
            name_9_5 = {}
            name_9_6 = {}
            id_9_1 = {}
            id_9_2 = {}
            id_9_3 = {}
            name_9_1['name'] = name_list_8_1[n_9]['name']
            name_9_2['name'] = name_list_8_2[n_9]['name']
            name_9_3['name'] = name_list_8_3[n_9]['name']
            name_9_4['name'] = name_list_8_4[n_9]['name']
            name_9_5['name'] = name_list_8_5[n_9]['name']
            name_9_6['name'] = name_list_8_6[n_9]['name']
            id_9_1['templateid'] = id_list_8_1[n_9]['templateid']
            id_9_2['applicationid'] = id_list_8_2[n_9]['applicationid']
            id_9_3['itemid'] = self.item_get(name_list_8_1[n_9]['name'], name_list_8_3[n_9]['name'])
            if id_9_3['itemid'] != []:
                print u"为模板 : \033[041m%s\033[0m 创建监控项失败!,监控项 : \033[041m%s\033[0m 已存在,并且监控项ID为 : \033[041m%s\033[0m" % \
                    (name_list_8_1[n_9]['name'], name_list_8_3[n_9]['name'], id_9_3['itemid'])
                continue
            name_list_9_1.append(name_9_1)
            name_list_9_2.append(name_9_2)
            name_list_9_3.append(name_9_3)
            name_list_9_4.append(name_9_4)
            name_list_9_5.append(name_9_5)
            name_list_9_6.append(name_9_6)
            id_list_9_1.append(id_9_1)
            id_list_9_2.append(id_9_2)
        for n_10 in range(len(name_list_9_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "item.create",
                                "params": {
                                            "hostid": id_list_9_1[n_10]['templateid'],
                                            "applications": [id_list_9_2[n_10]['applicationid']],
                                            "name": name_list_9_3[n_10]['name'],
                                            "type": 7,
                                            "key_": name_list_9_4[n_10]['name'],
                                            "value_type": name_list_9_5[n_10]['name'],
                                            "delay": name_list_9_6[n_10]['name']
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为模板 : \033[042m%s\033[0m 创建监控项 : \033[042m%s\033[0m 成功!,并且监控项ID为 : \033[042m%s\033[0m" % \
                (name_list_9_1[n_10]['name'], name_list_9_3[n_10]['name'], ",".join(response['result']['itemids']))
            elif response.get('error','') != '':
                print u"为模板 : \033[041m%s\033[0m 创建监控项 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_9_1[n_10]['name'], name_list_9_3[n_10]['name'], response['error']['data'])

    def item_delete(self, templateName, itemName):
        name_list_1 = []
        for n_1 in templateName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in itemName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        if len(name_list_1) != len(name_list_2):
            print u"为模板删除应用集失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_3_1 = []
        name_list_3_2 = []
        id_list_3 = []
        for n_3 in range(len(name_list_1)):
            name_3_1 = {}
            name_3_2 = {}
            id_3 = {}
            name_3_1['name'] = name_list_1[n_3]['name']
            name_3_2['name'] = name_list_2[n_3]['name']
            id_3['templateid'] = self.template_get(name_list_1[n_3]['name'])
            if id_3['templateid'] == []:
                print u"为模板 : \033[041m%s\033[0m 删除监控项失败!,模板不存在" % name_list_1[n_3]['name']
                continue
            name_list_3_1.append(name_3_1)
            name_list_3_2.append(name_3_2)
            id_list_3.append(id_3)
        name_list_4_1 = []
        name_list_4_2 = []
        id_list_4 = []
        for n_4 in range(len(name_list_3_1)):
            name_4_1 = {}
            name_4_2 = {}
            id_4 = {}
            name_4_1['name'] = name_list_3_1[n_4]['name']
            name_4_2['name'] = name_list_3_2[n_4]['name']
            id_4['itemid'] = self.item_get(name_list_3_1[n_4]['name'], name_list_3_2[n_4]['name'])
            if id_4['itemid'] == []:
                print u"为模板 : \033[041m%s\033[0m 删除监控项 : \033[041m%s\033[0m 失败!,\033[041m监控项不存在\033[0m !" %\
                (name_list_4_1[n_4]('name'), name_list_4_2[n_4]('name'))
                continue
            name_list_4_1.append(name_4_1)
            name_list_4_2.append(name_4_2)
            id_list_4.append(id_4)
        for n_5 in range(len(name_list_4_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "item.delete",
                                "params": [
                                            id_list_4[n_5]['itemid']
                                        ],
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为模板 : \033[042m%s\033[0m 删除监控项 : \033[042m%s\033[0m 成功!,并且应监控项ID为 : \033[042m%s\033[0m" % \
                (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], ",".join(response['result']['itemids']))
            elif response.get('error','') != '':
                print u"为模板 : \033[041m%s\033[0m 删除监控项 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], response['error']['data'])
    #![04_为模板创建触发器]
    def trigger_get(self, templateName, descriptionName):
        data = json.dumps({
                            "jsonrpc":"2.0",
                            "method":"trigger.get",
                            "params":{
                                    "output": "extend",
                                    "templateids": self.template_get(templateName),
                                    "filter":{
                                            "description": descriptionName
                                        },
                                    },
                            "auth":self.authID,
                            "id":1,
                        })
        request = urllib2.Request(self.url, data, self.header)     
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        if response.get('result','') != []:
            return response['result'][0]['triggerid']
        else:
            return response['result']

    def trigger_create(self, templateName, itemName, descriptionName, expressionName):
        name_list_1 = []
        for n_1 in templateName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in itemName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        name_list_3 = []
        for n_3 in descriptionName.split('//'):
            name_3 = {}
            name_3['name'] = n_3
            name_list_3.append(name_3)
        name_list_4 = []
        for n_4 in expressionName.split('//'):
            name_4 = {}
            name_4['name'] = n_4
            name_list_4.append(name_4)
        if len(name_list_1) != len(name_list_2) or \
        len(name_list_1) != len(name_list_3) or \
        len(name_list_1) != len(name_list_4):
            print u"为模板创建触发器失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_5_1 = []
        name_list_5_2 = []
        name_list_5_3 = []
        name_list_5_4 = []
        for n_5 in range(len(name_list_1)):
            name_5_1 = {}
            name_5_2 = {}
            name_5_3 = {}
            name_5_4 = {}
            id_5 = {}
            name_5_1['name'] = name_list_1[n_5]['name']
            name_5_2['name'] = name_list_2[n_5]['name']
            name_5_3['name'] = name_list_3[n_5]['name']
            name_5_4['name'] = name_list_4[n_5]['name']
            id_5['templateid'] = self.template_get(name_list_1[n_5]['name'])
            if id_5['templateid'] == []:
                print u"为模板 : \033[041m%s\033[0m 的监控项创建触发器失败!,模板不存在"  % name_list_1[n_5]['name']
                continue
            name_list_5_1.append(name_5_1)
            name_list_5_2.append(name_5_2)
            name_list_5_3.append(name_5_3)
            name_list_5_3.append(name_5_3)
            name_list_5_4.append(name_5_4)
        name_list_6_1 = []
        name_list_6_2 = []
        name_list_6_3 = []
        name_list_6_4 = []
        for n_6 in range(len(name_list_5_1)):
            name_6_1 = {}
            name_6_2 = {}
            name_6_3 = {}
            name_6_4 = {}
            id_6 = {}
            name_6_1['name'] = name_list_5_1[n_6]['name']
            name_6_2['name'] = name_list_5_2[n_6]['name']
            name_6_3['name'] = name_list_5_3[n_6]['name']
            name_6_4['name'] = name_list_5_4[n_6]['name']
            id_6['itemid'] = self.item_get(name_list_5_1[n_6]['name'], name_list_5_2[n_6]['name'])
            if id_6['itemid'] == []:
                print u"为模板 : \033[041m%s\033[0m 的监控项 : \033[041m%s\033[0m 创建触发器失败!,监控项不存在" % \
                (name_list_5_1[n_6]['name'], name_list_5_2[n_6]['name'])
                continue
            name_list_6_1.append(name_6_1)
            name_list_6_2.append(name_6_2)
            name_list_6_3.append(name_6_3)
            name_list_6_4.append(name_6_4)
        name_list_7_1 = []
        name_list_7_2 = []
        name_list_7_3 = []
        name_list_7_4 = []
        for n_7 in range(len(name_list_5_1)):
            name_7_1 = {}
            name_7_2 = {}
            name_7_3 = {}
            name_7_4 = {}
            id_7 = {}
            name_7_1['name'] = name_list_5_1[n_7]['name']
            name_7_2['name'] = name_list_5_2[n_7]['name']
            name_7_3['name'] = name_list_5_3[n_7]['name']
            name_7_4['name'] = name_list_5_4[n_7]['name']
            id_7['description'] = self.trigger_get(name_list_5_1[n_7]['name'], name_list_5_3[n_7]['name'])
            if id_7['description'] != []:
                print u"为模板 : \033[041m%s\033[0m 的监控项 : \033[041m%s\033[0m 创建触发器失败!,触发器 : \033[041m%s\033[0m 已存在,并且触发器ID为 : \033[041m%s\033[0m" % \
                (name_list_5_1[n_7]['name'], name_list_5_2[n_7]['name'], name_list_5_3[n_7]['name'], id_7['description'])
                continue
            name_list_7_1.append(name_7_1)
            name_list_7_2.append(name_7_2)
            name_list_7_3.append(name_7_3)
            name_list_7_4.append(name_7_4)
        for n_8 in range(len(name_list_7_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "trigger.create",
                                "params": {
                                            "description": name_list_7_3[n_8]['name'],
                                            "expression": name_list_7_4[n_8]['name'],
                                            "priority": 5,
                                            "manual_close": 1
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为模板 : \033[042m%s\033[0m 的监控项 : \033[042m%s\033[0m 创建触发器 : \033[042m%s\033[0m 成功!,并且触发器ID为 : \033[042m%s\033[0m" % \
                (name_list_7_1[n_8]['name'], name_list_7_2[n_8]['name'], name_list_7_3[n_8]['name'], ",".join(response['result']['triggerids']))
            elif response.get('error','') != '':
                print u"为模板 : \033[041m%s\033[0m 的监控项 : \033[041m%s\033[0m 创建触发器 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_7_1[n_8]['name'], name_list_7_2[n_8]['name'], name_list_7_3[n_8]['name'], response['error']['data'])
                
    def trigger_delete(self, templateName, descriptionName):
        name_list_1 = []
        for n_1 in templateName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in descriptionName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        if len(name_list_1) != len(name_list_2):
            print u"为模板删除应用集失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_3_1 = []
        name_list_3_2 = []
        id_list_3 = []
        for n_3 in range(len(name_list_1)):
            name_3_1 = {}
            name_3_2 = {}
            id_3 = {}
            name_3_1['name'] = name_list_1[n_3]['name']
            name_3_2['name'] = name_list_2[n_3]['name']
            id_3['triggerid'] = self.trigger_get(name_list_1[n_3]['name'], name_list_2[n_3]['name'])
            if id_3['triggerid'] == []:
                print u"为模板 : \033[041m%s\033[0m 删除触发器 : \033[041m%s\033[0m 失败!,\033[041m触发器不存在\033[0m !" % \
                (name_list_1[n_3]['name'], name_list_2[n_3]['name'])
                continue
            name_list_3_1.append(name_3_1)
            name_list_3_2.append(name_3_2)
            id_list_3.append(id_3)
        for n_4 in range(len(name_list_3_1)):
            data = json.dumps({
                                "jsonrpc":"2.0",
                                "method":"trigger.delete",
                                "params":[
                                            id_list_3[n_4]['triggerid']
                                        ],
                                "auth":self.authID,
                                "id":1,
                            })
            request = urllib2.Request(self.url, data, self.header)     
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为模板 : \033[042m%s\033[0m 删除触发器 : \033[042m%s\033[0m 成功!,并且触发器ID为 : \033[042m%s\033[0m" % \
                (name_list_3_1[n_4]['name'], name_list_3_2[n_4]['name'], ",".join(response['result']['triggerids']))
            elif response.get('error','') != '':
                print u"为模板 : \033[041m%s\033[0m 删除触发器 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_3_1[n_4]['name'], name_list_3_2[n_4]['name'], response['error']['data'])
    #![05_创建主机]
    def host_get(self, hostName):
        data = json.dumps({
                            "jsonrpc":"2.0",
                            "method":"host.get",
                            "params":{
                                    "output": "extend",
                                    "filter": {
                                                "host": hostName
                                            },
                                    },
                            "auth":self.authID,
                            "id":1,
                        })
        request = urllib2.Request(self.url, data, self.header)     
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        if response.get('result','') != []:
            return response['result'][0]['hostid']
        else:
            return response['result']

    def host_create(self, hostName):
        default_id = {}
        default_id['groupid'] = self.hostGroup_get('000_LocalHost')
        if default_id['groupid'] == []:
            self.hostGroup_create('000_LocalHost')
            default_id['groupid'] = self.hostGroup_get('000_LocalHost')
        name_list_1 = []
        for n_1 in hostName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in range(len(name_list_1)):
            name_2 = {}
            id_2 = {}
            name_2['name'] = name_list_1[n_2]['name']
            id_2['hostid'] = self.host_get(name_list_1[n_2]['name'])
            if id_2['hostid'] != []:
                print u"创建主机 : \033[041m%s\033[0m 失败!,主机重复创建" % name_list_1[n_2]['name']
                continue
            name_list_2.append(name_2)
        for n_3 in range(len(name_list_2)):
            data = json.dumps({
                               "jsonrpc":"2.0",
                               "method":"host.create",
                               "params":{
                                         "host": name_list_2[n_3]['name'],
                                         "interfaces": [
                                                            {
                                                                "type": 1,
                                                                "main": 1,
                                                                "useip": 1,
                                                                "ip": "127.0.0.1",
                                                                "dns": "",
                                                                "port": "10050"
                                                            }
                                                        ],
                                        "groups": [
                                                        {
                                                            "groupid": default_id['groupid']
                                                        }
                                                   ],
                                         },
                               "auth": self.authID,
                               "id":1                  
            })
            request = urllib2.Request(self.url, data, self.header)  
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"创建主机 : \033[042m%s\033[0m 成功!,主机ID为 : \033[042m%s\033[0m" % (name_list_2[n_3]['name'], ",".join(response['result']['hostids']))
            elif response.get('error','') != '':
                print u"创建主机 : \033[041m%s\033[0m 失败!\n\033[041m%s\033[0m" % (name_list_2[n_3]['name'], response['error']['data'])

    def host_delete(self, hostName):
        name_list_1 = []
        for n_1 in hostName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        id_list_2 = []
        for n_2 in range(len(name_list_1)):
            name_2 = {}
            id_2 = {}
            name_2['name'] = name_list_1[n_2]['name']
            id_2['hostid'] = self.host_get(name_list_1[n_2]['name'])
            if id_2['hostid'] == []:
                print u"删除主机组 : \033[041m%s\033[0m 失败!,主机组不存在" % name_list_1[n_2]['name']
                continue
            name_list_2.append(name_2)
            id_list_2.append(id_2)
        for n_3 in range(len(name_list_2)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "host.delete",
                                "params": [
                                            id_list_2[n_3]['hostid']
                                        ],
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"删除主机 : \033[042m%s\033[0m 成功!,主机组ID为 : \033[042m%s\033[0m" % (name_list_2[n_3]['name'], ",".join(response['result']['hostids']))
            elif response.get('error','') != '':
                print u"删除主机 : \033[041m%s\033[0m 失败!\n\033[041m%s\033[0m" % (name_list_2[n_3]['name'], response['error']['data'])
    #![06_为主机创建接口]
    def interface_get(self, hostName, ipName, portName):
        data = json.dumps({
                            "jsonrpc":"2.0",
                            "method":"hostinterface.get",
                            "params":{
                                    "output": "extend",
                                    "hostids": self.host_get(hostName),
                                    "filter":{
                                            "ip": ipName,
                                            "port": portName
                                        },
                                    },
                            "auth":self.authID,
                            "id":1,
                        })
        request = urllib2.Request(self.url, data, self.header)     
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        if response.get('result','') != []:
            return response['result'][0]['interfaceid']
        else:
            return response['result']

    def interface_massadd(self, hostName, ipName, portName, defaultName, typeName):
        name_list_1 = []
        for n_1 in hostName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in ipName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        name_list_3 = []
        for n_3 in portName.split('//'):
            name_3 = {}
            name_3['name'] = n_3
            name_list_3.append(name_3)
        name_list_4 = []
        for n_4 in defaultName.split('//'):
            name_4 = {}
            name_4['name'] = n_4
            name_list_4.append(name_4)
        name_list_5 = []
        for n_5 in typeName.split('//'):
            name_5 = {}
            name_5['name'] = n_5
            name_list_5.append(name_5)  
        if len(name_list_1) != len(name_list_2) or \
        len(name_list_1) != len(name_list_3) or \
        len(name_list_1) != len(name_list_4) or \
        len(name_list_1) != len(name_list_5):
            print u"为主机附加接口失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_6_1 = []
        name_list_6_2 = []
        name_list_6_3 = []
        name_list_6_4 = []
        name_list_6_5 = []
        id_list_6 = []
        for n_6 in range(len(name_list_1)):
            name_6_1 = {}
            name_6_2 = {}
            name_6_3 = {}
            name_6_4 = {}
            name_6_5 = {}
            id_6 = {}
            name_6_1['name'] = name_list_1[n_6]['name']
            name_6_2['name'] = name_list_2[n_6]['name']
            name_6_3['name'] = name_list_3[n_6]['name']
            name_6_4['name'] = name_list_4[n_6]['name']
            name_6_5['name'] = name_list_5[n_6]['name']
            id_6['hostid'] = self.host_get(name_list_1[n_6]['name'])
            if id_6['hostid'] == []:
                print u"为主机附加接口失败!,主机 : \033[041m%s\033[0m 不存在" % name_list_1[n_6]['name']
                continue
            name_list_6_1.append(name_6_1)
            name_list_6_2.append(name_6_2)
            name_list_6_3.append(name_6_3)
            name_list_6_4.append(name_6_4)
            name_list_6_5.append(name_6_5)
            id_list_6.append(id_6)
        name_list_7_1 = []
        name_list_7_2 = []
        name_list_7_3 = []
        name_list_7_4 = []
        name_list_7_5 = []
        id_list_7 = []
        for n_7 in range(len(name_list_1)):
            name_7_1 = {}
            name_7_2 = {}
            name_7_3 = {}
            name_7_4 = {}
            name_7_5 = {}
            id_7_1 = {}
            id_7_2 = {}
            name_7_1['name'] = name_list_1[n_7]['name']
            name_7_2['name'] = name_list_2[n_7]['name']
            name_7_3['name'] = name_list_3[n_7]['name']
            name_7_4['name'] = name_list_4[n_7]['name']
            name_7_5['name'] = name_list_5[n_7]['name']
            id_7_1['hostid'] = id_list_6[n_7]['hostid']
            id_7_2['interfaceid'] = self.interface_get(name_list_1[n_7]['name'], name_list_2[n_7]['name'], name_list_3[n_7]['name'])
            if id_7_2['interfaceid'] != []:
                print u"为主机 : \033[041m%s\033[0m 附加接口失败!,接口 : \033[041m%s\033[0m 已存在,并且接口ID为 : \033[042m%s\033[0m" % \
                    (name_list_1[n_7]['name'], name_list_3[n_7]['name'], id_7_2['interfaceid'])
                continue
            name_list_7_1.append(name_7_1)
            name_list_7_2.append(name_7_2)
            name_list_7_3.append(name_7_3)
            name_list_7_4.append(name_7_4)
            name_list_7_5.append(name_7_5)
            id_list_7.append(id_7_1)
        for n_8 in range(len(name_list_7_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "hostinterface.massadd",
                                "params": {
                                            "hosts": [
                                                        {
                                                            "hostid": id_list_7[n_8]['hostid']
                                                        }
                                                ],
                                            "interfaces": [
                                                            {
                                                                "dns": "",                                                                    
                                                                "ip": name_list_7_2[n_8]['name'],
                                                                "main": name_list_7_4[n_8]['name'],
                                                                "port": name_list_7_3[n_8]['name'],
                                                                "type": name_list_7_5[n_8]['name'],
                                                                "useip": 1,
                                                            }
                                                        ],
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为主机 : \033[042m%s\033[0m 附加接口 : \033[042m%s\033[0m 成功!,并且接口ID为 : \033[042m%s\033[0m" % \
                (name_list_7_1[n_8]['name'], name_list_7_3[n_8]['name'], ",".join(response['result']['interfaceids']['interfaceids']))
            elif response.get('error','') != '':
                print u"为主机 : \033[041m%s\033[0m 附加接口 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_7_1[n_8]['name'],name_list_7_3[n_8]['name'], response['error']['data'])

    def interface_massRemove(self, hostName, ipName, portName):
        name_list_1 = []
        for n_1 in hostName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in ipName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        name_list_3 = []
        for n_3 in portName.split('//'):
            name_3 = {}
            name_3['name'] = n_3
            name_list_3.append(name_3)
        if len(name_list_1) != len(name_list_2) or \
        len(name_list_1) != len(name_list_3):
            print u"为主机移除接口失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_4_1 = []
        name_list_4_2 = []
        name_list_4_3 = []
        id_list_4 = []
        for n_4 in range(len(name_list_1)):
            name_4_1 = {}
            name_4_2 = {}
            name_4_3 = {}
            id_4 = {}
            name_4_1['name'] = name_list_1[n_4]['name']
            name_4_2['name'] = name_list_2[n_4]['name']
            name_4_3['name'] = name_list_3[n_4]['name']
            id_4['hostid'] = self.host_get(name_list_1[n_4]['name'])
            if id_4['hostid'] == []:
                print u"为主机 : \033[041m%s\033[0m 移除接口失败!,主机不存在" % name_list_1[n_4]['name']
                continue
            name_list_4_1.append(name_4_1)
            name_list_4_2.append(name_4_2)
            name_list_4_3.append(name_4_3)
            id_list_4.append(id_4)
        name_list_5_1 = []
        name_list_5_2 = []
        name_list_5_3 = []
        id_list_5 = []
        for n_5 in range(len(name_list_1)):
            name_5_1 = {}
            name_5_2 = {}
            name_5_3 = {}
            id_5_1 = {}
            id_5_2 = {}
            name_5_1['name'] = name_list_1[n_5]['name']
            name_5_2['name'] = name_list_2[n_5]['name']
            name_5_3['name'] = name_list_3[n_5]['name']
            id_5_1['hostid'] = id_list_4[n_5]['hostid']
            id_5_2['interfaceid'] = self.interface_get(name_list_1[n_5]['name'], name_list_2[n_5]['name'], name_list_3[n_5]['name'])
            if id_5_2['interfaceid'] == []:
                print u"为主机 : \033[041m%s\033[0m 移除接口失败!,接口 : \033[041m%s\033[0m 不存在" % (name_list_1[n_5]['name'], name_list_3[n_5]['name'])
                continue
            name_list_5_1.append(name_5_1)
            name_list_5_2.append(name_5_2)
            name_list_5_3.append(name_5_3)
            id_list_5.append(id_5_1)       
        for n_6 in range(len(name_list_5_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "hostinterface.massremove",
                                "params": {
                                            "hosts": [
                                                        {
                                                            "hostids": id_list_5[n_6]['hostid']
                                                        }
                                                ],
                                            "interfaces": [
                                                            {
                                                                "dns": "",                                                                    
                                                                "ip": name_list_5_2[n_6]['name'],
                                                                "port": name_list_5_3[n_6]['name'],
                                                            }
                                                        ],
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为主机 : \033[042m%s\033[0m 移除接口 : \033[042m%s\033[0m 成功!,并且接口ID为 : \033[042m%s\033[0m" % \
                (name_list_5_1[n_6]['name'], name_list_5_3[n_6]['name'], ",".join([str(i) for i in response['result']['interfaceids']]))
            elif response.get('error','') != '':
                print u"为主机 : \033[041m%s\033[0m 移除接口 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_5_1[n_6]['name'], name_list_5_3[n_6]['name'], response['error']['data'])
    #![07_为主机关联模板]
    def host_massadd(self, hostName, templateName):
        name_list_1 = []
        for n_1 in hostName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in templateName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        if len(name_list_1) != len(name_list_2):
            print u"为主机附加模板失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_3_1 = []
        name_list_3_2 = []
        id_list_3 = []
        for n_3 in range(len(name_list_1)):
            name_3_1 = {}
            name_3_2 = {}
            id_3 = {}
            name_3_1['name'] = name_list_1[n_3]['name']
            name_3_2['name'] = name_list_2[n_3]['name']
            id_3['hostid'] = self.host_get(name_list_1[n_3]['name'])
            if id_3['hostid'] == []:
                print u"为主机 : \033[041m%s\033[0m 附加模板失败!,主机不存在" % name_list_1[n_3]['name']
                continue
            name_list_3_1.append(name_3_1)
            name_list_3_2.append(name_3_2)
            id_list_3.append(id_3)
        name_list_4_1 = []
        name_list_4_2 = []
        id_list_4_1 = []
        id_list_4_2 = []
        for n_4 in range(len(name_list_3_1)):
            name_4_1 = {}
            name_4_2 = {}
            id_4_1 = {}
            id_4_2 = {}
            name_4_1['name'] = name_list_3_1[n_4]['name']
            name_4_2['name'] = name_list_3_2[n_4]['name']
            id_4_1['hostid'] = id_list_3[n_4]['hostid']
            id_4_2['templateid'] = self.template_get(name_list_3_2[n_4]['name'])
            if id_4_2['templateid'] == []:
                print u"为主机附加模板 : \033[041m%s\033[0m 失败!,模板不存在!" % name_list_3_2[n_4]['name']
                continue
            name_list_4_1.append(name_4_1)
            name_list_4_2.append(name_4_2)
            id_list_4_1.append(id_4_1)
            id_list_4_2.append(id_4_2)
        for n_5 in range(len(name_list_4_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "host.massadd",
                                "params": {
                                            "hosts": [
                                                            {
                                                                "hostid": id_list_4_1[n_5]['hostid']
                                                            }
                                                        ],
                                            "templates": [
                                                        {
                                                            "templateid": id_list_4_2[n_5]['templateid']
                                                        }
                                                    ],
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为主机 : \033[042m%s\033[0m 附加模板 : \033[042m%s\033[0m 成功!,并且主机ID为 : \033[042m%s\033[0m" % \
                (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], ",".join(response['result']['hostids']))
            elif response.get('error','') != '':
                print u"为主机 : \033[041m%s\033[0m 附加模板 : \033[041m%s\033[0m 失败!,并且主机ID为 : \033[041m%s\033[0m \
                \n\033[041m%s\033[0m" % (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], id_list_4_2[n_5]['templateid'], response['error']['data'])
    
    def host_massremove(self, hostName, templateName):
        name_list_1 = []
        for n_1 in hostName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in templateName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        if len(name_list_1) != len(name_list_2):
            print u"为主机附加模板失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_3_1 = []
        name_list_3_2 = []
        id_list_3 = []
        for n_3 in range(len(name_list_1)):
            name_3_1 = {}
            name_3_2 = {}
            id_3 = {}
            name_3_1['name'] = name_list_1[n_3]['name']
            name_3_2['name'] = name_list_2[n_3]['name']
            id_3['hostid'] = self.host_get(name_list_1[n_3]['name'])
            if id_3['hostid'] == []:
                print u"为主机 : \033[041m%s\033[0m 附加模板失败!,主机不存在" % name_list_1[n_3]['name']
                continue
            name_list_3_1.append(name_3_1)
            name_list_3_2.append(name_3_2)
            id_list_3.append(id_3)
        name_list_4_1 = []
        name_list_4_2 = []
        id_list_4_1 = []
        id_list_4_2 = []
        for n_4 in range(len(name_list_3_1)):
            name_4_1 = {}
            name_4_2 = {}
            id_4_1 = {}
            id_4_2 = {}
            name_4_1['name'] = name_list_3_1[n_4]['name']
            name_4_2['name'] = name_list_3_2[n_4]['name']
            id_4_1['hostid'] = id_list_3[n_4]['hostid']
            id_4_2['templateid'] = self.template_get(name_list_3_2[n_4]['name'])
            if id_4_2['templateid'] == []:
                print u"为主机附加模板 : \033[041m%s\033[0m 失败!,模板不存在!" % name_list_3_2[n_4]['name']
                continue
            name_list_4_1.append(name_4_1)
            name_list_4_2.append(name_4_2)
            id_list_4_1.append(id_4_1)
            id_list_4_2.append(id_4_2)
        for n_5 in range(len(name_list_4_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "host.massremove",
                                "params": {
                                            "hostids": [
                                                            id_list_4_1[n_5]['hostid']
                                                    ],
                                            "templateids_clear": id_list_4_2[n_5]['templateid']
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为主机 : \033[042m%s\033[0m 移除模板 : \033[042m%s\033[0m 成功!,并且主机ID为 : \033[042m%s\033[0m" % \
                (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], ",".join(response['result']['hostids']))
            elif response.get('error','') != '':
                print u"为主机 : \033[041m%s\033[0m 移除模板 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], response['error']['data'])
    #![08_创建主机组]
    def hostGroup_get(self, hostGroupName):
        data = json.dumps({
                            "jsonrpc":"2.0",
                            "method":"hostgroup.get",
                            "params":{
                                    "output": "extend",
                                    "filter": {
                                                "name": hostGroupName
                                            }
                                    },
                            "auth":self.authID,
                            "id":1,
                        })
        request = urllib2.Request(self.url, data, self.header)   
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        if response.get('result','') != []:
            return response['result'][0]['groupid']
        else:
            return response['result']
             
    def hostGroup_create(self, hostGroupName):
        name_list_1 = []
        for n_1 in hostGroupName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in range(len(name_list_1)):
            name_2 = {}
            id_2 = {}
            name_2['name'] = name_list_1[n_2]['name']
            id_2['groupid'] = self.hostGroup_get(name_list_1[n_2]['name'])
            if id_2['groupid'] != []:
                print u"创建主机组 : \033[041m%s\033[0m 失败!,主机组重复创建" % name_list_1[n_2]['name']
                continue
            name_list_2.append(name_2)
        for n_3 in range(len(name_list_2)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "hostgroup.create",
                                "params": {
                                "name": name_list_2[n_3]['name']
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)  
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"创建主机组 : \033[042m%s\033[0m 成功!,主机组ID为 : \033[042m%s\033[0m" % (name_list_2[n_3]['name'], ",".join(response['result']['groupids']))
            elif response.get('error','') != '':
                print u"创建主机组 : \033[041m%s\033[0m 失败!\n\033[041m%s\033[0m" % (name_list_2[n_3]['name'], response['error']['data'])   
 
    def hostGroup_delete(self, hostGroupName):
        name_list_1 = []
        for n_1 in hostGroupName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        id_list_2 = []
        for n_2 in range(len(name_list_1)):
            name_2 = {}
            id_2 = {}
            name_2['name'] = name_list_1[n_2]['name']
            id_2['groupid'] = self.hostGroup_get(name_list_1[n_2]['name'])
            if id_2['groupid'] == []:
                print u"删除主机组 : \033[041m%s\033[0m 失败!,主机组不存在" % name_list_1[n_2]['name']
                continue
            name_list_2.append(name_2)
            id_list_2.append(id_2)
        for n_3 in range(len(name_list_2)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "hostgroup.delete",
                                "params": [
                                            id_list_2[n_3]['groupid']
                                        ],
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"删除主机组 : \033[042m%s\033[0m 成功!,主机组ID为 : \033[042m%s\033[0m" % (name_list_2[n_3]['name'], ",".join(response['result']['groupids']))
            elif response.get('error','') != '':
                print u"删除主机组 : \033[041m%s\033[0m 失败!\n\033[041m%s\033[0m" % (name_list_2[n_3]['name'], response['error']['data'])
    #![09_为主机附加主机组]
    def hostGroup_massadd(self, hostName, hostGroupName):
        name_list_1 = []
        for n_1 in hostName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in hostGroupName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        if len(name_list_1) != len(name_list_2):
            print u"为主机附加主机组失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_3_1 = []
        name_list_3_2 = []
        id_list_3 = []
        for n_3 in range(len(name_list_1)):
            name_3_1 = {}
            name_3_2 = {}
            id_3 = {}
            name_3_1['name'] = name_list_1[n_3]['name']
            name_3_2['name'] = name_list_2[n_3]['name']
            id_3['hostid'] = self.host_get(name_list_1[n_3]['name'])
            if id_3['hostid'] == []:
                print u"为主机 : \033[041m%s\033[0m 附加主机组失败!,主机不存在" % name_list_1[n_3]['name']
                continue
            name_list_3_1.append(name_3_1)
            name_list_3_2.append(name_3_2)
            id_list_3.append(id_3)
        name_list_4_1 = []
        name_list_4_2 = []
        id_list_4_1 = []
        id_list_4_2 = []
        for n_4 in range(len(name_list_3_1)):
            name_4_1 = {}
            name_4_2 = {}
            id_4_1 = {}
            id_4_2 = {}
            name_4_1['name'] = name_list_3_1[n_4]['name']
            name_4_2['name'] = name_list_3_2[n_4]['name']
            id_4_1['hostid'] = id_list_3[n_4]['hostid']
            id_4_2['groupid'] = self.hostGroup_get(name_list_3_2[n_4]['name'])
            if id_4_2['groupid'] == []:
                print u"为主机附加主机组 : \033[041m%s\033[0m 失败!,主机组不存在!" % name_list_3_2[n_4]['name']
                continue
            name_list_4_1.append(name_4_1)
            name_list_4_2.append(name_4_2)
            id_list_4_1.append(id_4_1)
            id_list_4_2.append(id_4_2)
        for n_5 in range(len(name_list_4_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "host.massadd",
                                "params": {
                                            "hosts": [
                                                            {
                                                                "hostid": id_list_4_1[n_5]['hostid']
                                                            }
                                                        ],
                                            "groups": [
                                                        {
                                                            "groupid": id_list_4_2[n_5]['groupid']
                                                        }
                                                    ],
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为主机 : \033[042m%s\033[0m 附加模板 : \033[042m%s\033[0m 成功!,并且主机ID为 : \033[042m%s\033[0m" % \
                (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], ",".join(response['result']['hostids']))
            elif response.get('error','') != '':
                print u"为主机 : \033[041m%s\033[0m 附加模板 : \033[041m%s\033[0m 失败!,并且主机ID为 : \033[041m%s\033[0m \
                \n\033[041m%s\033[0m" % (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], id_list_4_2[n_5]['groupid'], response['error']['data'])

    def hostGroup_massremove(self, hostName, hostGroupName):
        name_list_1 = []
        for n_1 in hostName.split('//'):
            name_1 = {}
            name_1['name'] = n_1
            name_list_1.append(name_1)
        name_list_2 = []
        for n_2 in hostGroupName.split('//'):
            name_2 = {}
            name_2['name'] = n_2
            name_list_2.append(name_2)
        if len(name_list_1) != len(name_list_2):
            print u"为主机移除主机组失败!,\033[041m输入的参数存在空值\033[0m"
            sys.exit(1)
        name_list_3_1 = []
        name_list_3_2 = []
        id_list_3 = []
        for n_3 in range(len(name_list_1)):
            name_3_1 = {}
            name_3_2 = {}
            id_3 = {}
            name_3_1['name'] = name_list_1[n_3]['name']
            name_3_2['name'] = name_list_2[n_3]['name']
            id_3['hostid'] = self.host_get(name_list_1[n_3]['name'])
            if id_3['hostid'] == []:
                print u"为主机 : \033[041m%s\033[0m 移除主机组失败!,主机不存在" % name_list_1[n_3]['name']
                continue
            name_list_3_1.append(name_3_1)
            name_list_3_2.append(name_3_2)
            id_list_3.append(id_3)
        name_list_4_1 = []
        name_list_4_2 = []
        id_list_4_1 = []
        id_list_4_2 = []
        for n_4 in range(len(name_list_3_1)):
            name_4_1 = {}
            name_4_2 = {}
            id_4_1 = {}
            id_4_2 = {}
            name_4_1['name'] = name_list_3_1[n_4]['name']
            name_4_2['name'] = name_list_3_2[n_4]['name']
            id_4_1['hostid'] = id_list_3[n_4]['hostid']
            id_4_2['groupid'] = self.hostGroup_get(name_list_3_2[n_4]['name'])
            if id_4_2['groupid'] == []:
                print u"为主机移除主机组 : \033[041m%s\033[0m 失败!,主机组不存在!" % name_list_3_2[n_4]['name']
                continue
            name_list_4_1.append(name_4_1)
            name_list_4_2.append(name_4_2)
            id_list_4_1.append(id_4_1)
            id_list_4_2.append(id_4_2)
        for n_5 in range(len(name_list_4_1)):
            data = json.dumps({
                                "jsonrpc": "2.0",
                                "method": "host.massremove",
                                "params": {
                                            "hostids": [
                                                            id_list_4_1[n_5]['hostid']
                                                    ],
                                            "groupids": id_list_4_2[n_5]['groupid']
                                        },
                                "auth": self.authID,
                                "id": 1
                            })
            request = urllib2.Request(self.url, data, self.header)
            result = urllib2.urlopen(request)
            response = json.loads(result.read())
            result.close()
            if response.get('result','') != '':
                print u"为主机 : \033[042m%s\033[0m 移除主机组 : \033[042m%s\033[0m 成功!,并且主机ID为 : \033[042m%s\033[0m" % \
                (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], ",".join(response['result']['hostids']))
            elif response.get('error','') != '':
                print u"为主机 : \033[041m%s\033[0m 移除主机组 : \033[041m%s\033[0m 失败!\
                \n\033[041m%s\033[0m" % (name_list_4_1[n_5]['name'],name_list_4_2[n_5]['name'], response['error']['data'])

if __name__ == "__main__":
    zabbix = zabbix_api()
    #![01_创建模板]
    parser = argparse.ArgumentParser(description='zabbix  api ', usage='%(prog)s [options]')
    parser.add_argument('-ct', nargs='+', metavar=('模板名称'), dest='ct', help=u"创建模板(多个可用//隔开)")
    parser.add_argument('-cte', nargs='?', metavar=('无参数'), dest='cte', default='cte', \
                        help=u"通过zabbix_api.xlsx的Sheet2表为A列的主机批量创建模板")
    parser.add_argument('-dt', metavar=('模板名称'), nargs='+', dest='dt', help=u"删除模板(多个可用//隔开)")
    parser.add_argument('-dte', nargs='?', metavar=('无参数'), dest='dte', default='dte', \
                        help=u"通过zabbix_api.xlsx的Sheet2表从A列批量删除模板")
    #![02_为模板创建应用集]
    parser.add_argument('-ca', nargs='+', metavar=('模板名称 应用集名称'), dest='ca', \
                        help=u"为模板(多个模板可用//隔开)创建应用集(多个应用集可用//隔开)")
    parser.add_argument('-cae', nargs='?', metavar=('无参数'), dest='cae',default='cae', \
                        help=u"通过zabbix_api.xlsx的Sheet5表为A列模板批量创建B列应用集")
    parser.add_argument('-da', nargs='+', metavar=('模板名称 应用集名称'), dest='da', \
                        help=u"为模板(多个模板可用//隔开)删除应用集(多个应用集可用//隔开)")
    parser.add_argument('-dae', nargs='?', metavar=('无参数'), dest='dae',default='dae', \
                        help=u"通过zabbix_api.xlsx的Sheet5表为A列模板批量删除B列应用集")
    #![03_为模板创建监控项]
    parser.add_argument('-ci', nargs='+', \
                        metavar=('模板名称 应用集名称 监控项名称 监控项键值 监控项信息类型 监控项更新间隔'), \
                        dest='ci', help=u"为模板(多个模板可用//隔开)创建监控项(多个监控项可用//隔开)")
    parser.add_argument('-cie', nargs='?', metavar=('无参数'), dest='cie',default='cie', \
                        help=u"通过zabbix_api.xlsx的Sheet5表为A列模板批量创建CDEF列监控项,并附加到B列应用集")
    parser.add_argument('-di', nargs='+', metavar=('模板名称 应用集名称'), dest='di', \
                        help=u"为模板(多个模板可用//隔开)删除监控项(多个监控项可用//隔开)")
    parser.add_argument('-die', nargs='?', metavar=('无参数'), dest='die',default='die', \
                        help=u"通过zabbix_api.xlsx的Sheet5表为A列模板批量删除C列监控项")
    #![04_为模板创建触发器]
    parser.add_argument('-ctg', nargs='+', \
                        metavar=('模板名称 监控项名称 触发器名称 触发器表达式'), \
                        dest='ctg', help=u"为监控项(多个监控项可用//隔开)创建触发器(多个触发器可用//隔开)")
    parser.add_argument('-ctge', nargs='?', metavar=('无参数'), dest='ctge',default='ctge', \
                        help=u"通过zabbix_api.xlsx的Sheet6表为A列模板的B列监控项批量创建CD列触发器")
    parser.add_argument('-dtg', nargs='+', metavar=('模板名称 触发器名称'), dest='dtg', \
                        help=u"为模板(多个模板可用//隔开)删除触发器(多个触发器可用//隔开)")
    parser.add_argument('-dtge', nargs='?', metavar=('无参数'), dest='dtge',default='dtge', \
                        help=u"通过zabbix_api.xlsx的Sheet6表为A列模板批量删除C列触发器")
    #![05_创建主机]
    parser.add_argument('-ch', nargs='+', metavar=('主机名称'), dest='ch', \
                        help=u"创建主机(多个可用//隔开)")
    parser.add_argument('-che', nargs='?', metavar=('无参数'), dest='che', default='che', \
                        help=u"通过zabbix_api.xlsx的Sheet4表从A列批量创建主机")
    parser.add_argument('-dh', nargs='+', metavar=('主机组名称'), dest='dh', help=u"删除主机组(多个可用//隔开)")
    parser.add_argument('-dhe', nargs='?', metavar=('无参数'), dest='dhe', default='dhe', \
                        help=u"通过zabbix_api.xlsx的Sheet1表从A列批量删除主机组")
    #![06_为主机创建接口]
    parser.add_argument('-mai', nargs='+', \
                        metavar=('主机名称 接口地址 接口端口 作为默认接口 接口类型'), \
                        dest='mai', help=u"为主机(多个主机可用//隔开)附加接口(多个接口可用//隔开)")
    parser.add_argument('-maie', nargs='?', metavar=('无参数'), dest='maie',default='maie', \
                        help=u"通过zabbix_api.xlsx的Sheet4表为A列主机批量附加BCDE列接口")
    parser.add_argument('-mri', nargs='+', metavar=('主机名称 接口地址 接口端口'), dest='mri', \
                        help=u"为主机(多个主机可用//隔开)移除接口(多个接口可用//隔开)")
    parser.add_argument('-mrie', nargs='?', metavar=('无参数'), dest='mrie', default='mrie', \
                        help=u"通过zabbix_api.xlsx的Sheet4表为A列主机批量移除BC列接口")
    #![07_为主机关联模板]
    parser.add_argument('-mat', nargs='+', metavar=('主机组名称 模板名称'), dest='mat', \
                        help=u"为主机(多个主机可用//隔开)附加模板(多个模板可用//隔开)")
    parser.add_argument('-mate', nargs='?', metavar=('无参数'), dest='mate',default='mate', \
                        help=u"通过zabbix_api.xlsx的Sheet3表为A列主机组批量附加B列模板")
    parser.add_argument('-mrt', nargs='+', metavar=('主机组名称 模板名称'), dest='mrt', \
                        help=u"为主机(多个主机可用//隔开)移除模板(多个模板可用//隔开)")
    parser.add_argument('-mrte', nargs='?', metavar=('无参数'), dest='mrte', default='mrte',\
                        help=u"通过zabbix_api.xlsx的Sheet3表为A列主机组批量移除B列模板")
    #![08_创建主机组]
    parser.add_argument('-cg', nargs='+', metavar=('主机组名称'), dest='cg', help=u"创建主机组(多个可用//隔开)")
    parser.add_argument('-cge', nargs='?', metavar=('无参数'), dest='cge', default='cge', \
                        help=u"通过zabbix_api.xlsx的Sheet1表从A列批量创建主机组")
    parser.add_argument('-dg', nargs='+', metavar=('主机组名称'), dest='dg', help=u"删除主机组(多个可用//隔开)")
    parser.add_argument('-dge', nargs='?', metavar=('无参数'), dest='dge', default='dge', \
                        help=u"通过zabbix_api.xlsx的Sheet1表从A列批量删除主机组")
    #![09_为主机附加主机组]
    parser.add_argument('-mag', nargs='+', metavar=('主机名称 模板名称'), dest='mag', \
                        help=u"为主机(多个主机可用//隔开)附加主机组(多个主机组可用//隔开)")
    parser.add_argument('-mage', nargs='?', metavar=('无参数'), dest='mage',default='mage', \
                        help=u"通过zabbix_api.xlsx的Sheet3表为A列主机批量附加B列主机组")
    parser.add_argument('-mrg', nargs='+', metavar=('主机组名称 模板名称'), dest='mrg', \
                        help=u"为主机(多个主机可用//隔开)移除主机组(多个主机组可用//隔开)")
    parser.add_argument('-mrge', nargs='?', metavar=('无参数'), dest='mrge', default='mrge',\
                        help=u"通过zabbix_api.xlsx的Sheet3表为A列主机组批量移除B列主机组")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 如有问题请联系作者QQ1284524409', help=u"如有问题请联系作者QQ1284524409")
    if len(sys.argv) == 1:
        print parser.print_help()
    else:
        args = parser.parse_args()
        #![01_创建模板]
        if args.ct:
            zabbix.template_create(args.ct[0])
        elif args.cte != 'cte':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for row in xrange(workbook.sheets()[0].nrows):
                if row == 0:
                    continue
                else:
                    templateName = workbook.sheets()[0].cell(row, 0).value
                    if templateName == '':
                        break
                    try:
                        zabbix.template_create(templateName)
                    except Exception as e:
                        print u"Sheet2表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (row + 1, e)
                        sys.exit(1)
        elif args.dt:
            zabbix.template_delete(args.dt[0])
        elif args.dte != 'dte':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for row in xrange(workbook.sheets()[0].nrows):
                if row == 0:
                    continue
                else:
                    templateName = workbook.sheets()[0].cell(row, 0).value
                    if templateName == '':
                        break
                    try:
                        zabbix.template_delete(templateName)
                    except Exception as e:
                        print u"Sheet2表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (row + 1, e)
                        sys.exit(1)
        #![02_为模板创建应用集]
        elif args.ca:
            zabbix.application_create(args.ca[0], args.ca[1])
        elif args.cae != 'cae':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for x in xrange(workbook.sheets()[1].nrows):
                if x == 0:
                    continue
                else:
                    templateName = workbook.sheets()[1].cell(x, 0).value
                    if templateName == '':
                        break
                    applicationName = workbook.sheets()[1].cell(x, 1).value
                    if applicationName == '':
                        break
                    try:
                        zabbix.application_create(templateName, applicationName)
                    except Exception as e:
                        print u"Sheet5表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (x + 1, e)
                        sys.exit(1)
        elif args.da:
            zabbix.application_delete(args.da[0], args.da[1])
        elif args.dae != 'dae':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for x in xrange(workbook.sheets()[1].nrows):
                if x == 0:
                    continue
                else:
                    templateName = workbook.sheets()[1].cell(x, 0).value
                    if templateName == '':
                        break
                    applicationName = workbook.sheets()[1].cell(x, 1).value
                    if applicationName == '':
                        break
                    try:
                        zabbix.application_delete(templateName, applicationName)
                    except Exception as e:
                        print u"Sheet5表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (x + 1, e)
                        sys.exit(1)
        #![03_为模板创建监控项]
        elif args.ci:
            zabbix.item_create(args.ci[0], args.ci[1], args.ci[2], args.ci[3], args.ci[4], args.ci[5])
        elif args.cie != 'cie':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for x in xrange(workbook.sheets()[6].nrows):
                if x == 0:
                    continue
                else:
                    templateName = workbook.sheets()[2].cell(x, 0).value
                    if templateName == '':
                        break
                    itemApplication = workbook.sheets()[2].cell(x, 1).value
                    if itemApplication == '':
                        break
                    itemName = workbook.sheets()[2].cell(x, 2).value
                    if itemName == '':
                        break
                    itemKey = workbook.sheets()[2].cell(x, 3).value
                    if itemKey == '':
                        break
                    itemValueType = workbook.sheets()[2].cell(x, 4).value
                    if itemValueType == '':
                        break
                    itemDely = workbook.sheets()[2].cell(x, 5).value
                    if itemDely == '':
                        break
                    try:
                        zabbix.item_create(templateName, itemApplication, itemName, itemKey, str(int(itemValueType)), itemDely)
                    except Exception as e:
                        print u"Sheet5表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (x + 1, e)
                        sys.exit(1)
        elif args.di:
            zabbix.item_delete(args.di[0], args.di[1])
        elif args.die != 'die':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for x in xrange(workbook.sheets()[2].nrows):
                if x == 0:
                    continue
                else:
                    templateName = workbook.sheets()[2].cell(x, 0).value
                    if templateName == '':
                        break
                    itemName = workbook.sheets()[2].cell(x, 1).value
                    if itemName == '':
                        break
                    try:
                        zabbix.item_delete(templateName, itemName)
                    except Exception as e:
                        print u"Sheet5表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (x + 1, e)
                        sys.exit(1)
        #![04_为模板创建触发器]
        elif args.ctg:
            zabbix.trigger_create(args.ctg[0], args.ctg[1], args.ctg[2], args.ctg[3])
        elif args.ctge != 'ctge':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for x in xrange(workbook.sheets()[3].nrows):
                if x == 0:
                    continue
                else:
                    templateName = workbook.sheets()[3].cell(x, 0).value
                    if templateName == '':
                        break
                    itemName = workbook.sheets()[3].cell(x, 1).value
                    if itemName == '':
                        break
                    descriptionName = workbook.sheets()[3].cell(x, 2).value
                    if descriptionName == '':
                        break
                    expressionName = workbook.sheets()[3].cell(x, 3).value
                    if expressionName == '':
                        break
                    try:
                        zabbix.trigger_create(templateName, itemName, descriptionName, expressionName)
                    except Exception as e:
                        print u"Sheet5表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (x + 1, e)
                        sys.exit(1)
        elif args.dtg:
            zabbix.trigger_delete(args.dtg[0], args.dtg[1])
        elif args.dtge != 'dtge':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for x in xrange(workbook.sheets()[3].nrows):
                if x == 0:
                    continue
                else:
                    templateName = workbook.sheets()[3].cell(x, 0).value
                    if templateName == '':
                        break
                    triggerName = workbook.sheets()[3].cell(x, 2).value
                    if triggerName == '':
                        break
                    try:
                        zabbix.trigger_delete(templateName, triggerName)
                    except Exception as e:
                        print u"Sheet5表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (x + 1, e)
                        sys.exit(1)
        #![05_创建主机]
        elif args.ch:
            zabbix.host_create(args.ch[0])
        elif args.che != 'che':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for row in xrange(workbook.sheets()[4].nrows):
                if row == 0:
                    continue
                else:                    
                    hostName = workbook.sheets()[4].cell(row, 0).value
                    if hostName == '':
                        break
                    try:
                        zabbix.host_create(hostName)
                    except Exception as e:
                        print u"Sheet4表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (row + 1, e)
                        sys.exit(1)
        elif args.dh:
            zabbix.host_delete(args.dh[0])
        elif args.dhe != 'dhe':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for row in xrange(workbook.sheets()[4].nrows):
                if row == 0:
                    continue
                else:
                    hosthost = workbook.sheets()[4].cell(row, 0).value
                    if hosthost == '':
                        break
                    try:
                        zabbix.host_delete(hosthost)
                    except Exception as e:
                        print u"Sheet4表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (row + 1, e)
                        sys.exit(1)
        #![06_为主机创建接口]
        elif args.mai:
            zabbix.interface_massadd(args.mai[0], args.mai[1], args.mai[2], args.mai[3], args.mai[4])
        elif args.maie != 'maie':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for col1 in xrange(workbook.sheets()[5].nrows):
                if col1 == 0:
                    continue
                else:
                    hostName = workbook.sheets()[5].cell(col1, 0).value
                    if hostName == '':
                        break
                    ipName = workbook.sheets()[5].cell(col1, 1).value
                    if ipName == '':
                        break
                    portName = workbook.sheets()[5].cell(col1, 2).value
                    if portName == '':
                        break
                    defaultName = workbook.sheets()[5].cell(col1, 3).value
                    if defaultName == '':
                        break
                    typeName = workbook.sheets()[5].cell(col1, 4).value
                    if typeName == '':
                        break
                    try:
                        zabbix.interface_massadd(hostName, ipName, str(int(portName)), str(int(defaultName)), str(int(typeName)))
                    except Exception as e:
                        print u"Sheet4表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (col1 + 1, e)
                        sys.exit(1)
        elif args.mri:
            zabbix.interface_massRemove(args.mri[0], args.mri[1], args.mri[2])
        elif args.mrie != 'mrie':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for col1 in xrange(workbook.sheets()[5].nrows):
                if col1 == 0:
                    continue
                else:
                    hostName = workbook.sheets()[5].cell(col1, 0).value
                    if hostName == '':
                        break
                    ipName = workbook.sheets()[5].cell(col1, 1).value
                    if ipName == '':
                        break
                    portName = workbook.sheets()[5].cell(col1, 2).value
                    if portName == '':
                        break
                    try:
                        zabbix.interface_massRemove(hostName, ipName, str(int(portName)))
                    except Exception as e:
                        print u"Sheet4表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (col1 + 1, e)
                        sys.exit(1)
        #![07_为主机关联模板]
        elif args.mat:
            zabbix.host_massadd(args.mat[0], args.mat[1])
        elif args.mate != 'mate':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for n_1 in xrange(workbook.sheets()[6].nrows):
                if n_1 == 0:
                    continue
                else:
                    hostgroup = workbook.sheets()[6].cell(n_1, 0).value
                    if hostgroup == '':
                        break
                    templateName = workbook.sheets()[6].cell(n_1, 1).value
                    if templateName == '':
                        break
                    try:
                        zabbix.host_massadd(hostgroup, templateName)
                    except Exception as e:
                        print u"Sheet3表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (n_1 + 1, e)
                        sys.exit(1)
        elif args.mrt:
            zabbix.host_massremove(args.mrt[0], args.mrt[1])
        elif args.mrte != 'mrte':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for n_1 in xrange(workbook.sheets()[6].nrows):
                if n_1 == 0:
                    continue
                else:
                    hostgroup = workbook.sheets()[6].cell(n_1, 0).value
                    if hostgroup == '':
                        break
                    templateName = workbook.sheets()[6].cell(n_1, 1).value
                    if templateName == '':
                        break
                    try:
                        zabbix.host_massremove(hostgroup, templateName)
                    except Exception as e:
                        print u"Sheet3表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (n_1 + 1, e)
                        sys.exit(1)
        #![08_创建主机组]
        elif args.cg:
            zabbix.hostGroup_create(args.cg[0])
        elif args.cge != 'cge':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for row in xrange(workbook.sheets()[7].nrows):
                if row == 0:
                    continue
                else:                    
                    hostgroup = workbook.sheets()[7].cell(row, 0).value
                    if hostgroup == '':
                        break
                    try:
                        zabbix.hostGroup_create(hostgroup)
                    except Exception as e:
                        print u"Sheet1表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (row + 1, e)
                        sys.exit(1)
        elif args.dg:
            zabbix.hostGroup_delete(args.dg[0])
        elif args.dge != 'dge':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for row in xrange(workbook.sheets()[7].nrows):
                if row == 0:
                    continue
                else:
                    hostgroup = workbook.sheets()[7].cell(row, 0).value
                    if hostgroup == '':
                        break
                    try:
                        zabbix.hostGroup_delete(hostgroup)
                    except Exception as e:
                        print u"Sheet1表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (row + 1, e)
                        sys.exit(1)
        #![09_为主机附加主机组]
        elif args.mag:
            zabbix.hostGroup_massadd(args.mag[0], args.mag[1])
        elif args.mage != 'mage':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for n_1 in xrange(workbook.sheets()[8].nrows):
                if n_1 == 0:
                    continue
                else:
                    hostName = workbook.sheets()[8].cell(n_1, 0).value
                    if hostName == '':
                        break
                    hostGroupName = workbook.sheets()[8].cell(n_1, 1).value
                    if hostGroupName == '':
                        break
                    try:
                        zabbix.hostGroup_massadd(hostName, hostGroupName)
                    except Exception as e:
                        print u"Sheet3表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (n_1 + 1, e)
                        sys.exit(1)
        elif args.mrg:
            zabbix.hostGroup_massremove(args.mrt[0], args.mrt[1])
        elif args.mrge != 'mrge':
            workbook = xlrd.open_workbook('zabbix_api.xlsx')
            for n_1 in xrange(workbook.sheets()[8].nrows):
                if n_1 == 0:
                    continue
                else:
                    hostName = workbook.sheets()[8].cell(n_1, 0).value
                    if hostName == '':
                        break
                    hostGroupName = workbook.sheets()[8].cell(n_1, 1).value
                    if hostGroupName == '':
                        break
                    try:
                        zabbix.hostGroup_massremove(hostName, hostGroupName)
                    except Exception as e:
                        print u"Sheet3表第\033[041m%s\033[0m行数据异常\n\033[041m%s\033[0m" % (n_1 + 1, e)
                        sys.exit(1)
