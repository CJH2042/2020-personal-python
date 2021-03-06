import json
import os
import argparse
import time

class Data:
    def __init__(self,addr:str = None,reload:int = 0):
        self.uevent = {}
        self.revent = {}
        self.urevent = {}
        if reload == 1:
            self.read_data(addr)
            self.savetolocal()
        if (addr is None and not os.path.exists('1.json')
            ) and not os.path.exists('2.json') and not os.path.exists('3.json'):
            raise RuntimeError('error: init failed')

        x = open('1.json', 'r', encoding = 'utf-8').read()
        self.localu = json.loads(x)
        x = open('2.json', 'r', encoding = 'utf-8').read()
        self.localr = json.loads(x)
        x = open('3.json', 'r', encoding = 'utf-8').read()
        self.localur = json.loads(x)

    def read_data(self,addr:str):
        #解析文件夹中所有的json
        for root, dic, files in os.walk(addr):
            for f in files:
                if f[-5:] == ".json":
                    jpath = f
                    self.analyse(addr,jpath)
       


    def analyse(self,addr:str,jpath:str):
        #解析单个json
        f = open(addr+'\\'+jpath,'r', encoding = 'utf-8')
        try:
            while True:
                stmp = f.readline()
                #一行一行读入
                if stmp:
                    dtmp = json.loads(stmp)
                    if not dtmp["type"] in ['PushEvent','IssueCommentEvent',
                                            'IssuesEvent','PullRequestEvent']:
                        continue
                    if not dtmp["actor"]["login"] in self.uevent.keys():
                        event = {'PushEvent':0,'IssueCommentEvent':0,
                               'IssuesEvent':0,'PullRequestEvent':0}
                        self.uevent[dtmp["actor"]["login"]] = event
                    if not dtmp["repo"]["name"] in self.revent.keys():
                        event = {'PushEvent':0,'IssueCommentEvent':0,
                               'IssuesEvent':0,'PullRequestEvent':0}
                        self.revent[dtmp["repo"]["name"]] = event
                    if not dtmp["actor"]["login"]+dtmp["repo"]["name"] in self.urevent.keys():
                        event = {'PushEvent': 0, 'IssueCommentEvent': 0,
                                 'IssuesEvent': 0, 'PullRequestEvent': 0}
                        self.urevent[dtmp["actor"]["login"]+dtmp["repo"]["name"]] = event
                        
                    self.uevent[dtmp["actor"]["login"]][dtmp['type']] += 1
                    self.revent[dtmp["repo"]["name"]][dtmp['type']] += 1
                    self.urevent[dtmp["actor"]["login"] + dtmp["repo"]["name"]][dtmp['type']] += 1
                else:
                    break
        except:
            pass
        finally:
            f.close()
    def savetolocal(self):
        #初始化数据保存到本地
        with open('1.json', 'w', encoding = 'utf-8') as f:
            json.dump(self.uevent,f)
        with open('2.json', 'w', encoding = 'utf-8') as f:
            json.dump(self.revent,f)
        with open('3.json', 'w', encoding = 'utf-8') as f:
            json.dump(self.urevent,f)

    def query_u(self, user:str, event: str):
        if not user in self.localu.keys():
            return 0
        return self.localu[user][event]

    def query_r(self, repo: str, event: str):
        if not self.localr.get(repo, 0):
            return 0
        return self.localr[repo][event]
    
    def query_ur(self,user:str,repo:str,event: str):
        if not self.localur.get(user+repo,0):
            return 0
        return self.localur[user+repo][event]
    
class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')
        print(self.analyse())
        
    def analyse(self):
        if self.parser.parse_args().init:
            self.data = Data(self.parser.parse_args().init, 1)
            return 0
        else:
            if self.data is None:
                self.data = Data()
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        res = self.data.query_ur(
                            self.parser.parse_args().user,
                            self.parser.parse_args().repo,
                            self.parser.parse_args().event)
                    else:
                        res = self.data.query_u(
                            self.parser.parse_args().user,
                            self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    res = self.data.query_r(
                        self.parser.parse_args().repo,
                        self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -u or -r are required')
            else:
                raise RuntimeError('error: argument -e is required')
        return res


if __name__ == '__main__':
   
    run=Run()
