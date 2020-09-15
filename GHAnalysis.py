import json
import os
import argparse

class Data:
    def __init__(self, addr: int = None, reload: int = 0):
        if reload == 1:
            self.__init(addr)
        if (addr is None and not os.path.exists('1.json')
            ) and not os.path.exists('2.json') and not os.path.exists('3.json'):
            raise RuntimeError('error: init failed')
        x = open('1.json', 'r', encoding='utf-8').read()
        self.P4E = json.loads(x)
        x = open('2.json', 'r', encoding='utf-8').read()
        self.R4E = json.loads(x)
        x = open('3.json', 'r', encoding='utf-8').read()
        self.PandR4E = json.loads(x)

    def __init(self, addr: str):
        json_list = []
        for root, dic, files in os.walk(addr):
            for f in files:
                if f[-5:] == '.json':
                    json_path = f
                    x = open(addr+'\\'+json_path,
                             'r', encoding='utf-8').read()
                    str_list = [_x for _x in x.split('\n') if len(_x) > 0]
                    for i, _str in enumerate(str_list):
                        try:
                            json_list.append(json.loads(_str))
                        except:
                            pass
        records = self.ListD(json_list)
        self.P4E = {}
        self.R4E = {}
        self.PandR4E = {}
        for i in records:
            if not self.P4E.get(i['actor__login'], 0):
                self.P4E.update({i['actor__login']: {}})
                self.PandR4E.update({i['actor__login']: {}})
            self.P4E[i['actor__login']
                     ][i['type']] = self.P4E[i['actor__login']].get(i['type'], 0)+1
            if not self.R4E.get(i['repo__name'], 0):
                self.R4E.update({i['repo__name']: {}})
            self.R4E[i['repo__name']
                     ][i['type']] = self.R4E[i['repo__name']].get(i['type'], 0)+1
            if not self.PandR4E[i['actor__login']].get(i['repo__name'], 0):
                self.PandR4E[i['actor__login']].update({i['repo__name']: {}})
            self.PandR4E[i['actor__login']
                         ][i['repo__name']
                           ][i['type']] = self.PandR4E[i['actor__login']
                                                       ][i['repo__name']].get(i['type'], 0)+1
        with open('1.json', 'w', encoding='utf-8') as f:
            json.dump(self.P4E,f)
        with open('2.json', 'w', encoding='utf-8') as f:
            json.dump(self.R4E,f)
        with open('3.json', 'w', encoding='utf-8') as f:
            json.dump(self.PandR4E,f)

    def parse(self, d: dict, prefix: str):
        _d = {}
        for k in d.keys():
            if str(type(d[k]))[-6:-2] == 'dict':
                _d.update(self.parse(d[k], k))
            else:
                _k = f'{prefix}__{k}' if prefix != '' else k
                _d[_k] = d[k]
        return _d

    def ListD(self, a: list):
        records = []
        for d in a:
            _d = self.parse(d, '')
            records.append(_d)
        return records

    def getU(self, username: str, event: str) -> int:
        if not self.P4E.get(username,0):
            return 0
        else:
            return self.P4E[username].get(event,0)

    def getR(self, reponame: str, event: str) -> int:
        if not self.R4E.get(reponame,0):
            return 0
        else:
            return self.R4E[reponame].get(event,0)

    def getUandR(self, username: str, reponame: str, event: str) -> int:
        if not self.P4E.get(username,0):
            return 0
        elif not self.PandR4E[username].get(reponame,0):
            return 0
        else:
            return self.PandR4E[username][reponame].get(event,0)


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.argInit()
        print(self.analyse())

    def argInit(self):
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

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
                        res = self.data.getUandR(
                            self.parser.parse_args().user,
                            self.parser.parse_args().repo,
                            self.parser.parse_args().event)
                    else:
                        res = self.data.getU(
                            self.parser.parse_args().user,
                            self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    res = self.data.getR(
                        self.parser.parse_args().reop,
                        self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -u or -r are required')
            else:
                raise RuntimeError('error: argument -e is required')
        return res


if __name__ == '__main__':
    a = Run()
