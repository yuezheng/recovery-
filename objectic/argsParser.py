#!/usr/bin/python

import sys,getopt

class argParser():
    def __init__(self,args=sys.argv[1:],argsName="i:h:t"):
        self.args = args
        self.argsName = argsName
        self.infoList = []

    def parseArgs(self):
        opts,args = getopt.getopt(self.args,self.argsName)
        for k,v in opts:
            if k == '-i':
                self.infoList.append(v)
            if k == '-h':
                self.infoList.append(v)
            if k == '-t':
                self.infoList.append(v)
        return self.infoList

if __name__ == "__main__":
    parser = argParser()
    parser.parseArgs()
