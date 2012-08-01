#! /usr/bin/env python
# encoding: utf-8

import ConfigParser
import os

from arduinoBoard import *

from waflib import Logs

def options(opt):
    opt.load('c cxx')
    opt.load('avrdude', tooldir='waf-tools')

def configure(conf):
    conf.load('avr-gcc', tooldir='waf-tools')
    conf.load('avr-gxx', tooldir='waf-tools')
    conf.load('avrdude', tooldir='waf-tools')

def getLibSources(ctx, ardPath, libs):
    libBase = ardPath + os.sep + 'libraries'
    srcs = []
    includes = []
    for lib in libs:
        libNode = ctx.root.find_node(libBase + os.sep + lib)
        if not libNode:
            bld.fatal('Invalid library %s' % lib)
        includes.append(libNode)
        srcs += libNode.ant_glob('*.c')
        srcs += libNode.ant_glob('*.cpp')

    return (srcs, includes)

def getArduinoSources(ctx, ardPath):
    arduinoPath = ardPath + os.sep + 'hardware/arduino/cores/arduino/'
    ardNode = ctx.root.find_node(arduinoPath)
    if not ardNode:
        ctx.fatal('Arduino source path %s does not exist' % arduinoPath)

    sources = ardNode.ant_glob('*.c')
    sources += ardNode.ant_glob('*.cpp')

    return sources

def getConfig(bld):
    cp = ConfigParser.SafeConfigParser()
    try: cp.read('config.ini')
    except: bld.env.fatal('config.ini missing')

    defaultArdInstPath = '/usr/share/arduino/hardware/arduino/cores/arduino/'

    configs = type('config', (object,), {})
    try: configs.board = cp.get('hardware', 'board', 0)
    except: bld.fatal('You must specify the type of Arduino board')
    try: configs.srcDir = cp.get('sources', 'dir')
    except: configs.srcDir = None
    try: configs.srcFiles = cp.get('sources', 'files')
    except: configs.srcFiles = None
    if not configs.srcDir and not configs.srcFiles:
        bld.fatal('You must specify dir and/or files in sources section')
    try: configs.srcRm = cp.get('sources', 'remove')
    except: configs.srcRm = None
    try: configs.ardPath = cp.get('arduino', 'installPath')
    except:
        Logs.debug('arduino installPath not provided, using %s' %
                       defaultArdInstPath)
        configs.ardPath = defaultArdInstPath
    try: configs.libs = cp.get('arduino', 'libraries')
    except: pass

    if configs.srcFiles:
        configs.srcFiles = configs.srcFiles.split(' ,')
    else:
        configs.srcFiles = []
    if configs.srcDir:
        configs.srcDir = configs.srcDir.split(' ,')
        for srcDir in configs.srcDir:
            dirNode = bld.srcnode.find_node(srcDir)
            if not dirNode:
                bld.fatal('Could not find source directory ' + srcDir)
            configs.srcFiles += dirNode.ant_glob('*.c')
            configs.srcFiles += dirNode.ant_glob('*.cpp')

    if configs.libs:
        configs.libs = configs.libs.split(' ,')

    if configs.srcRm:
        configs.srcRm = configs.srcRm.split(' ,')
        for srcRm in configs.srcRm:
            rmNode = bld.srcnode.find_node(srcRm)
            try: configs.srcFiles.remove(rmNode)
            except: bld.fatal('No source %s to remove' % rmPath)

    #print configs.board
    #print configs.srcFiles
    #print configs.srcDir
    #print configs.ardPath

    parser = BoardFileParser(configs.ardPath + '/hardware/arduino/boards.txt',
                             ctx=bld)
    ardBoards = parser.parseABoardConfig(boardName=configs.board)
    if len(ardBoards) == 0:
        bld.fatal("Board %s not found." % configs.board)
    boardCfg = ardBoards[0]
    configs.mcu = boardCfg.getConfig('mcu', parent='build')
    configs.f_cpu = boardCfg.getConfig('f_cpu', parent='build')
    configs.protocol = boardCfg.getConfig('protocol', parent='upload')

    return configs

def upload(bld):
    config = getConfig(bld)

    bld(features='avrdude',
        source='build/firmware.hex',
        mcu=config.mcu,
        protocol=config.protocol)

def build(bld):
    config = getConfig(bld)

    projSources = config.srcFiles
    arduinoSources = getArduinoSources(bld, config.ardPath)
    libSources,libIncludes = getLibSources(bld, config.ardPath, config.libs)

    sources = projSources

    cflags = ['-mmcu=%s' % config.mcu,
              '-DF_CPU=%s' % config.f_cpu,
              '-MMD', '-DARDUINO=100', '-Os',
    		  '-ffunction-sections', '-fdata-sections', '-c', '-g', '-Wall',
              '-fno-exceptions', '-fno-strict-aliasing']

    bld(target='core',
        features='c cxx cxxstlib avr-gcc',
        source = arduinoSources,
        cflags=cflags,
        cxxflags=cflags,
        linkflags=['-Os', '-mmcu=%s' % config.mcu],
        includes=[config.ardPath + '/hardware/arduino/cores/arduino',
                  config.ardPath + '/hardware/arduino/variants/standard'])

    bld(target='firmware.elf',
        features='c cxx cprogram avr-gcc',
        source=sources + libSources,
        use='core',
        cflags=cflags,
        cxxflags=cflags,
        linkflags=['-Os', '-mmcu=%s' % config.mcu, '-lm'],
        includes=['roaster_main/',
                  config.ardPath + '/hardware/arduino/cores/arduino',
                  config.ardPath + '/hardware/arduino/variants/standard'] +
                  libIncludes)

