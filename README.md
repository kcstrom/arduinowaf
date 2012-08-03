arduinowaf
==========

A waf script and tools to allow easy building and loading of arduino software
from command line.

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

License
------------
The software in this git repository is licensed under the same license as
waf itself, the BSD license: http://opensource.org/licenses/bsd-license.php.
Basically - give credit as to where you got the sources:
https://github.com/kcstrom/arduinowaf

Copyright (c) 2012, kcstrom
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
