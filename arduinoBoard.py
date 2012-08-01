#! /usr/bin/env python

import os
import sys
import re

class Board:
    def __init__(self):
        self.configs = {}
        self.name = None

    def addConfig(self, config, value, parent):
        if not parent:
            self.configs.update(((config, value),))
            return

        try: parent = self.configs[parent]
        except:
            self.configs.update(((parent, {}),))
            parent = self.configs[parent]
        parent.update(((config, value),))

    def getConfig(self, config, parent=None):
        try:
            if parent:
                return self.configs[parent][config]
            else:
                return self.configs[config]
        except:
            return None

    def __str__(self):
        if self.name:
            name = self.name
        else:
            name = "Unknown name"
        s = name + ':\n'
        for config in self.configs:
            value = self.configs[config]
            if isinstance(value, str):
                s += config + ":" + value + '\n'
            else:
                for child in value:
                    childvalue = value[child]
                    s += config + ":" + child + ":" + childvalue + '\n'

        return s

class BoardFileParser:
    reStart = re.compile(r'^[#]+$')
    reCfg = re.compile(r'^(?P<name>\w+)[.]((?P<parent>\w+)[.])?(?P<config>\w+)=' + \
                       r'(?P<value>\w+)')

    def __init__(self, cfilename, ctx=None):
        self.filename = cfilename
        self.ctx = ctx
        try: self.file = open(cfilename, 'r')
        except:
            if ctx:
                ctx.fatal("Couldn't open " + self.filename + "\n")
            else:
                sys.stderr.write("Couldn't open " + self.filename + "\n")

    def parseABoardConfig(self, boardName=None):
        #Lines look like
        #atmega8.upload.protocol=arduino
        boards = []

        newBoard = None
        line = self.file.readline()
        while line != "":
            if self.reStart.match(line):
                if newBoard and newBoard.name:
                    #Add the last board we store configs for
                    boards.append(newBoard)
                newBoard = Board()
                line = self.file.readline()
                continue

            if not newBoard:
                line = self.file.readline()
                continue

            if line == '\n' or line == '\r' or line == '\r\n':
                line = self.file.readline()
                continue

            result = self.reCfg.match(line)
            if not result:
                line = self.file.readline()
                continue

            try: parent = result.group('parent')
            except: parent = None
            name = result.group('name')
            config = result.group('config')
            value = result.group('value')

            if boardName and name != boardName:
                line = self.file.readline()
                continue

            newBoard.addConfig(config, value, parent)
            if not newBoard.name:
                newBoard.name = name
            elif name != newBoard.name:
                sys.stderr.write("Config file has mixed board names\n")

            line = self.file.readline()

        #Make sure we get last one in
        if newBoard and newBoard.name:
            #Add the last board we store configs for
            boards.append(newBoard)

        return boards

if __name__ == "__main__":
    parser = BoardFileParser(sys.argv[1])
#    boards = parser.parseABoardConfig()
#    for aboard in boards:
#        print aboard

    boards = parser.parseABoardConfig(boardName='atmega328')
    print len(boards)
    print boards[0]

