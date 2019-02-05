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
# Imports
#

from FindGeneralScriptSupport import *
import InstallProgramDriver
import os

#
# Defaults and constants
#

devtools_install_dir = os.path.dirname(os.path.abspath(__file__))

scratch_dir = os.getcwd()

sourceGitUrlBase_default = "https://github.com/tribitsdevtools/"

# tool default versions
autoconf_version_default = "2.69"
cmake_version_default    = "3.10.2"
git_version_default      = "2.6.4"
gcc_version_default      = "5.4.0"
mpich_version_default    = "3.2.1"
mvapich2_version_default = "2.3"
hdf5_version_default     = "1.10.1"
blas_version_default     = "3.3.1"
lapack_version_default   = "3.3.1"
hypre_version_default    = "2.9.1a"
petsc_version_default    = "3.6.3"
slepc_version_default    = "3.5.4"
sundials_version_default = "2.9.0"


# Common (compile independent) tools
commonToolsArray = [ "git", "gitdist", "autoconf", "cmake" ]
commonToolsChoices = (["all"] + commonToolsArray + [""])

# Compiler toolset
compilerToolsetArray = [ "gcc", "mpich", "mvapich2" ]
compilerToolsetChoices = (["all"] + compilerToolsetArray + [""])

# TPL toolset
TPLsetArray = [ "hdf5", "blas", "lapack", "hypre", "petsc", "slepc", "sundials" ]
TPLsetChoices = (["all"] + TPLsetArray + [""])

#
# Utility functions
#

usageHelp = r"""install-devtools.py [OPTIONS]

This script drives the installation of a number of tools needed by many
TriBITS-based projects.  The most typical usage is to first create a scratch
directory with::

  mkdir scratch
  cd scratch

and then run:

  install-devtools.py --install-dir=<dev_env_base> \
   --parallel=<num-procs> --do-all

By default, this installs the following tools in the dev env install
directory:

  <dev_env_base>/
    common_tools/
      autoconf-<autoconf-version>/
      cmake-<cmake-version>/
      gitdist
    gcc-<gcc-version>/
      load_dev_env.[sh,csh]
      toolset/
        gcc-<gcc-version>/
        mpich-<mpich-version>/

The default versions of the tools installed are:

* autoconf-"""+autoconf_version_default+"""
* cmake-"""+cmake_version_default+"""
* gcc-"""+gcc_version_default+"""
* mpich-"""+mpich_version_default+"""
* hdf5-"""+hdf5_version_default+"""
* blas-"""+blas_version_default+"""
* lapack-"""+lapack_version_default+"""
* hypre-"""+hypre_version_default+"""
* petsc-"""+petsc_version_default+"""
* slepc-"""+slepc_version_default+"""
* sundials-"""+sundials_version_default+"""

The tools installed under common_tools/ only need to be installed once
independent of any compilers that may be used to build TriBITS-based projects.

The tools installed under gcc-<gcc-version>/ are specific to a GCC compiler
and MPICH configuration and build.

The download and install of each of these tools is drive by its own
install-<toolname>.py script in the same directory as install-devtools.py.

Before running this script, some version of a C and C++ compiler must already
be installed on the system.

At a high level, this script performs the following actions.

1) Create the base directories (if they don't already exist) and install
   load_dev_env.sh (csh).  (if --initial-setup is passed in.)

2) Download the sources for all of the requested common tools and compiler
   toolset.  (if --download is passed in.)

3) Configure, build, and install the requested common tools under
   common_tools/. (if --install is passed in.)

4) Configure, build, and install the downloaded GCC and MPICH tools.  First
   install GCC then MPICH using the installed GCC and install under
   gcc-<gcc-version>/.  (if --install is passed in.)

The informational arguments to this function are:

  --install-dir=<dev_env_base>

    The base directory that will be used for the install.  There is not
    default.  If this is not specified then it will abort.

  --source-git-url-base=<url_base>

    Gives the base URL for to get the tool sources from.  The default is:

      """+sourceGitUrlBase_default+"""

    This is used to build the full git URL as:

      <url_base><tool_name>-<tool_version>-base

    This can also accomidate gitolite repos and other directory structures,
    for example, with:

      git@<host-name>:prerequisites/

  --common-tools=all

    Specifies the tools to download and install under common_tools/.  One can
    pick specific tools with:

      --common-tools=autoconf,cmake,...

    This will download and install the default versions of these tools.  To
    select specific versions, use:

      --common-tools=autoconf:"""+autoconf_version_default+""",cmake:"""+cmake_version_default+""",...

    The default is 'all'.  To install none of these, pass in empty:

      --common-tools=''

    (NOTE: A version of 'git' is *not* installed using this script but can be
    installed using the script install-git.py.  But note the extra packages
    that must be installed on a system in order to fully install git and its
    documentation.  All of the git-related TriBITS tools can use any recent
    version of git and most systems will already have a current-enough version
    of git so there is no need to install one to be effective doing
    development.)

  --compiler-toolset=all

    Specifies GCC and MPICH (and other compiler-specific tools) to download
    and install under gcc-<gcc-version>/toolset/.  One can pick specific
    componets with:

      --compiler-toolset=gcc,mpich

    or specific versions with:

      --compiler-toolset=gcc:"""+gcc_version_default+""",mpich:"""+mpich_version_default+"""

    Of course if one is only installing GCC with an existing installed MPICH,
    one will need to also reinstall MPICH as well.

    The default is 'all'.  To install none of these, pass in empty:

      --compiler-toolset=''

  --tpl-toolset=all

    Specifies HDF5, BLAS, LAPACK, HYPRE, PETSC, SLEPC, and SUNDIALS (and other
    TPL tools) to use in the load_dev_env.sh/.csh files.

      --tpl-toolset=hdf5,blas,lapack,hypre,petsc,slepc,sundials

    or specific versions with:

      --tpl-toolset=hdf5:"""+hdf5_version_default+""",blas:"""+blas_version_default+""",lapack:"""+lapack_version_default+""",hypre:"""+hypre_version_default+""",petsc:"""+petsc_version_default+""",slepc:"""+slepc_version_default+""",sundials:"""+sundials_version_default+"""

    The default is 'all'.  To install none of these, pass in empty:

      --tpl-toolset=''

The action argumnets are:

  --initial-setup: Create <dev_env_base>/ directories and install
    load_dev_env.sh

  --download: Download all of the requested tools

  --install: Configure, build, and install all of the requested tools

  --do-all: Do everything.  Implies --initial-setup --downlaod --install

To change modify the permissions of the installed files, see the options
--install-owner, --install-group, and --install-for-all.

Note that the user can see what operations and command would be run without
actually running them by passing in --no-op.  This can be used to show how to
run each of the individual install command so that the user can run it for
him/her-self and customize it as needed.

If the user needs more customization, then they can just run with --do-all
--no-op and see what commands are run to install things and then they can run
the commands themselves manually and make whatever modifications they need.

NOTE: The actual tool installs are performed using the scripts:

* install-autoconf.py
* install-cmake.py
* install-gcc.py
* install-git.py
* install-mpich.py
* install-mvapich2.py
* install-openmpi.py

More information about what versions are installed, how they are installed,
etc. is found in these scripts.  Note that some of these scripts apply patches
for certain versions.  For details, look at the --help output from these
scripts and look at the implementaion of these scripts.
"""


