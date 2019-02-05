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


#
# Defaults
#

cmakeBaseName = "cmake"
cmakeBaseURL  = "https://cmake.org/files/"
cmakeDefaultVersion = "3.10.2"
cmakeSupportedVersions = ["2.8.11",
                          "3.1.1",
                          "3.3.2",
                          "3.4.0",
                          "3.4.1",
                          "3.4.3",
                          "3.5.1",
                          "3.6.2",
                          "3.10.2"]
cmakeTarballVersions = {
  "2.8.11" : "2.8.11.2",
  "3.1.1" : "3.1.1",
  "3.3.2" : "3.3.2",
  "3.4.0" : "3.4.0",
  "3.4.1" : "3.4.1",
  "3.4.3" : "3.4.3",
  "3.5.1" : "3.5.1",
  "3.6.2" : "3.6.2",
  "3.10.2" : "3.10.2",
  }

# NOTES:
#
# See the patch files for 2.8.11 and 3.1.1 for CPack in the untar() function!

#
# Script code
#

from InstallProgramDriver import *
from GeneralScriptSupport import *


class CMakeInstall:

  def __init__(self):
    self.dummy = None

  #
  # Called before even knowing the product version
  #

  def getScriptName(self):
    return "install-cmake.py"

  def getProductBaseName(self):
    return cmakeBaseName

  def getProductDefaultVersion(self):
    return cmakeDefaultVersion

  def getProductSupportedVersions(self):
    return cmakeSupportedVersions

  #
  # Called after knowing the product version but before parsing the
  # command-line.
  #

  def getURL(self, version):
    return cmakeBaseURL+"v"+re.sub('\..$','',version)+"/"

  def getProductName(self, version):
    return cmakeBaseName+"-"+version

  def getBaseDirName(self, version):
    return cmakeBaseName+"-"+version+"-base"

  def getExtraHelpStr(self, version):
    return """
This script builds """+self.getProductName(version)+""" from source compiled with the
configured C/C++ compilers in your path.  Note that the provided CMake
configure script actually builds a local bootstrap copy of CMake first, before
building the final version of CMake and the rest of the tools that gets
installed.

NOTE: This build script sets the environment vars CXXFLAGS=-O3 AND CFLAGS=-O3
when doing the configure.  Therefore, this builds and installs an optimized
version of CMake by default.

NOTE: The assumed directory structure of the download source provided by the
command --download-cmnd=<download-cmnd> is:

   cmake-<version>-base/
     cmake-<full-version>.tar.gz
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
      help="Extra options to add to the 'configure' command for "+self.getProductName(version)+"." \
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
    self.cmakeBaseDir = self.baseDir+"/"+self.getBaseDirName(self.inOptions.version)
    cmakeVersionFull = cmakeTarballVersions[self.inOptions.version]
    self.cmakeTarball = "cmake-"+cmakeVersionFull+".tar.gz"
    self.cmakeSrcDir = "cmake-"+cmakeVersionFull
    self.cmakeBuildBaseDir = self.cmakeBaseDir+"/cmake-build"
    self.scriptBaseDir = getScriptBaseDir()

  #
  # Called after setup()
  #

  def doDownload(self):
    removeDirIfExists(self.cmakeBaseDir, True)
    echoRunSysCmnd(self.inOptions.downloadCmnd)

  def doUntar(self):
    # Find the full name of the source tarball
    echoChDir(self.cmakeBaseDir)
    echoRunSysCmnd("tar -xzf "+self.cmakeTarball)
    if self.inOptions.version == "2.8.11" or self.inOptions.version == "3.1.1":
      echoChDir(self.cmakeSrcDir+"/Source/CPack")
      echoRunSysCmnd("patch -i ../../../fix_cpack_symlink.patch")
    elif self.inOptions.version == "3.3.2" or self.inOptions.version == "3.4.0":
      echoChDir(self.cmakeSrcDir+"/Source")
      echoRunSysCmnd("patch -i ../../remove_getrealpath.patch")

  def doConfigure(self):
    createDir(self.cmakeBuildBaseDir, True, True)
    echoRunSysCmnd(
      "../"+self.cmakeSrcDir+"/configure "+\
      " "+self.inOptions.extraConfigureOptions+\
      getParallelOpt(self.inOptions, "--parallel=")+\
      " --prefix="+self.inOptions.installDir,
      extraEnv={"CXXFLAGS":"-O3", "CFLAGS":"-O3"},
      )

  def doBuild(self):
    echoChDir(self.cmakeBuildBaseDir)
    echoRunSysCmnd("make "+getParallelOpt(self.inOptions, "-j")+self.inOptions.makeOptions)

  def doInstall(self):
    echoChDir(self.cmakeBuildBaseDir)
    echoRunSysCmnd("make "+self.inOptions.makeOptions+" install")

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
    module_file.write("prepend-path   PATH            $modroot/bin\n")

    #Standard help
    module_file.write("proc ModulesHelp { } {\n")
    module_file.write("    puts stderr \" Loads $name-$version as a part of the MPACT development environment.\"\n" + \
      "}\n\n")

    #More info
    module_file.write("module-whatis \"" + \
      "CMake is an open-source, cross-platform family of tools designed to build," + \
      "test and package software." + \
      "\"\n")
    module_file.write("module-whatis \"Vendor Website: https://cmake.org/\"\n")
    module_file.write("module-whatis \"        Manual: https://cmake.org/documentation/\"\n")

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

cmakeInstaller = InstallProgramDriver(CMakeInstall())
cmakeInstaller.runDriver()
