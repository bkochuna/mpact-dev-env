#!/usr/bin/env python

# @HEADER
# ************************************************************************
#
#            TriBITS: Tribal Build, Integrate, and Test System
#                    Copyright 2013 Sandia Corporation
#
# Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the Corporation nor the names of the
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY SANDIA CORPORATION "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL SANDIA CORPORATION OR THE
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ************************************************************************
# @HEADER
import sys

#
# Defaults
#

gccBaseName = "gcc"
gccBaseURL  = "https://ftp.gnu.org/gnu/gcc/"
gccDefaultVersion = "5.4.0"
gccSupportedVersions = ["4.8.3",
                        "4.8.5",
                        "5.4.0"]
gccTarballVersions = {
  "4.8.3" : "4.8.3",
  "4.8.5" : "4.8.5",
  "5.4.0" : "5.4.0",
  }


#allows for any user-specified version of gcc to be installed --EHC
for arg in sys.argv[1:]:
  if "version" in arg and "gcc" in arg:
    gccSupportedVersions.append(arg.split("=")[1])
    break


#
# Script code
#


from InstallProgramDriver import *
from GeneralScriptSupport import *


class GccInstall:

  def __init__(self):
    self.dummy = None

  #
  # Called before even knowing the product version
  #

  def getScriptName(self):
    return "install-gcc.py"

  def getProductBaseName(self):
    return gccBaseName

  def getProductDefaultVersion(self):
    return gccDefaultVersion

  def getProductSupportedVersions(self):
    return gccSupportedVersions

  #
  # Called after knowing the product version but before parsing the
  # command-line.
  #

  def getURL(self, version):
    url = gccBaseURL+gccBaseName+"-"+version+"/"
    return url

  def getProductName(self, version):
    return gccBaseName+"-"+version

  def getBaseDirName(self, version):
    return gccBaseName+"-"+version+"-base"

  def getExtraHelpStr(self, version):
    return """
This script builds """+self.getProductName(version)+""" from source compiled with the
configured C compilers in your path.

NOTE: The assumed directory structure of the download source provided by the
command --download-cmnd=<download-cmnd> is:

   gcc-<version>-base/
     gcc-<full-version>.tar.gz
"""

  def setDownloadCmndOption(self, clp, version):
    url = self.getURL(version)
    productName = self.getProductBaseName()+"-"+version
    productBaseDirName = productName+"-base"
    productTarball = productName+".tar.gz"

    defaultDownloadCmnd = \
      "wget -P "+productBaseDirName+" "+url+productTarball
    clp.add_option(
      "--download-cmnd", dest="downloadCmnd", type="string",
      default=defaultDownloadCmnd,
      help="Command used to download source for "+productName+"." \
        +"  (Default ='"+defaultDownloadCmnd+"')  WARNING: This will delete" \
        +" an existing directory '"+productBaseDirName+"' if it already exists!")

  def injectExtraCmndLineOptions(self, clp, version):
    self.setDownloadCmndOption(clp, version)
    clp.add_option(
      "--extra-configure-options", dest="extraConfigureOptions", type="string", \
      default="", \
      help="Extra options to add to the 'configure' command for " \
        + self.getProductName(version)+"." \
        +"  Note: This does not override the hard-coded configure options." )

  def echoExtraCmndLineOptions(self, inOptions):
    cmndLine = ""
    cmndLine += "  --download-cmnd='"+inOptions.downloadCmnd+"' \\\n"
    cmndLine += "  --extra-configure-options='"+inOptions.extraConfigureOptions+"' \\\n"
    return cmndLine

  #
  # Called after parsing the command-line
  #

  def setup(self, inOptions):
    self.inOptions = inOptions
    self.baseDir = os.getcwd()
    self.gccBaseDir = self.baseDir+"/"+self.getBaseDirName(self.inOptions.version)
    gccVersionFull = gccTarballVersions[self.inOptions.version]
    self.gccSrcDir = "gcc-"+gccVersionFull
    self.gccBuildBaseDir = self.gccBaseDir+"/gcc-build"
    self.scriptBaseDir = getScriptBaseDir()
    self.gccTarball = "gcc-"+gccVersionFull+".tar.gz"

  #
  # Called after setup()
  #

  def doDownload(self):
    removeDirIfExists(self.gccBaseDir, True)
    echoRunSysCmnd(self.inOptions.downloadCmnd)

  def doUntar(self):
     echoChDir(self.gccBaseDir)
     echoRunSysCmnd("tar -xzf "+self.gccTarball)

  def doConfigure(self):
    createDir(self.gccBuildBaseDir)
    echoRunSysCmnd(
      "../"+self.gccSrcDir+"/configure --disable-multilib --enable-languages='c,c++,fortran'"+\
      " "+self.inOptions.extraConfigureOptions+\
      " --prefix="+self.inOptions.installDir,
      workingDir=self.gccBuildBaseDir,
      extraEnv={"CFLAGS":"-O3"},
      )

  def doBuild(self):
    echoChDir(self.gccBuildBaseDir)
    echoRunSysCmnd("make " + getParallelOpt(self.inOptions, "-j") \
      + self.inOptions.makeOptions)

  def doInstall(self):
    echoChDir(self.gccBuildBaseDir)
    echoRunSysCmnd("make " + getParallelOpt(self.inOptions, "-j") \
      + self.inOptions.makeOptions + " install")

  def writeModuleFile(self):
    moduleDir = self.inOptions.moduleDir+"/"+self.getProductBaseName()+"/"
    createDir(moduleDir, False, True)
    module_file = open(moduleDir + "/" + self.inOptions.version, 'w+')
    module_file.write("#%Module\n\n")

    #Always conflicts with itself
    module_file.write("conflict " + self.getProductBaseName() + "\n\n")

    #Prerequisites
    #TODO: Figure out how to handle...

    #Standard pre-amble/script variables
    root = self.inOptions.installDir.replace( \
      self.getProductBaseName()+"-"+self.inOptions.version,"")
    module_file.write("set  root      " + root + "\n")
    module_file.write("set  version   " + self.inOptions.version + "\n")
    module_file.write("set  app       " + self.getProductBaseName()  + "\n")
    module_file.write("set  modroot   $root/$app-$version\n\n")

    #How environment needs to modified (package specific)
    module_file.write("prepend-path   MANPATH         $modroot/share/man\n")
    module_file.write("prepend-path   PATH            $modroot/bin\n")
    module_file.write("prepend-path   LD_LIBRARY_PATH $modroot/lib\n")

    #Standard help
    module_file.write("proc ModulesHelp { } {\n")
    module_file.write("    puts stderr \" Loads $name-$version as a part of the MPACT development environment.\"\n" + \
      "}\n\n")

    #More info
    module_file.write("module-whatis \"GNU compiler collection " + \
      "includes front ends for C, C++, Objective-C, Fortran, Ada, Go, and D, " + \
      "as well as libraries for these languages (libstdc++,...).\"\n")
    module_file.write("module-whatis \"Vendor Website: https://gcc.gnu.org/\"\n")
    module_file.write("module-whatis \"        Manual: https://gcc.gnu.org/onlinedocs/\"\n")

    module_file.close()

  def getFinalInstructions(self):
    return """
    To use the installed version of """+self.getProductBaseName()+"""-"""+ \
      self.inOptions.version+"""with environment modules
    modify your MODULEPATH environment variable from the command line with:

    $ export MODULEPATH="""+self.inOptions.moduleDir+""":$MODULEPATH

    Or modify your .bashrc (or other login script) and that should be it!"""


#
# Executable statements
#

gccInstaller = InstallProgramDriver(GccInstall())
gccInstaller.runDriver()