# Get and process command-line arguments
def getCmndLineOptions(cmndLineArgs, skipEchoCmndLine=False):

  from optparse import OptionParser

  clp = OptionParser(usage=usageHelp)
  clp.add_option(
    "--install-dir", dest="installDir", type="string", default="",
    help="The base directory <dev_env_base> that will be used for the install." \
      +"  There is not default.  If this is not specified then will abort.")

  InstallProgramDriver.insertInstallPermissionsOptions(clp)

  clp.add_option(
    "--source-git-url-base", dest="sourceGitUrlBase", type="string",
    default=sourceGitUrlBase_default,
    help="Gives the base URL <url_base> for the git repos to object the source from.")

  clp.add_option(
    "--common-tools", dest="commonTools", type="string", default="all",
    help="Specifies the common tools to download and install under common_tools/." \
      "  Can be 'all', or empty '', or any combination of" \
      " '"+(",".join(commonToolsArray))+"' (separated by commas, no spaces).")

  clp.add_option(
    "--compiler-toolset", dest="compilerToolset", type="string", default="all",
    help="Specifies GCC and MPICH and other compiler-specific tools to" \
      " download and install under gcc-<gcc-version>/toolset/." \
      "  Can be 'all', or empty '', or any combination of" \
      " '"+(",".join(compilerToolsetArray))+"' (separated by commas, no spaces).")

  clp.add_option(
    "--tpl-toolset", dest="TPLset", type="string", default="all",
    help="Specifies and other tpl-specific tools to" \
      " set in the load_dev_env scripts." \
      "  Can be 'all', or empty '', or any combination of" \
      " '"+(",".join(TPLsetArray))+"' (separated by commas, no spaces).")

  clp.add_option(
    "--parallel", dest="parallelLevel", type="string", default="1",
    help="Number of parallel processes to use in the build.  The default is" \
      " just '1'.  Use something like '8' to get faster parallel builds." )

  clp.add_option(
    "--do-op", dest="skipOp", action="store_false",
    help="Do all of the requested actions [default].")
  clp.add_option(
    "--no-op", dest="skipOp", action="store_true", default=False,
    help="Skip all of the requested actions and just print what would be done.")

  clp.add_option(
    "--show-defaults", dest="showDefaults", action="store_true", default=False,
    help="[ACTION] Show the defaults and exit." )

  clp.add_option(
    "--initial-setup", dest="doInitialSetup", action="store_true", default=False,
    help="[ACTION] Create base directories under <dev_env_base>/ and install" \
      " load_dev_env.[sh,csh].")

  clp.add_option(
    "--download", dest="doDownload", action="store_true", default=False,
    help="[ACTION] Download all of the tools specified by --common-tools" \
      " and --compiler-toolset.  WARNING:  If the source for a tool has" \
      " already been downloaded, it will be deleted (along with the build" \
      " directory) and downloaded from scratch!")

  clp.add_option(
    "--install", dest="doInstall", action="store_true", default=False,
    help="[ACTION] Configure, build, and install all of the tools specified by" \
      " --common-tools and --compiler-toolset.")

  clp.add_option(
    "--install-tpls", dest="doInstallTPLs", action="store_true", default=False,
    help="[ACTION] Configure, build, and install all of the TPLs specified by" \
      " --tpl-set.")

  clp.add_option(
    "--show-final-instructions", dest="showFinalInstructions", action="store_true",
    default=False,
    help="[ACTION] Show final instructions for using the installed dev env." )

  clp.add_option("-b", "--build-image", action="store_true", dest="build_image", default=False, help="Enable to build a docker image from the configured docker file. Default is false")

  clp.add_option(
    "--gcc-version",dest="gcc_ver",type="string",default=gcc_version_default,
    help="Set the gcc version default is "+gcc_version_default+".")

  clp.add_option(
    "--do-all", dest="doAll", action="store_true", default=False,
    help="[AGGR ACTION] Do everything.  Implies --initial-setup --downlaod" \
      +" --install --show-final-instructions")

  (options, args) = clp.parse_args(args=cmndLineArgs)

  # NOTE: Above, in the pairs of boolean options, the *last* add_option(...)
  # takes effect!  That is why the commands are ordered the way they are!

  #
  # Echo the command-line
  #

  if not skipEchoCmndLine:

    cmndLine = "**************************************************************************\n"
    cmndLine +=  "Script: install-devtools.py \\\n"
    cmndLine +=  "  --install-dir='"+options.installDir+"' \\\n"
    cmndLine += InstallProgramDriver.echoInsertPermissionsOptions(options)
    cmndLine +=  "  --source-git-url-base='"+options.sourceGitUrlBase+"' \\\n"
    cmndLine +=  "  --common-tools='"+options.commonTools+"' \\\n"
    cmndLine +=  "  --compiler-toolset='"+options.compilerToolset+"' \\\n"
    cmndLine +=  "  --tpl-set='"+options.TPLset+"' \\\n"
    cmndLine +=  "  --build-image='"+str(options.build_image)+"' \\\n"
    cmndLine +=  "  --parallel='"+options.parallelLevel+"' \\\n"
    if not options.skipOp:
      cmndLine +=  "  --do-op \\\n"
    else:
      cmndLine +=  "  --no-op \\\n"
    if options.doInitialSetup:
      cmndLine +=  "  --initial-setup \\\n"
    if options.doDownload:
      cmndLine +=  "  --download \\\n"
    if options.doInstall:
      cmndLine +=  "  --install \\\n"
    if options.doInstallTPLs:
      cmndLine +=  "  --install-tpls \\\n"
    if options.showFinalInstructions:
      cmndLine +=  "  --show-final-instructions \\\n"
    if options.doAll:
      cmndLine +=  "  --do-all \\\n"

    print(cmndLine)

    if options.showDefaults:
      sys.exit(0);

  #
  # Check the input arguments
  #

  if options.installDir == "":
    print("\nError, you must set --install-dir=<dev_env_base>!")
    raise Exception("Bad input option --install-dir")
  options.installDir = os.path.abspath(os.path.expanduser(options.installDir))

  if options.commonTools == "all":
    options.commonTools = ",".join(commonToolsArray)
  #print("options.commonTools = '"+options.commonTools+"'")

  if options.compilerToolset == "all":
    options.compilerToolset = ",".join(compilerToolsetArray)
    options.compilerToolset = options.compilerToolset.replace(",mvapich2","")

  if options.TPLset == "all":
    options.TPLset = ",".join(TPLsetArray)
  #print("options.TPLset = '"+options.TPLset+"'")

  if options.doAll:
    options.doInitialSetup = True
    options.doDownload = True
    options.doInstall = True
    options.doInstallTPLs = True
    options.doModules = True
    options.showFinalInstructions = True

  #
  # Return the options
  #

  return options

