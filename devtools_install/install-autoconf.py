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

autoconfBaseName = "autoconf"
autoconfBaseURL  = "http://ftp.gnu.org/gnu/autoconf/"
autoconfDefaultVersion = "2.69"
autoconfSupportedVersions = ["2.69"]
autoconfTarballVersions = {
  "2.69" : "2.69"
  }

#
# Script code
#


from InstallProgramDriver import *
from GeneralScriptSupport import *


class AutoconfInstall:

  def __init__(self):
    self.dummy = None

  #
  # Called before even knowing the product version
  #

  def getScriptName(self):
    return "install-autoconf.py"

  def getProductBaseName(self):
    return autoconfBaseName

  def getProductDefaultVersion(self):
    return autoconfDefaultVersion

  def getProductSupportedVersions(self):
    return autoconfSupportedVersions

  #
  # Called after knowing the product version but before parsing the
  # command-line.
  #

  def getURL(self, version):
    return autoconfBaseURL

  def getProductName(self, version):
    return autoconfBaseName+"-"+version

  def getBaseDirName(self, version):
    return autoconfBaseName+"-"+version+"-base"

  def getExtraHelpStr(self, version):
    return """
This script builds Autoconf"""+self.getProductName(version)+""" from source compiled with the
configured C compilers in your path.

NOTE: The assumed directory structure of the download source provided by the
command --download-cmnd=<download-cmnd> is:

   autoconf-<version>-base/
     autoconf-<full-version>.tar.gz
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
    self.autoconfBaseDir = self.baseDir+"/"+self.getBaseDirName(self.inOptions.version)
    autoconfVersionFull = autoconfTarballVersions[self.inOptions.version]
    self.autoconfTarball = "autoconf-"+autoconfVersionFull+".tar.gz"
    self.autoconfSrcDir = "autoconf-"+autoconfVersionFull
    self.autoconfBuildBaseDir = self.autoconfBaseDir+"/autoconf-build"
    self.scriptBaseDir = getScriptBaseDir()

  #
  # Called after setup()
  #

  def doDownload(self):
    removeDirIfExists(self.autoconfBaseDir, True)
    echoRunSysCmnd(self.inOptions.downloadCmnd)

  def doUntar(self):
    # Find the full name of the source tarball
    echoChDir(self.autoconfBaseDir)
    echoRunSysCmnd("tar -xzf "+self.autoconfTarball)

  def doConfigure(self):
    createDir(self.autoconfBuildBaseDir, True, True)
    echoRunSysCmnd(
      "../"+self.autoconfSrcDir+"/configure "+\
      " "+self.inOptions.extraConfigureOptions+\
      " --prefix="+self.inOptions.installDir,
      extraEnv={"CFLAGS":"-O3"},
      )

  def doBuild(self):
    echoChDir(self.autoconfBuildBaseDir)
    echoRunSysCmnd("make " + getParallelOpt(self.inOptions, "-j") \
      + self.inOptions.makeOptions)

  def doInstall(self):
    echoChDir(self.autoconfBuildBaseDir)
    echoRunSysCmnd("make " + getParallelOpt(self.inOptions, "-j") \
      + self.inOptions.makeOptions + " install")

  def writeModuleFile(self):
    module_file = open(self.inOptions.moduleDir + \
      "/" + self.getProductBaseName() + "-" + self.inOptions.version, 'w+')
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

    #Standard help
    module_file.write("proc ModulesHelp { } {\n")
    module_file.write("    puts stderr \" Loads $name-$version as a part of the MPACT development environment.\"\n" + \
      "}\n\n")

    #More info
    module_file.write("module-whatis \"" + \
      "Autoconf is an extensible package of M4 macros that produce " + \
      "shell scripts to automatically configure software source code packages." + \
      "\"\n")
    module_file.write("module-whatis \"Vendor Website: https://www.gnu.org/software/autoconf/\"\n")
    module_file.write("module-whatis \"        Manual: https://www.gnu.org/software/autoconf/manual/index.html\"\n")

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

autoconfInstaller = InstallProgramDriver(AutoconfInstall())
autoconfInstaller.runDriver()
