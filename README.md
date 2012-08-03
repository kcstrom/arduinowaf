arduinowaf
==========

A waf script and tools to allow easy building and loading of arduino software
from command line.

License
------------
The software in this git repository is licensed under the same license as
waf itself, the BSD license: http://opensource.org/licenses/bsd-license.php.
Basically - give credit as to where you got the sources:
https://github.com/kcstrom/arduinowaf

Instructions for use
-----------
Note, this has only been tested in Linux so far. It should work for Windows,
but I have yet to test it.

1. Drop the waf (tested with waf 1.6.11) executable binary into the root
   directory of this source.
2. Edit config.ini to indicate:
   board - The Arduino board you are building for and uploading to. This value
     needs to match one from the boards.txt that is installed with the Arduino
     sources.
   dir - Set this to a comma or space separated list of directories for which
         you want to build all .c and .cpp files in.
   files - Set this to a comma or space separated list of individual files with
           paths relative to the location of config.ini. This can be used
           instead of or in additoin to dir
   arduino - This doesn't matter currently.
   installPath - The path to the root directory of the Arduino install.
   libraries - Set this to the directory name of any libraries you want to be
               a part of the build.
3. Run waf configure: ./waf-1.6.11 configure or python waf-1.6.11
4. Build software: ./waf-1.6.11 build
5. Upload to board: ./waf-1.6.11 upload