#
# Check Script Pre-requisites
#
def checkPreReqTools():
  if os.isfile("/usr/bin/which"):
    echoRunSysCmnd("which chmod")
    echoRunSysCmnd("which chown")
    echoRunSysCmnd("which chgrp")
    echoRunSysCmnd("which mkdir")
    echoRunSysCmnd("which rm")
    echoRunSysCmnd("which cp")
    echoRunSysCmnd("which tar")
    echoRunSysCmnd("which wget")
  else:
    raise EnvironmentError("/usr/bin/which does not exist! Cannot check for prequisite system software!")

#
# Get array of selected tools (can be empty)
#
def getToolsSelectedArray(toolsSelectedStr, validToolsArray):
  validToolsArraySet = set(validToolsArray)
  if toolsSelectedStr == "":
    return []
  toolsArray = []
  for toolName in toolsSelectedStr.split(","):
    if not toolName.split(':')[0] in validToolsArraySet:
      raise Exception("Error, '"+toolName+"' is not one of" \
        " '"+(",".join(validToolsArray))+"'")
    toolsArray.append(toolName.split(':')[0])
  return toolsArray


#
# Do substututions in a string given replacements
#
def substituteStrings(inputStr, subPairArray):
  outputStr = ""
  inputStrArray = inputStr.splitlines()
  if inputStrArray[-1] == "": inputStrArray = inputStrArray[0:-1]
  for line in inputStrArray:
    #print("line = '"+line+"'")
    for (str1, str2) in subPairArray:
      #print("(str1, str2) =", (str1, str2))
      line = line.replace(str1, str2)
    outputStr += (line + "\n")
  return outputStr


