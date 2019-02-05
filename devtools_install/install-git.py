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

gitBaseName = "git"
gitBaseURL  = "https://github.com/git/git/archive/"
gitDefaultVersion = "2.6.4"
gitSupportedVersions = ["2.6.4"]
gitTarballVersions = {
  "2.6.4" : "2.6.4",
  }


#
# Script code
#


from InstallProgramDriver import *
from GeneralScriptSupport import *


class GitInstall:

  def __init__(self):
    self.dummy = None

  #
  # Called before even knowing the product version
  #

  def getScriptName(self):
    return "install-git.py"

  def getProductBaseName(self):
    return gitBaseName

  def getProductDefaultVersion(self):
    return gitDefaultVersion

  def getProductSupportedVersions(self):
    return gitSupportedVersions

  #
  # Called after knowing the product version but before parsing the
  # command-line.
  #

  def getURL(self, version):
    return gitBaseURL

  def getProductName(self, version):
    return gitBaseName+"-"+version

  def getBaseDirName(self, version):
    return gitBaseName+"-"+version+"-base"

  def getExtraHelpStr(self, version):
    return """
This script builds """+self.getProductName(version)+""" from source compiled with the
configured C compiler in your path.   This also installs the git-subtree provided in the
contributed folder on install.

To also build and install the documentaion, additionally, pass in:

  --with-doc --with-info

(but note the extra packages that must be installed on the system).

For more details on installing from source and required system dependencies
before attempting this build, see:

  https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

In particular, to build everything you will need to install the documentation
(--with-doc and --with-info), you will need to install the packages
'asciidoc', 'xmlto', and 'docbook2X'.  Again, see the above webpage for
details (it is not 100% pretty).

NOTE: The assumed directory structure of the download source provided by the
command --download-cmnd=<download-cmnd> is:

   git-<version>-base/
     git-<full-version>.tar.gz
"""

  def setDownloadCmndOption(self, clp, version):
    url = self.getURL(version)
    productName = self.getProductBaseName()+"-"+version
    productBaseDirName = productName+"-base"
    productTarball = "v"+version+".tar.gz"

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
    clp.add_option(
      "--with-doc", dest="withDoc", action="store_true", default=False,
      help="Build and install manpage documentation (requires asciidoc and xmlto)." )
    clp.add_option(
      "--with-info", dest="withInfo", action="store_true", default=False,
      help="Build and install info documentation (requires docbook2x)." )

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
    self.gitBaseDir = self.baseDir+"/"+self.getBaseDirName(self.inOptions.version)
    gitVersionFull = gitTarballVersions[self.inOptions.version]
    self.gitTarball = "v"+gitVersionFull+".tar.gz"
    self.gitSrcDir = "git-"+gitVersionFull
    self.gitSrcBuildDir = self.gitBaseDir+"/"+self.gitSrcDir
    self.gitSubtreeSrcBuildDir = self.gitSrcBuildDir+"/contrib/subtree"
    self.scriptBaseDir = getScriptBaseDir()

  #
  # Called after setup()
  #

  def doDownload(self):
    removeDirIfExists(self.gitBaseDir, True)
    echoRunSysCmnd(self.inOptions.downloadCmnd)

  def doUntar(self):
    # Find the full name of the source tarball
    echoChDir(self.gitBaseDir)
    echoRunSysCmnd("tar -xzf "+self.gitTarball)

  def doConfigure(self):
    echoChDir(self.gitSrcBuildDir)
    echoRunSysCmnd("make configure")
    echoRunSysCmnd(
      "./configure "+\
      " "+self.inOptions.extraConfigureOptions+\
      " --prefix="+self.inOptions.installDir
      )
    # NOTE: Git appears to only allow an in-source build :-(

  def doBuild(self):
    echoChDir(self.gitSrcBuildDir)
    echoRunSysCmnd("make "+getParallelOpt(self.inOptions, "-j")+\
      self.inOptions.makeOptions+" all")
    if self.inOptions.withDoc:
      echoRunSysCmnd("make "+getParallelOpt(self.inOptions, "-j")+\
        self.inOptions.makeOptions+" doc")
    if self.inOptions.withInfo:
      echoRunSysCmnd("make "+getParallelOpt(self.inOptions, "-j")+\
        self.inOptions.makeOptions+" info")
    # Build git-subtree to get ready to install
    echoChDir(self.gitSubtreeSrcBuildDir)


  def doInstall(self):
    echoChDir(self.gitSrcBuildDir)
    echoRunSysCmnd("make "+self.inOptions.makeOptions+" install")
    if self.inOptions.withDoc:
      echoRunSysCmnd("make "+self.inOptions.makeOptions+" install-doc")
      echoRunSysCmnd("make "+self.inOptions.makeOptions+" install-html")
    if self.inOptions.withInfo:
      echoRunSysCmnd("make "+self.inOptions.makeOptions+" install-info")
    # Install git-subtree and documentation
    echoChDir(self.gitSubtreeSrcBuildDir)
    echoRunSysCmnd("make "+self.inOptions.makeOptions+" install")
    if self.inOptions.withDoc:
      echoRunSysCmnd("make "+self.inOptions.makeOptions+" install-doc")

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

    #Standard help
    module_file.write("proc ModulesHelp { } {\n")
    module_file.write("    puts stderr \" Loads $name-$version as a part of the MPACT development environment.\"\n" + \
      "}\n\n")

    #More info
    module_file.write("module-whatis \"" + \
      "Git is a free and open source distributed version control system designed " + \
      "to handle everything from small to very large projects with speed and efficiency." + \
      "\"\n")
    module_file.write("module-whatis \"Vendor Website: https://git-scm.com/\"\n")
    module_file.write("module-whatis \"        Manual: https://git-scm.com/docs\"\n")

    module_file.close()

  def getFinalInstructions(self):
    return """
    To use the installed version of """+self.getProductBaseName()+"""-"""+ \
      self.inOptions.version+""" with environment modules
    modify your MODULEPATH environment variable from the command line with:

    $ export MODULEPATH="""+self.inOptions.moduleDir+""":$MODULEPATH

    Or modify your .bashrc (or other login script) and that should be it!"""


#
# Executable statements
#

gitInstaller = InstallProgramDriver(GitInstall())
gitInstaller.runDriver()
