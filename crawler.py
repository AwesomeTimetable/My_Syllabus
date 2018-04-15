#!/usr/bin/env python3

# This crawler scrape your course table
# from 4m3.tongji.edu.cn

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery

class course(object):
    def __init__(self,class_list):
        if class_list.find('\n')==-1:
            class_info=class_list.split()
            self.id=class_info[0]
            self.name=class_info[-1]
            self.teacher=class_info[1]
            if(len(class_info)==7):
                self.location=[class_info[-2]]
            else:
                self.location=None
            self.time=[class_info[2]+' '+class_info[3]]
        else:
            class_list.replace('\n',' ')
            class_info=class_list.split()
            self.id=class_info[0]
            self.name=class_info[-1]
            self.teacher=class_info[1]
            self.location=[class_info[5],class_info[10]]
            self.time=[class_info[2]+' '+class_info[3],class_info[7]+' '+class_info[8]]

    def show(self):
        print(self.id)
        print(self.name)
        print(self.teacher)
        print(self.location)
        print(self.time)

    def get_course_info(self):
        course_info={
            'id':self.id,
            'name':self.name,
            'teacher':self.teacher,
            'location':self.location,
            'time':self.time,
        }
        return course_info

def login(header,s):
    '''登陆4m3'''
    username=input('your student id')
    password=intput('your password')
    startURL='http://4m3.tongji.edu.cn/eams/login.action'
    href='http://4m3.tongji.edu.cn/eams/samlCheck'
    res=s.get(startURL)
    header['Upgrade-Insecure-Requests']='1'
    res=s.get(href,headers=header)
    soup=BeautifulSoup(res.content,'html.parser')
    jumpURL=soup.meta['content'][6:]
    header['Accept-Encoding']='gzip, deflate, sdch, br'
    res=s.get(jumpURL,headers=header)

    soup=BeautifulSoup(res.content,'html.parser')
    logPageURL='https://ids.tongji.edu.cn:8443'+soup.form['action']
    res=s.get(logPageURL,headers=header)

    data={'option':'credential','Ecom_User_ID':username,'Ecom_Password':password,'submit':'登录'}
    soup=BeautifulSoup(res.content,'html.parser')
    loginURL=soup.form['action']
    res=s.post(loginURL,headers=header,data=data)

    soup=BeautifulSoup(res.content,'html.parser')
    str=soup.script.string
    str=str.replace('<!--',' ')
    str=str.replace('-->',' ')
    str=str.replace('top.location.href=\'',' ')
    str=str.replace('\';',' ')
    jumpPage2=str.strip()
    res=s.get(jumpPage2,headers=header)

    soup=BeautifulSoup(res.content,'html.parser')
    message={}
    messURL=soup.form['action']
    message['SAMLResponse']=soup.input['value']
    message['RelayState']=soup.input.next_sibling.next_sibling['value']
    res=s.post(messURL,headers=header,data=message)


def get_course_table(header,s):
    # get ids 
    id_url='http://4m3.tongji.edu.cn/eams/courseTableForStd.action?_='
    req_id=s.get(id_url,headers=header)
    find_text="addInput(form,\"ids\","
    my_file=str(req_id.text)
    start_index=my_file.find(find_text)+len(find_text)+1
    ids=my_file[start_index:start_index+9]
    # get semester_id
    find_text="value:\""
    start_index=my_file.find(find_text)+len(find_text)
    semester_id=my_file[start_index:start_index+3]
    
    form_data={
        'ignoreHead':1,
        'startWeek':1,
        'semester.id':str(semester_id),
        'ids': ids,
        'setting.kind': 'std'
    }
    #print(form_data)
    table_url='http://4m3.tongji.edu.cn/eams/courseTableForStd!courseTable.action'
    req_table=s.post(table_url,headers=header,data=form_data)
    return req_table

def parse_table(req_table):
    req_bs=BeautifulSoup(req_table.text)
    raw_table_info=req_bs.findAll('tbody')[0]
    course_info_list=raw_table_info.findAll('td')
    n_class=int(len(course_info_list)/11)
    class_info_list=[]
    for i in range(n_class):
        class_id_num=i*11+1
        class_info_num=i*11+8
        class_name_num=i*11+2
        class_id=str(course_info_list[class_id_num])
        class_name=str(course_info_list[class_name_num])
        class_info=str(course_info_list[class_info_num])
        class_id=str(course_info_list[class_id_num])
        class_name_pq = PyQuery(class_name).text()
        class_info_pq = PyQuery(class_info).text()
        class_id_pq=PyQuery(class_id).text()
        class_name=class_name_pq.strip()
        class_info=class_info_pq.strip()
        class_id=class_id_pq.strip()
        class_info_list.append(class_id+' '+class_info+' '+class_name)
    my_class=[]
    for each_class in class_info_list:
        my_class.append(course(each_class))
    return my_class

s=requests.session()
header={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding': 'gzip, deflate, sdch',
'Accept-Language': 'zh-CN,zh;q=0.8','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
login(header,s)
print("login in succuessfully")
req_table=get_course_table(header,s)
my_table=parse_table(req_table)
# my_table here is a list that contains all course info
for each_course in my_table:
    each_course.show()
    print('--------')