#
# Configure a file by substituting strings
#
def configureFile(fileInPath, subPairArray, fileOutPath):
  fileInStr = open(fileInPath, 'r').read()
  fileOutStr = substituteStrings(fileInStr, subPairArray)
  open(fileOutPath, 'w').write(fileOutStr)

#
# Assert an install directory exists
#
def assertInstallDirExists(dirPath, inOptions):
  if not os.path.exists(dirPath) and not inOptions.skipOp:
    raise Exception(
      "Error, the install directory '"+dirPath+"'" \
       " does not exist!")


#
# Write the files load_dev_env.[sh,csh]
#
def writeLoadDevEnvFiles(devEnvBaseDir, devEnvDir, inOptions, versionList, mvapich2Installed):

  subPairArray = [
    ("@DEV_ENV_BASE@", devEnvBaseDir),
    ("@CMAKE_VERSION@", versionList["cmake"]),
    ("@AUTOCONF_VERSION@", versionList["autoconf"]),
    ("@GCC_VERSION@", versionList["gcc"]),
    ("@HDF5_VERSION@", versionList["hdf5"]),
    ("@BLAS_VERSION@", versionList["blas"]),
    ("@LAPACK_VERSION@", versionList["lapack"]),
    ("@HYPRE_VERSION@", versionList["hypre"]),
    ("@PETSC_VERSION@", versionList["petsc"]),
    ("@SLEPC_VERSION@", versionList["slepc"]),
    ("@SUNDIALS_VERSION@", versionList["sundials"])]
  if mvapich2Installed:
    subPairArray.append(("@MVAPICH_VERSION@", versionList["mvapich2"]))
  else:
    subPairArray.append(("@MPICH_VERSION@", versionList["mpich"])),


  load_dev_env_base = inOptions.loadDevEnvFileBaseName

  configureFile(
    os.path.join(devtools_install_dir, "load_dev_env.sh.in"),
    subPairArray,
    os.path.join(devEnvDir, load_dev_env_base+".sh")
    )

  configureFile(
    os.path.join(devtools_install_dir, "load_dev_env.csh.in"),
    subPairArray,
    os.path.join(devEnvDir, load_dev_env_base+".csh")
    )
  modulePathPairArray =[("@DEV_ENV_DIR@", devEnvDir)]
  configureFile(
    os.path.join(devtools_install_dir, "append_modulepath.sh.in"),
    modulePathPairArray,
    os.path.join(devEnvDir, "append_modulepath.sh")
    )


#
# Download the source for tool
#
def downloadToolSource(toolName, toolVer, inOptions):

  toolDir = toolName+"-"+toolVer
  toolTarball = toolDir+".tar.gz"

  print("\nDownloading the source for " + toolDir + " ...")

  outFile = toolDir+"-download.log"
  workingDir=scratch_dir

  cmnd = devtools_install_dir+"/install-"+toolName+".py" \
    +" --"+toolName+"-version="+toolVer \
    +" --download"
  if not inOptions.skipOp:
    echoRunSysCmnd(cmnd, workingDir=workingDir, outFile=outFile, timeCmnd=True)
  else:
    print("\nRunning: " + cmnd)
    print("\n  Running in working directory: " + workingDir)
    print("\n   Writing console output to file " + outFile)


