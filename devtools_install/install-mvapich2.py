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
mvapichBaseName = "mvapich2"
mvapichBaseURL  = "http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/"
mvapichDefaultVersion = "2.3"
mvapichSupportedVersions = ["2.3"]
mvapichTarballVersions = {
  "2.3" : "2.3"
  }
for arg in sys.argv[1:]:
  if "version" in arg and "mvapich2" in arg:
    mvapichSupportedVersions.append(arg.split("=")[1])
    mvapichTarballVersions[arg.split("=")[1]] = arg.split("=")[1]
    break

#
# Script code
#


from InstallProgramDriver import *
from GeneralScriptSupport import *


class MvapichInstall:

  def __init__(self):
    self.dummy = None

  #
  # Called before even knowing the product version
  #

  def getScriptName(self):
    return "install-mvapich.py"

  def getProductBaseName(self):
    return mvapichBaseName

  def getProductDefaultVersion(self):
    return mvapichDefaultVersion

  def getProductSupportedVersions(self):
    return mvapichSupportedVersions

  #
  # Called after knowing the product version but before parsing the
  # command-line.
  #

  def getURL(self, version):
    return mvapichBaseURL

  def getProductName(self, version):
    return mvapichBaseName+"-"+version

  def getBaseDirName(self, version):
    return mvapichBaseName+"-"+version+"-base"

  def getExtraHelpStr(self, version):
    return """
This script builds """+self.getProductName(version)+""" from source compiled
with the configured C/C++/Fortran compilers in your path or set by the env
vars CC, CXX, and FC.

NOTE: The assumed directory structure of the download source provided by the
command --download-cmnd=<download-cmnd> is:

   mvapich-<version>-base/
     mvapich-<version>.tar.gz
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
    self.mvapichBaseDir = self.baseDir+"/"+self.getBaseDirName(self.inOptions.version)
    mvapichVersionFull = mvapichTarballVersions[self.inOptions.version]
    self.mvapichTarball = "mvapich2-"+mvapichVersionFull+".tar.gz"
    self.mvapichSrcDir = "mvapich2-"+mvapichVersionFull
    self.mvapichBuildBaseDir = self.mvapichBaseDir+"/mvapich2-build"
    self.scriptBaseDir = getScriptBaseDir()

  #
  # Called after setup()
  #

  def doDownload(self):
    removeDirIfExists(self.mvapichBaseDir, True)
    echoRunSysCmnd(self.inOptions.downloadCmnd)

  def doUntar(self):
    # Find the full name of the source tarball
    echoChDir(self.mvapichBaseDir)
    echoRunSysCmnd("tar -xzf "+self.mvapichTarball)
    # NOTE: I found that you have to untar the tarball and can't store the
    # open source in the git repo.  Otherwise the timestaps are messed up and
    # it 'make' tries to recreate some generated files.

  def doConfigure(self):
    createDir(self.mvapichBuildBaseDir, True, True)
    echoRunSysCmnd(
      "../"+self.mvapichSrcDir+"/configure "+\
      " "+self.inOptions.extraConfigureOptions+\
      " --prefix="+self.inOptions.installDir,
      extraEnv={"CFLAGS":"-O3", "CXXFLAGS":"-O3", "FFLAGS":"-O3"},
      )

  def doBuild(self):
    echoChDir(self.mvapichBuildBaseDir)
    echoRunSysCmnd("make " + getParallelOpt(self.inOptions, "-j") \
      + self.inOptions.makeOptions)

  def doInstall(self):
    echoChDir(self.mvapichBuildBaseDir)
    echoRunSysCmnd("make " + getParallelOpt(self.inOptions, "-j") \
      + self.inOptions.makeOptions + " install")

  def getFinalInstructions(self):
    return """
To use the installed version of mvapich-"""+self.inOptions.version+""" add the path:

  """+self.inOptions.installDir+"""/bin

to your path and that should be it!

Also, when you link shared libs or executables, pass in:

   -Wl,-rpath,"""+self.inOptions.installDir+"""/lib[64]

That will make it so that you don't need to add this MPICH libs to your
LD_LIBRARY_PATH.
"""


#
# Executable statements
#

mvapichInstaller = InstallProgramDriver(MvapichInstall())
mvapichInstaller.runDriver()
