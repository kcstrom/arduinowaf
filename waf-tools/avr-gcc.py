#! /usr/bin/env python
# encoding: utf-8

import os,sys
from waflib import Configure,Options,Utils
from waflib.Tools import ccroot
from waflib.Configure import conf
from waflib import Task
from waflib.TaskGen import extension, feature, after_method

def find_avr_gcc(conf):
	cc=conf.find_program(['avr-gcc'],var='CC')
	cc=conf.cmd_to_list(cc)
	conf.get_cc_version(cc,gcc=True)
	conf.env.CC_NAME='avr-gcc'
	conf.env.CC=cc

	ar=conf.find_program(['avr-ar'])
	conf.env.AR=ar
	conf.env.ARFLAGS='rcs'

	prog=conf.find_program(['avr-objcopy'])
	conf.env.OBJCOPY=prog
	prog=conf.find_program(['avr-objdump'])
	conf.env.OBJDUMP=prog
	prog=conf.find_program(['avr-size'])
	conf.env.SIZE=prog
	prog=conf.find_program(['avr-nm'])
	conf.env.SIZE=prog

	#prog=conf.find_program(['avr-ld'])
	#conf.env.LD=prog
	#conf.env.LINK_CC=prog
	#conf.env.LINK_CXX=prog

def avr_gcc_common_flags(conf):
	v=conf.env
	v['CC_SRC_F']=[]
	v['CC_TGT_F']=['-c','-o']
	if not v['LINK_CC']:v['LINK_CC']=v['CC']
	v['CCLNK_SRC_F']=[]
	v['CCLNK_TGT_F']=['-o']
	v['CPPPATH_ST']='-I%s'
	v['DEFINES_ST']='-D%s'
	v['LIB_ST']='-l%s'
	v['LIBPATH_ST']='-L%s'
	v['STLIB_ST']='-l%s'
	v['STLIBPATH_ST']='-L%s'
	v['RPATH_ST']='-Wl,-rpath,%s'
	v['SONAME_ST']='-Wl,-h,%s'
	v['SHLIB_MARKER']='-Wl,-Bdynamic'
	v['STLIB_MARKER']='-Wl,-Bstatic'
	v['cprogram_PATTERN']='%s'
	v['CFLAGS_cshlib']=['-fPIC']
	v['LINKFLAGS_cshlib']=['-shared']
	v['cshlib_PATTERN']='lib%s.so'
	v['LINKFLAGS_cstlib']=['-Wl,-Bstatic']
	v['cstlib_PATTERN']='lib%s.a'
	v['LINKFLAGS_MACBUNDLE']=['-bundle','-undefined','dynamic_lookup']
	v['CFLAGS_MACBUNDLE']=['-fPIC']
	v['macbundle_PATTERN']='%s.bundle'
def avr_gcc_modifier_win32(conf):
	v=conf.env
	v['cprogram_PATTERN']='%s.exe'
	v['cshlib_PATTERN']='%s.dll'
	v['implib_PATTERN']='lib%s.dll.a'
	v['IMPLIB_ST']='-Wl,--out-implib,%s'
	v['CFLAGS_cshlib']=[]
	v.append_value('CFLAGS_cshlib',['-DDLL_EXPORT'])
	v.append_value('LINKFLAGS',['-Wl,--enable-auto-import'])
def avr_gcc_modifier_cygwin(conf):
	avr_gcc_modifier_win32(conf)
	v=conf.env
	v['cshlib_PATTERN']='cyg%s.dll'
	v.append_value('LINKFLAGS_cshlib',['-Wl,--enable-auto-image-base'])
	v['CFLAGS_cshlib']=[]
def avr_gcc_modifier_darwin(conf):
	v=conf.env
	v['CFLAGS_cshlib']=['-fPIC','-compatibility_version','1','-current_version','1']
	v['LINKFLAGS_cshlib']=['-dynamiclib']
	v['cshlib_PATTERN']='lib%s.dylib'
	v['FRAMEWORKPATH_ST']='-F%s'
	v['FRAMEWORK_ST']=['-framework']
	v['ARCH_ST']=['-arch']
	v['LINKFLAGS_cstlib']=[]
	v['SHLIB_MARKER']=[]
	v['STLIB_MARKER']=[]
	v['SONAME_ST']=[]
def avr_gcc_modifier_aix(conf):
	v=conf.env
	v['LINKFLAGS_cprogram']=['-Wl,-brtl']
	v['LINKFLAGS_cshlib']=['-shared','-Wl,-brtl,-bexpfull']
	v['SHLIB_MARKER']=[]
def avr_gcc_modifier_hpux(conf):
	v=conf.env
	v['SHLIB_MARKER']=[]
	v['CFLAGS_cshlib']=['-fPIC','-DPIC']
	v['cshlib_PATTERN']='lib%s.sl'
def avr_gcc_modifier_platform(conf):
	gcc_modifier_func=getattr(conf,'gcc_modifier_'+conf.env.DEST_OS,None)
	if gcc_modifier_func:
		gcc_modifier_func()
def configure(conf):
	conf.find_avr_gcc()
	#conf.find_ar()
	conf.avr_gcc_common_flags()
	conf.avr_gcc_modifier_platform()
	conf.cc_load_tools()
	conf.cc_add_flags()
	conf.link_add_flags()

class makeEEP(Task.Task):
    def run(self):
        cmd = self.env.OBJCOPY
        cmd += ' -O ihex -j .eeprom --set-section-flags=.eeprom=alloc,load'
        cmd += ' --no-change-warnings --change-section-lma .eeprom=0 '
        cmd += self.inputs[0].relpath() + ' ' + self.outputs[0].relpath()
        self.exec_command(cmd)

class makeHex(Task.Task):
    def run(self):
        cmd = self.env.OBJCOPY
        cmd += ' -O ihex -R .eeprom '
        cmd += self.inputs[0].relpath() + ' ' + self.outputs[0].relpath()
        self.exec_command(cmd)

@feature('avr-gcc')
@after_method('apply_link')
def avr_objcopy_tskgen(tgen):
    if not hasattr(tgen, 'link_task') or not tgen.link_task:
        return []
        #tgen.env.fatal("There must be a link task to process")

    if not tgen.link_task.outputs[0].name.endswith('.elf'):
        return []
        #tgen.env.fatal("Link task must end with .elf")

    out = tgen.link_task.outputs[0].change_ext('.eep')
    tsk =tgen.create_task('makeEEP', tgen.link_task.outputs[0], out)

    outhex = tgen.link_task.outputs[0].change_ext('.hex')
    tskHex = tgen.create_task('makeHex', tgen.link_task.outputs[0], outhex)
    return [tsk, tskHex]

conf(find_avr_gcc)
conf(avr_gcc_common_flags)
conf(avr_gcc_modifier_win32)
conf(avr_gcc_modifier_cygwin)
conf(avr_gcc_modifier_darwin)
conf(avr_gcc_modifier_aix)
conf(avr_gcc_modifier_hpux)
conf(avr_gcc_modifier_platform)