#
# Install downloaded tool from source
#
def installToolFromSource(toolName, toolVer, installBaseDir,
  extraEnv, extraConfig, inOptions \
  ):

  toolDir = toolName+"-"+toolVer

  print("\nInstalling " + toolDir + " ...")

  outFile = toolDir+"-install.log"
  workingDir=scratch_dir
  toolInstallDir = installBaseDir+"/"+toolDir

  cmnd = devtools_install_dir+"/install-"+toolName+".py" \
    +" --"+toolName+"-version="+toolVer \
    +" --untar --configure --build --install --show-final-instructions" \
    +" --parallel="+inOptions.parallelLevel \
    +" --install-dir="+toolInstallDir \
    +" --install-owner="+inOptions.installOwner \
    +" --install-group="+inOptions.installGroup
  if inOptions.installForAll:
    cmnd += "  --install-for-all"
  if extraConfig:
    cmnd += "  --extra-configure-options="+extraConfig
  print("Executing command: " + cmnd)
  if not inOptions.skipOp:
    echoRunSysCmnd(cmnd, workingDir=workingDir, outFile=outFile, timeCmnd=True,
      extraEnv=extraEnv)
  else:
    print("\nRunning: " + cmnd)
    print("\n  Running in working directory: " + workingDir)
    print("\n  Appending environment: " + str(extraEnv))
    print("\n  Writing console output to file " + outFile)
  print("Completed installing " + toolDir + " ...")

#
# Generate Environment Modulefile for tool
#
def generateModuleFile(toolName, toolVer, moduleBaseDir, depModules, inOptions):

  toolDir = toolName+"-"+toolVer

  print("\nGenerating Modulefile for " + toolDir + " ...")

  outFile = toolDir+"-module.log"
  workingDir=scratch_dir

  cmnd =  devtools_install_dir+"/install-"+toolName+".py" \
    +" --"+toolName+"-version="+toolVer \
    +" --generate-env-module" \
    +" --module-dir="+moduleBaseDir \
    +" --install-owner="+inOptions.installOwner \
    +" --install-group="+inOptions.installGroup
  if depModules:
    cmnd += " --dependent-env-modules="+depModules

  print("Executing command: " + cmnd)
  if not inOptions.skipOp:
    echoRunSysCmnd(cmnd, workingDir=workingDir, outFile=outFile, timeCmnd=True,
      extraEnv=None)
  else:
    print("\nRunning: " + cmnd)
    print("\n  Writing console output to file " + outFile)
  print("Completed writing module file for " + toolDir + " ...")


#
# Main
#

def main(cmndLineArgs):

  #
  # Get the command-line options
  #

  inOptions = getCmndLineOptions(cmndLineArgs)

  if inOptions.skipOp:
    print("\n***")
    print("*** NOTE: --no-op provided, will only trace actions and not touch the filesystem!")
    print("***\n")

  commonToolsSelected = \
    getToolsSelectedArray(inOptions.commonTools, commonToolsArray)
  print("\nSelected common tools = " + str(commonToolsSelected))
  commonToolsSelectedSet = set(commonToolsSelected)

  compilerToolsetSelected = \
    getToolsSelectedArray(inOptions.compilerToolset, compilerToolsetArray)
  if all(mpi in compilerToolsetSelected for mpi in ["mvapich2","mpich"]):
    print("\n\n***")
    print("*** NOTE: mvapich2 and mpich are specified. IGNORING MVAPICH!")
    print("***")
    compilerToolsetSelected.remove("mvapich2")
  print("\nSelected compiler toolset = " + str(compilerToolsetSelected))
  compilerToolsetSelectedSet = set(compilerToolsetSelected)

  TPLsetSelected = \
    getToolsSelectedArray(inOptions.TPLset, TPLsetArray)
  print("\nSelected TPLs  = " + str(TPLsetSelected))
  TPLsetSelectedSet = set(TPLsetSelected)

  dev_env_base_dir = inOptions.installDir

  ###
  print("\n\nB) Setup the install directory <dev_env_base> ='" +
        dev_env_base_dir + "':\n")
  ###

  dev_env_base_exists = os.path.exists(dev_env_base_dir)

  common_tools_dir = os.path.join(dev_env_base_dir, "common_tools")
  common_tools_exists = os.path.exists(common_tools_dir)

  compiler_toolset_base_dir = os.path.join(dev_env_base_dir, "gcc-"+inOptions.gcc_ver)
  compiler_toolset_base_exists = os.path.exists(compiler_toolset_base_dir)

  compiler_toolset_dir = os.path.join(compiler_toolset_base_dir, "toolset")
  compiler_toolset_exists = os.path.exists(compiler_toolset_dir)

  dev_env_dir = os.path.join(dev_env_base_dir, "env")
  dev_env_exists = os.path.exists(dev_env_dir)

  if inOptions.doInitialSetup:

    if not dev_env_base_exists:
      print("Creating directory '" + dev_env_base_dir + "' ...")
      if not inOptions.skipOp:
        os.makedirs(dev_env_base_dir)

    if not common_tools_exists:
      print("Creating directory '" + common_tools_dir + "' ...")
      if not inOptions.skipOp:
        os.makedirs(common_tools_dir)

    if not compiler_toolset_base_exists:
      print("Creating directory '" + compiler_toolset_base_dir + "' ...")
      if not inOptions.skipOp:
        os.makedirs(compiler_toolset_base_dir)

    if not compiler_toolset_exists:
      print("Creating directory '" + compiler_toolset_dir + "' ...")
      if not inOptions.skipOp:
        os.makedirs(compiler_toolset_dir)

    #TODO: Add image dirs

  else:
    print("Skipping setup of the install directory by request!")
    assertInstallDirExists(dev_env_base_dir, inOptions)
    assertInstallDirExists(common_tools_dir, inOptions)
    assertInstallDirExists(compiler_toolset_base_dir, inOptions)
    assertInstallDirExists(compiler_toolset_dir, inOptions)


  ###
  print("\n\nC) Download all sources for each selected tool:\n")
  ###
  if inOptions.doDownload:

    if "cmake" in commonToolsSelectedSet:
      downloadToolSource("cmake", cmake_version_default,
        inOptions)

    if "autoconf" in commonToolsSelectedSet:
      downloadToolSource("autoconf", autoconf_version_default,
        inOptions)

    if "git" in commonToolsSelectedSet:
      downloadToolSource("git", git_version_default,
        inOptions)

    if "gcc" in compilerToolsetSelectedSet:
      downloadToolSource("gcc", gcc_version_default,
        inOptions)

    if "mpich" in compilerToolsetSelectedSet:
      downloadToolSource("mpich", mpich_version_default,
        inOptions)
    elif "mvapich2" in compilerToolsetSelectedSet:
      downloadToolSource("mvapich2", mvapich2_version_default,
        inOptions)

  else:

    print("Skipping download of the source for the tools on request!")
    if inOptions.doInstall:
      print("NOTE: The downloads had better be there for the install!")

  ###
  print("\n\nD) Untar, configure, build and install each selected tool:\n")
  ###
  if inOptions.doInstall:

    if "gitdist" in commonToolsSelectedSet:
      print("\nInstalling gitdist ...")
      cmnd="cp "+pythonUtilsDir+"/gitdist "+common_tools_dir+"/"
      if not inOptions.skipOp:
        echoRunSysCmnd(cmnd)
        InstallProgramDriver.fixupInstallPermissions(inOptions, common_tools_dir)
      else:
        print("\nRunning: " + cmnd)

    if "cmake" in commonToolsSelectedSet:
      installToolFromSource("cmake", cmake_version_default,
        common_tools_dir, None, None, inOptions )

    if "autoconf" in commonToolsSelectedSet:
      installToolFromSource("autoconf", autoconf_version_default,
        common_tools_dir, None, None, inOptions )

    if "git" in commonToolsSelectedSet:
      installToolFromSource("git", git_version_default,
        common_tools_dir, None, None, inOptions )

    if "gcc" in compilerToolsetSelectedSet:
      installToolFromSource("gcc", gcc_version_default,
        compiler_toolset_dir, None, None, inOptions )

    if any(mpi in compilerToolsetSelectedSet for mpi in ["mpich","mvapich2"]):

      # Try script installed GCC first
      gccInstallDir = compiler_toolset_dir+"/gcc-"+gcc_version_default
      if not os.path.exists(gccInstallDir) and not inOptions.skipOp:
        #Check if environment gcc matches version
        gcc_ver = os.popen("gcc --version").read()
        gcc_ver = gcc_ver.split("\n")[0]
        gcc_ver = gcc_ver.split(" ")[2]
        if not gcc_ver == gcc_version_default:
          raise Exception("Error, gcc has not been installed yet." \
            "  Missing directory '"+gccInstallDir+"'")
        else:
          gccInstallDir = os.popen("which gcc").read()
          gccInstallDir = gccInstallDir.replace("/bin/gcc\n","")
          print("\n***")
          print("*** NOTE: Using system provided gcc at "+gccInstallDir)
          print("***\n")

      LD_LIBRARY_PATH = os.environ.get("LD_LIBRARY_PATH", "")

      if "mpich" in compilerToolsetSelectedSet:
        installToolFromSource(
          "mpich",
          mpich_version_default,
          compiler_toolset_dir,
          {
            "CC" : gccInstallDir+"/bin/gcc",
            "CXX" : gccInstallDir+"/bin/g++",
            "FC" : gccInstallDir+"/bin/gfortran",
            "LD_LIBRARY_PATH" : gccInstallDir+"/lib64:"+LD_LIBRARY_PATH
          },
          None,
          inOptions
        )
      elif "mvapich2" in compilerToolsetSelectedSet:
        installToolFromSource(
          "mvapich2",
          mvapich2_version_default,
          compiler_toolset_dir,
          {
            "CC" : gccInstallDir+"/bin/gcc",
            "CXX" : gccInstallDir+"/bin/g++",
            "FC" : gccInstallDir+"/bin/gfortran",
            "LD_LIBRARY_PATH" : gccInstallDir+"/lib64:"+LD_LIBRARY_PATH
          },
          None,
          inOptions
        )
  else:
    print("Skipping install of the tools on request!")

  ###
  print("\n\nE) Install TPLs:")
  ###
  if inOptions.doInstallTPLs:
    #TODO: Add this
    print("WIP!")
  else:
    print("Skipping install of the TPLs on request!")

  ###
  print("\n\nF) Setting up environment modules:\n")
  ###
  if inOptions.doModules:
    print("WIP!")

    if "cmake" in commonToolsSelectedSet:
      generateModuleFile("cmake", cmake_version_default,
        dev_env_dir, None, inOptions )

    if "autoconf" in commonToolsSelectedSet:
      generateModuleFile("autoconf", autoconf_version_default,
        dev_env_dir, None, inOptions )

    if "gcc" in compilerToolsetSelectedSet:
      generateModuleFile("gcc", gcc_version_default,
        dev_env_dir, None, inOptions )

    if "mpich" in compilerToolsetSelectedSet:
      generateModuleFile("mpich", mpich_version_default,
        dev_env_dir, "gcc-"+gcc_version_default, inOptions )
    elif "mvapich2" in compilerToolsetSelectedSet:
      generateModuleFile("mvapich2", mvapich2_version_default,
        dev_env_dir, "gcc-"+gcc_version_default, inOptions )

    #Write master PrgEnv file
    #TODO: Make this file correct
    if not inOptions.skipOp:
      createDir(dev_env_dir + "/PrgEnv/mpact-dev/", False, False)
      prgenv_module = open(dev_env_dir + "/PrgEnv/mpact-dev/gcc-"+inOptions.gcc_ver, "w+")
      prgenv_module.write("#%Module\n\n")
      prgenv_module.write("set root " + dev_env_base_dir + "\n")
      prgenv_module.write("set version gcc-" + gcc_version + "\n")
      prgenv_module.write("set tpldir " + compiler_toolset_base_dir + "/tpls\n")
      prgenv_module.write('set name "MPACT Development Environment - $version"\n')
      prgenv_module.write('set msg "Loads the development environment for MPACT."\n')
      prgenv_module.write('proc ModulesHelp { } {\n')
      prgenv_module.write(" puts stderr $msg }\n")
      prgenv_module.write("module-whatis $msg\n")
      if not mvapichInstalled:
        prgenv_module.write("if ![ is-loaded 'mpi/mpich-" + mpich_version + "-x86_64' ] {\n")
        prgenv_module.write(" module load mpi/mpich-" + mpich_version + "-x86_64 }\n")
      else:
        prgenv_module.write("if ![ is-loaded 'mpi/mvapich-" + mvapich_version + "-x86_64' ] {\n")
        prgenv_module.write(" module load mpi/mvapich-" + mvapich_version + "-x86_64 }\n")
      prgenv_module.write("setenv TRIBITS_DEV_ENV_BASE          $root\n")
      prgenv_module.write("setenv TRIBITS_DEV_ENV_GCC_VERSION   $version\n")
      prgenv_module.write("setenv TRIBITS_DEV_ENV_COMPILER_BASE $root/$version\n")
      prgenv_module.write("setenv TRIBITS_DEV_ENV_MPICH_DIR     $env(MPI_HOME)\n")
      prgenv_module.write("setenv LOADED_TRIBITS_DEV_ENV        $version\n")
      prgenv_module.write("setenv LOADED_VERA_DEV_ENV        $version\n")
      prgenv_module.write("prepend-path PATH $root/common_tools\n")
      prgenv_module.write("set tplpath $tpldir/hdf5-1.8.10\n")
      prgenv_module.write("setenv HDF5_ROOT             $tplpath\n")
      prgenv_module.write("prepend-path PATH            $tplpath/bin\n")
      prgenv_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
      prgenv_module.write("prepend-path INCLUDE         $tplpath/include\n")
      prgenv_module.write("set tplpath $tpldir/lapack-3.3.1\n")
      prgenv_module.write("setenv BLAS_ROOT             $tplpath\n")
      prgenv_module.write("setenv LAPACK_DIR            $tplpath\n")
      prgenv_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
      prgenv_module.write("set tplpath $tpldir/hypre-2.9.1a\n")
      prgenv_module.write("setenv HYPRE_DIR             $tplpath\n")
      prgenv_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
      prgenv_module.write("set tplpath $tpldir/petsc-3.5.4\n")
      prgenv_module.write("setenv PETSC_DIR             $tplpath\n")
      prgenv_module.write("prepend-path PATH            $tplpath/bin\n")
      prgenv_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
      prgenv_module.write("set tplpath $tpldir/slepc-3.5.4\n")
      prgenv_module.write("setenv SLEPC_DIR             $tplpath\n")
      prgenv_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
      prgenv_module.write("set tplpath $tpldir/sundials-2.9.0\n")
      prgenv_module.write("setenv SUNDIALS_DIR          $tplpath\n")
      prgenv_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
      prgenv_module.write("set-alias gitdist-status     {gitdist dist-repo-status}\n")
      prgenv_module.write("set-alias gitdist-mod        {gitdist --dist-mod-only}\n")
      prgenv_module.close()

  else:
    print("Skipping writing environment module files on request!")

  ###
  print("\n\nG) Final instructions for using installed dev env:\n")
  ###

  if inOptions.skipOp:
    print("\n***")
    print("*** NOTE: --no-op provided, only traced actions that would have been taken!")
    print("***")

    #TODO: Add final instructions
#
#  print("installing CMake target for vera_tpls")
#  if not inOptions.skipOp and inOptions.doInstall:
#    os.system("mkdir " + compiler_toolset_base_dir + "/tpls")
#    os.chdir(scratch_dir + "/..")
#    os.system("git submodule init && git submodule update")
#    if not os.path.exists(scratch_dir + "/tmp"):
#      os.mkdir(scratch_dir + "/tmp")
#    os.chdir(scratch_dir + "/tmp")
#    os.system("rm -rf *")
#    #os.system("module load mpi")
#    if 'HDF5_ROOT' in os.environ:
#      del os.environ['HDF5_ROOT']
#    if 'BLAS_ROOT' in os.environ:
#      del os.environ['BLAS_ROOT']
#    if 'LAPACK_DIR' in os.environ:
#      del os.environ['LAPACK_DIR']
#    if 'HYPRE_DIR' in os.environ:
#      del os.environ['HYPRE_DIR']
#    if 'PETSC_DIR' in os.environ:
#      del os.environ['PETSC_DIR']
#    if 'SLEPC_DIR' in os.environ:
#      del os.environ['SLEPC_DIR']
#    if 'SUNDIALS_DIR' in os.environ:
#      del os.environ['SUNDIALS_DIR']
#
#    #mpicc_path = compiler_toolset_dir + "/mpich-"+ mpich_version + "/bin/mpicc"
#    #mpicxx_path = compiler_toolset_dir + "/mpich-"+ mpich_version + "/bin/mpicxx"
#    #mpif90_path = compiler_toolset_dir + "/mpich-"+ mpich_version + "/bin/mpif90"
#
#    # Now do the Python equivalent of loading the mpi module
#    os.environ['PATH'] = compiler_toolset_dir + "/mpich-" + mpich_version + "/bin" + os.pathsep + os.environ['PATH']
#
#    if 'LD_LIBRARY_PATH' in os.environ:
#      os.environ['LD_LIBRARY_PATH'] = compiler_toolset_dir + "/mpich-" + mpich_version + "/lib" + os.pathsep + os.environ['LD_LIBRARY_PATH']
#    else:
#      os.environ['LD_LIBRARY_PATH'] = compiler_toolset_dir + "/mpich-" + mpich_version + "/lib"
#
#    if 'PKG_CONFIG_PATH' in os.environ:
#      os.environ['PKG_CONFIG_PATH'] = compiler_toolset_dir + "/mpich-" + mpich_version + "/lib/pkgconfig" + os.pathsep + os.environ['PKG_CONFIG_PATH']
#    else:
#      os.environ['PKG_CONFIG_PATH'] = compiler_toolset_dir + "/mpich-" + mpich_version + "/lib/pkgconfig"
#
#    os.environ['MPI_BIN'] = compiler_toolset_dir + "/mpich-" + mpich_version + "/bin"
#    os.environ['MPI_INCLUDE'] = compiler_toolset_dir + "/mpich-" + mpich_version + "/include"
#    os.environ['MPI_LIB'] = compiler_toolset_dir + "/mpich-" + mpich_version + "/lib"
#    os.environ['MPI_COMPILER'] = "mpiexec"
#    os.environ['MPI_SUFFIX'] = "_mpich"
#    os.environ['MPI_HOME'] = compiler_toolset_dir + "/mpich-" + mpich_version
#
#
#  else:
#  if not inOptions.skipOp:
#    if inOptions.build_image:
#      print("building docker image")
#      os.system("docker build -t test-mpact-dev-env " + dev_env_base_dir + "/images")
#  if inOptions.showFinalInstructions:
#    print("\nTo use the new dev env, just source the file:\n")
#    print("  source " + dev_env_base_dir + "/env/load_dev_env.sh\n")
#    print("for sh or bash shells (or load_dev_env.csh for csh shell).\n")
#    print("TIP: Add this source to your ~/.bash_profile!")
  else:
    print("Skipping Final instructions on request ...")

  print("\n[End]")

#
# Script driver
#
if __name__ == '__main__':
  try:
    sys.exit(main(sys.argv[1:]))
  except Exception as e:
    print(e)
    print()
    printStackTrace()
    sys.exit(1)
