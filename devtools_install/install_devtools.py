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
cmake_version_default = "3.3.2"
gcc_version_default = "4.8.3"
mpich_version_default = "3.1.3"
mvapich_version_default = "2.3"

# Common (compile independent) tools
commonToolsArray = [ "gitdist", "autoconf", "cmake" ]
commonToolsChoices = (["all"] + commonToolsArray + [""])

# Compiler toolset
compilerToolsetArray = [ "gcc", "mpich", "mvapich" ]
compilerToolsetChoices = (["all"] + compilerToolsetArray + [""])


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
    "--load-dev-env-file-base-name", dest="loadDevEnvFileBaseName",
    type="string", default="load_dev_env",
    help="Base name of the load dev env script that will be installed." \
      "  (Default = 'load_dev_env')" )

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
    "--show-final-instructions", dest="showFinalInstructions", action="store_true",
    default=False,
    help="[ACTION] Show final instructions for using the installed dev env." )

  clp.add_option("-m", "--mkl", action="store_true", dest="mkl_true", default=False, help="Enable to install tpls with intel-mkl rather than blas-lapack. Default is vera tpls")

  clp.add_option("-b", "--build-image", action="store_true", dest="build_image", default=False, help="Enable to build a docker image from the configured docker file. Default is false")

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
    cmndLine +=  "  --load-dev-env-file-base-name='"+options.loadDevEnvFileBaseName+"' \\\n"
    cmndLine +=  "  --common-tools='"+options.commonTools+"' \\\n"
    cmndLine +=  "  --compiler-toolset='"+options.compilerToolset+"' \\\n"
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
  #print("options.compilerToolset = '"+options.compilerToolset+"'")

  if options.doAll:
    options.doInitialSetup = True
    options.doDownload = True
    options.doInstall = True
    options.showFinalInstructions = True

  #
  # Return the options
  #

  return options


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
def writeLoadDevEnvFiles(devEnvBaseDir, devEnvDir, inOptions, versionList, mvapichInstalled):

  subPairArray = [
    ("@DEV_ENV_BASE@", devEnvBaseDir),
    ("@CMAKE_VERSION@", versionList["cmake"]),
    ("@AUTOCONF_VERSION@", versionList["autoconf"]),
    ("@GCC_VERSION@", versionList["gcc"])]
  if mvapichInstalled:
    subPairArray.append(("@MVAPICH_VERSION@", versionList["mvapich"]))
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


#
# Download the source for tool
#
def downloadToolSource(toolName, toolVer, gitUrlBase, inOptions):

  toolDir = toolName+"-"+toolVer

  print("\nDownloading the source for " + toolDir + " ...")

  outFile = toolDir+"-download.log"
  workingDir=scratch_dir
  toolSrcBaseDir = toolDir+"-base"
  targetToolSrcDir = workingDir+"/"+toolSrcBaseDir

  if os.path.exists(targetToolSrcDir):
    print("\nRemoving existing directory '" + targetToolSrcDir + "' ...")
    cmnd = "rm -rf "+targetToolSrcDir
    if not inOptions.skipOp:
      echoRunSysCmnd(cmnd)
    else:
      print("\nRunning: " + cmnd)

  cmnd = "git clone "+gitUrlBase+toolSrcBaseDir+" "+targetToolSrcDir
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
  extraEnv, inOptions \
  ):

  toolDir = toolName+"-"+toolVer

  print("\nInstalling " + toolDir + " ...")

  outFile = toolDir+"-install.log"
  workingDir=scratch_dir
  toolInstallDir = installBaseDir+"/"+toolDir

  cmnd = devtools_install_dir+"/install-"+toolName+".py" \
    +" --"+toolName+"-version="+toolVer \
    +" --untar --configure --build --install --show-final-instructions" \
    +" --install-dir="+toolInstallDir \
    +" --parallel="+inOptions.parallelLevel \
    +" --install-owner="+inOptions.installOwner \
    +" --install-group="+inOptions.installGroup
  if inOptions.installForAll:
    cmnd += "  --install-for-all"
  if not inOptions.skipOp:
    echoRunSysCmnd(cmnd, workingDir=workingDir, outFile=outFile, timeCmnd=True,
      extraEnv=extraEnv)
  else:
    print("\nRunning: " + cmnd)
    print("\n  Running in working directory: " + workingDir)
    print("\n  Appending environment: " + str(extraEnv))
    print("\n  Writing console output to file " + outFile)


#
# Main
#

def main(cmndLineArgs):
  #
  # Get the command-line options
  #
  autoconf_version = autoconf_version_default
  cmake_version = cmake_version_default
  gcc_version = gcc_version_default
  mpich_version = mpich_version_default
  mvapich_version = mvapich_version_default
  mvapichInstalled = False
  #iterates over tools selected. If name is specified and a ':' is present, non-default version was specified. Updating install version to specified value
  #if no version was specified, default version will be installed
  inOptions = getCmndLineOptions(cmndLineArgs)
  versionList = dict()
  for toolName in inOptions.commonTools.split(','):
    if "cmake" in toolName and ':' in toolName:
      cmake_version = toolName.split(':')[1]
    elif "autoconf" in toolName and ':' in toolName:
      autoconf_version = toolName.split(':')[1]
  for toolName in inOptions.compilerToolset.split(','):
    if "gcc" in toolName and ':' in toolName:
      gcc_version = toolName.split(':')[1]      
    elif "mpich" in toolName and ':' in toolName:
      mpich_version = toolName.split(':')[1]      
    elif "mvapich" in toolName and ':' in toolName:
      mvapich_version = toolName.split(':')[1]
      mvapichInstalled = True
      
  versionList["cmake"] = cmake_version
  versionList["autoconf"] = autoconf_version
  versionList["gcc"] = gcc_version
  versionList["mpich"] = mpich_version
  versionList["mvapich"] = mvapich_version
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
  print("\nSelected compiler toolset = " + str(compilerToolsetSelected))
  compilerToolsetSelectedSet = set(compilerToolsetSelected)

  dev_env_base_dir = inOptions.installDir

  ###
  print("\n\nA) Setup the install directory <dev_env_base> ='" +
        dev_env_base_dir + "':\n")
  ###

  dev_env_base_exists = os.path.exists(dev_env_base_dir)

  common_tools_dir = os.path.join(dev_env_base_dir, "common_tools")
  common_tools_exists = os.path.exists(common_tools_dir)

  compiler_toolset_base_dir = os.path.join(dev_env_base_dir, "gcc-"+gcc_version)
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
    if not dev_env_exists and not inOptions.skipOp:
      os.makedirs(dev_env_dir)
    if not common_tools_exists:
      print("Creating directory '" + common_tools_dir + "' ...")
      if not inOptions.skipOp:
        os.makedirs(common_tools_dir)

    # Always create this directory so we can write the load_dev_env.sh script!
    if not compiler_toolset_base_exists:
      print("Creating directory '" + compiler_toolset_base_dir + "' ...")
      if not inOptions.skipOp:
        os.makedirs(compiler_toolset_base_dir)

    if not compiler_toolset_exists:
      print("Creating directory '" + compiler_toolset_dir + "' ...")
      if not inOptions.skipOp:
        os.makedirs(compiler_toolset_dir)

    print("Writing new files " + inOptions.loadDevEnvFileBaseName +
          ".[sh,csh] ...")
    if not inOptions.skipOp:
      writeLoadDevEnvFiles(dev_env_base_dir, dev_env_dir, inOptions, versionList, mvapichInstalled)

  else:

    print("Skipping setup of the install directory by request!")

    assertInstallDirExists(dev_env_base_dir, inOptions)
    assertInstallDirExists(common_tools_dir, inOptions)
    assertInstallDirExists(compiler_toolset_base_dir, inOptions)
    assertInstallDirExists(compiler_toolset_dir, inOptions)
  if not inOptions.skipOp:
    os.system("mkdir " + dev_env_base_dir + "/images")
    os.system("mkdir " + dev_env_base_dir + "/images/dev_env")
    os.system("mkdir " + dev_env_base_dir + "/images/install")
    gcc_first = gcc_version[0]
    gcc_short = str()
    for chr in gcc_version:
      if chr != '.':
        gcc_short += chr
    if mvapichInstalled:
      mpi_version = "mvapich2-" + mvapich_version
    else:
      mpi_version = "mpich-" + mpich_version
    if inOptions.mkl_true:
      mkl_true = "true"
      tpl_url = 'https://github.com/ehcole/MPACT_tpls.git'
      tpl_source_dir = "/MPACT_tpls/TPL_build/"
    else:
      mkl_true = "false"
      tpl_url = "https://github.com/CASL/vera_tpls.git"
      tpl_source_dir = "/vera_tpls/TPL_build/"
    os.system("autoconf")
    os.system("./configure GCC_VERSION=gcc_version GCC_FIRST=gcc_first GCC_SHORT=gcc_short MPI_VERSION=MPI_VERSION CMAKE_VERSION=cmake_version TPL_URL=tpl_url TPL_SOURCE_DIR=tpl_source_dir MKL_TRUE=mkl_true")
    os.system("mv Dockerfile " + dev_env_base_dir + "/images/dev_env")
    os.system("mv Dockerfile_install " + dev_env_base_dir + "/images/install")
  ###
  print("\n\nB) Download all sources for each selected tool:\n")
  ###
  if inOptions.doDownload:
    for tool in commonToolsSelectedSet:
      if "cmake" in tool:
        print("")
        print("Downloading the source for cmake-" + cmake_version + " ...")
        print("")
        cmakeShort = cmake_version[:-2]
        if not inOptions.skipOp:
          try:
            os.system("wget https://cmake.org/files/v" + cmakeShort + "/cmake-" + cmake_version + ".tar.gz")
          except:
            print("Invalid CMake version passed. No Download link found.")
            exit(1)
          os.system("mv cmake-" + cmake_version + ".tar.gz " + common_tools_dir)
        else:
          print("wget " + dev_env_base_dir + "/common_tools https://cmake.org/files/v" + cmakeShort + "/cmake-" + cmake_version + ".tar.gz")
      elif "autoconf" in tool:
        downloadToolSource("autoconf", autoconf_version,
          inOptions.sourceGitUrlBase, inOptions)
    for tool in compilerToolsetSelectedSet:
      if "gcc" in tool:
        print("")
        print("Downloading the source for gcc-" + gcc_version + " ...")
        print("")
        if not inOptions.skipOp:
          try:
            os.system("wget https://ftp.gnu.org/gnu/gcc/gcc-" + gcc_version + "/gcc-" + gcc_version + ".tar.gz")
          except:
            print("Invalid gcc version passed. No Download link found.")
            exit(1)
        else:
          print("wget https://ftp.gnu.org/gnu/gcc/gcc-" + gcc_version + "/gcc-" + gcc_version + ".tar.gz")

      elif "mpich" in tool:
        if mpich_version == '3.1.3':
          downloadToolSource("mpich", mpich_version,
                             inOptions.sourceGitUrlBase, inOptions)
        else:
          print("")
          print("Downloading the source for mpich-" + mpich_version + " ..")
          print("")
          if not inOptions.skipOp:
            try:
              os.system("wget / http://www.mpich.org/static/downloads/" + mpich_version + "/mpich-" + mpich_version + ".tar.gz")
            except:
              print("Invalid mpich version passed. No Download link found.")
              exit(1)
          else:
            print("wget http://www.mpich.org/static/downloads/" + mpich_version + "/mpich-" + mpich_version + ".tar.gz")
      elif "mvapich" in tool:
        print("")
        print("Downloading the source for mvapich-" + mvapich_version + " ..")
        print("")
        if not inOptions.skipOp:
          try:
            os.system("wget http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-" + mvapich_version + ".tar.gz")
          except:
            print("Invalid mvapich version passed. No Download link found.")
            exit(1)
        else:
          print("wget/ http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-" + mvapich_version + ".tar.gz")
  else:

    print("Skipping download of the source for the tools on request!")
    if inOptions.doInstall:
      print("NOTE: The downloads had better be there for the install!")

  ###
  print("\n\nC) Untar, configure, build and install each selected tool:\n")
  ###
  if inOptions.doInstall:
    if "gitdist" in commonToolsSelectedSet:
      print("\nInstalling gitdist ...")
      echoRunSysCmnd("cp "+pythonUtilsDir+"/gitdist "+common_tools_dir+"/")
      InstallProgramDriver.fixupInstallPermissions(inOptions, common_tools_dir)

    if "cmake" in commonToolsSelectedSet:
      os.system("tar -xf " + common_tools_dir + "/cmake-" + cmake_version + ".tar.gz")
      os.system("mv -f cmake-" + cmake_version + " " + common_tools_dir)
      os.system("yum install openssl-devel")
      if not inOptions.skipOp:
        try:
          os.system("cmake " + common_tools_dir + "/cmake-" + cmake_version + " -DCMAKE_USE_OPENSSL=ON -DCMAKE_INSTALL_PREFIX=" + dev_env_base_dir + "/common_tools/cmake-" + cmake_version + "/")
        except:
          os.system("cmake " + common_tools_dir + "/cmake-" + cmake_version + " -DCMAKE_INSTALL_PREFIX=" + dev_env_base_dir + "/common_tools/cmake-" + cmake_version + "/")
        os.system("make -j8 install")
        os.system("cd ..")
        cmake_module = open(dev_env_dir + "/cmake-" + cmake_version, 'w+')
        cmake_module.write("#%Module\n\n")
        cmake_module.write("set version " + cmake_version + "\n")
        cmake_module.write('set name "MPACT Development Environment - 2.1.0"\n')
        cmake_module.write('set msg "Loads the development environment for MPACT."\n')
        cmake_module.write('\n')
        cmake_module.write("procs ModulesHelp { } {\n")
        cmake_module.write(" puts stderr $msg }\n\n")
        cmake_module.write("module-whatis $msg\n")
        cmake_module.write(common_tools_dir + "cmake-$version/bin\n")
        cmake_module.close()
    if "autoconf" in commonToolsSelectedSet:
      installToolFromSource("autoconf", autoconf_version_default,
        common_tools_dir, None, inOptions )

    if "gcc" in compilerToolsetSelectedSet:
      print("unpacking gcc-" + gcc_version + ".tar.gz...")
      os.system("tar xzf gcc-" + gcc_version + ".tar.gz")
      os.chdir("gcc-" + gcc_version)
      print("downloading gcc prerequisites...")
      os.system("./contrib/download_prerequisites")      
      os.chdir(compiler_toolset_dir)
      os.system("mkdir gcc-" + gcc_version)
      os.chdir("gcc-" + gcc_version)
      print("configuring gcc...")
      os.system(scratch_dir + "/gcc-" + gcc_version + "/configure --disable-multilib --prefix=" + compiler_toolset_dir + "/gcc-" + gcc_version + " --enable-languages=c,c++,fortran")
      print("building gcc...")
      os.system("make -j8")
      os.system("make install")
      os.chdir(scratch_dir)
      if not inOptions.skipOp:
        gcc_module = open(dev_env_dir + "/gcc-" + gcc_version, 'w+')
        gcc_module.write("#%module\n\n")
        gcc_module.write("set root " + dev_env_base_dir + "\n")
        gcc_module.write("set version gcc-" + gcc_version + "\n")
        gcc_module.write("set tpldir " + compiler_toolset_base_dir + "/tpls\n")
        gcc_module.write('set name "MPACT Development Environment - $version"\n')
        gcc_module.write('set msg "Loads the development environment for MPACT."\n')
        gcc_module.write('proc ModulesHelp { } {\n')
        gcc_module.write(" puts stderr $msg }\n")
        gcc_module.write("module-whatis $msg\n")
        if not mvapichInstalled:
          gcc_module.write("if ![ is-loaded 'mpi/mpich-" + mpich_version + "-x86_64' ] {\n")
          gcc_module.write(" module load mpi/mpich-" + mpich_version + "-x86_64 }\n")
        else:
          gcc_module.write("if ![ is-loaded 'mpi/mvapich-" + mvapich_version + "-x86_64' ] {\n")
          gcc_module.write(" module load mpi/mvapich-" + mvapich_version + "-x86_64 }\n")
        gcc_module.write("setenv TRIBITS_DEV_ENV_BASE          $root\n")
        gcc_module.write("setenv TRIBITS_DEV_ENV_GCC_VERSION   $version\n")
        gcc_module.write("setenv TRIBITS_DEV_ENV_COMPILER_BASE $root/$version\n")
        gcc_module.write("setenv TRIBITS_DEV_ENV_MPICH_DIR     $env(MPI_HOME)\n")
        gcc_module.write("setenv LOADED_TRIBITS_DEV_ENV        $version\n")
        gcc_module.write("setenv LOADED_VERA_DEV_ENV        $version\n")
        gcc_module.write("prepend-path PATH $root/common_tools\n")
        gcc_module.write("set tplpath $tpldir/hdf5-1.8.10\n")
        gcc_module.write("setenv HDF5_ROOT             $tplpath\n")
        gcc_module.write("prepend-path PATH            $tplpath/bin\n")
        gcc_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
        gcc_module.write("prepend-path INCLUDE         $tplpath/include\n")
        gcc_module.write("set tplpath $tpldir/lapack-3.3.1\n")
        gcc_module.write("setenv BLAS_ROOT             $tplpath\n")
        gcc_module.write("setenv LAPACK_DIR            $tplpath\n")
        gcc_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
        gcc_module.write("set tplpath $tpldir/hypre-2.9.1a\n")
        gcc_module.write("setenv HYPRE_DIR             $tplpath\n")
        gcc_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
        gcc_module.write("set tplpath $tpldir/petsc-3.5.4\n")
        gcc_module.write("setenv PETSC_DIR             $tplpath\n")
        gcc_module.write("prepend-path PATH            $tplpath/bin\n")
        gcc_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
        gcc_module.write("set tplpath $tpldir/slepc-3.5.4\n")
        gcc_module.write("setenv SLEPC_DIR             $tplpath\n")
        gcc_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
        gcc_module.write("set tplpath $tpldir/sundials-2.9.0\n")
        gcc_module.write("setenv SUNDIALS_DIR          $tplpath\n")
        gcc_module.write("prepend-path LD_LIBRARY_PATH $tplpath/lib\n")
        gcc_module.write("set-alias gitdist-status     {gitdist dist-repo-status}\n")
        gcc_module.write("set-alias gitdist-mod        {gitdist --dist-mod-only}\n")
        gcc_module.close()
        
    if "mpich" in compilerToolsetSelectedSet:
      gccInstallDir = compiler_toolset_dir+"/gcc-"+gcc_version
      if not os.path.exists(gccInstallDir) and not inOptions.skipOp:
        raise Exception("Error, gcc has not been installed yet." \
          "  Missing directory '"+gccInstallDir+"'") 
      LD_LIBRARY_PATH = os.environ.get("LD_LIBRARY_PATH", "")
      if mpich_version == "3.1.3":
        installToolFromSource(
          "mpich",
          mpich_version,
          compiler_toolset_dir,
          {
            "CC" : gccInstallDir+"/bin/gcc",
            "CXX" : gccInstallDir+"/bin/g++",
            "FC" : gccInstallDir+"/bin/gfortran",
            "LD_LIBRARY_PATH" : compiler_toolset_dir+"/lib64:"+LD_LIBRARY_PATH
          },
          inOptions
        )
      else:
        os.system("tar xfz mpich-" + mpich_version + ".tar.gz")
        os.system("mkdir -p " + compiler_toolset_dir + "/mpich-" + mpich_version)
        os.system("mkdir tmp") 
        os.chdir("tmp")
        os.system("../mpich-" + mpich_version +  "/configure -prefix=" + compiler_toolset_dir + "/mpich-" + mpich_version)
        os.system("make")
        os.system("make install")
      if not inOptions.skipOp:
        mpich_module = open(dev_env_dir + "/mpich-" + mpich_version, 'w+')
        mpich_module.write("conflict mvapich\n")
        mpich_module.write("prepend-path            PATH            /usr/lib64/mpich/bin\n")
        mpich_module.write("prepend-path            LD_LIBRARY_PATH /usr/lib64/mpich/lib\n")
        mpich_module.write("prepend-path            PYTHONPATH      /usr/lib64/python2.7/site-packages/mpich\n")
        mpich_module.write("prepend-path            MANPATH         /usr/share/man/mpich-x86_64\n")
        mpich_module.write("prepend-path            PKG_CONFIG_PATH /usr/lib64/mpich/lib/pkgconfig\n")
        mpich_module.write("setenv                  MPI_BIN         /usr/lib64/mpich/bin\n")
        mpich_module.write("setenv                  MPI_SYSCONFIG   /etc/mpich-x86_64\n")
        mpich_module.write("setenv                  MPI_FORTRAN_MOD_DIR     /usr/lib64/gfortran/modules/mpich-x86_64\n")
        mpich_module.write("setenv                  MPI_INCLUDE     /usr/include/mpich-x86_64\n")
        mpich_module.write("setenv                  MPI_LIB         /usr/lib64/mpich/lib\n")
        mpich_module.write("setenv                  MPI_MAN         /usr/share/man/mpich-x86_64\n")
        mpich_module.write("setenv                  MPI_PYTHON_SITEARCH     /usr/lib64/python2.7/site-packages/mpich\n")
        mpich_module.write("setenv                  MPI_COMPILER    mpich-x86_64\n")
        mpich_module.write("setenv                  MPI_SUFFIX      _mpich\n")
        mpich_module.write("setenv                  MPI_HOME        /usr/lib64/mpich\n")
        mpich_module.close()

    elif "mvapich" in compilerToolsetSelectedSet:
      gccInstallDir = compiler_toolset_dir+"/gcc-"+gcc_version
      if not os.path.exists(gccInstallDir) and not inOptions.skipOp:
        raise Exception("Error, gcc has not been installed yet." \
          "  Missing directory '"+gccInstallDir+"'") 
      LD_LIBRARY_PATH = os.environ.get("LD_LIBRARY_PATH", "")
      mvapichDir = gccInstallDir + "/toolset/mvapich-" + mvapich_version
      if not inOptions.skipOp:
        os.system("yum install libibverbs")
        os.system("gzip -dc mvapich2-" + mvapich_version + ".tar.gz | tar -x")
        os.chdir("mvapich2-" + mvapich_version)
        os.system("./configure --prefix " + mvapichDir)
        os.system("make -j8")
        os.system("make install")
        mvapich_module = open(dev_env_dir + "/mvapich-" + mvapich_version, 'w+')
        mvapich_module.write("conflict mpich\n")
        mvapich_module.write("prepend-path            PATH            /usr/lib64/mvapich2/bin\n")
        mvapich_module.write("prepend-path            LD_LIBRARY_PATH /usr/lib64/mvapich2/lib\n")
        mvapich_module.write("prepend-path            PYTHONPATH      /usr/lib64/python2.7/site-packages/mvapich2\n")
        mvapich_module.write("prepend-path            MANPATH         /usr/share/man/mvapich2-x86_64\n")
        mvapich_module.write("prepend-path            PKG_CONFIG_PATH /usr/lib64/mvapich2/lib/pkgconfig\n")
        mvapich_module.write("setenv                  MPI_BIN         /usr/lib64/mvapich2/bin\n")
        mvapich_module.write("setenv                  MPI_SYSCONFIG   /etc/mvapich2-x86_64\n")
        mvapich_module.write("setenv                  MPI_FORTRAN_MOD_DIR     /usr/lib64/gfortran/modules/mvapich2-x86_64\n")
        mvapich_module.write("setenv                  MPI_INCLUDE     /usr/include/mvapich2-x86_64\n")
        mvapich_module.write("setenv                  MPI_LIB         /usr/lib64/mvapich2/lib\n")
        mvapich_module.write("setenv                  MPI_MAN         /usr/share/man/mvapich2-x86_64\n")
        mvapich_module.write("setenv                  MPI_PYTHON_SITEARCH     /usr/lib64/python2.7/site-packages/mvapich2")
        mvapich_module.write("setenv                  MPI_COMPILER    mvapich2-x86_64\n")
        mvapich_module.write("setenv                  MPI_SUFFIX      _mvapich2\n")
        mvapich_module.write("setenv                  MPI_HOME        /usr/lib64/mvapich2")
        mvapich_module.close()
  else:
    print("Skipping install of the tools on request!")

  ###
  print("\n\nD) Final instructions for using installed dev env:")
  ###

  if inOptions.skipOp:
    print("\n***")
    print("*** NOTE: --no-op provided, only traced actions that would have been taken!")
    print("***")
  else:
    os.system("mv load_dev_env.sh " + dev_env_dir)
    os.system("mv load_dev_env.csh " + dev_env_dir)

  print("installing CMake target for vera_tpls")
  if not inOptions.skipOp and inOptions.doInstall:   
    os.system("mkdir " + compiler_toolset_base_dir + "/tpls")
    os.chdir(scratch_dir + "/..")
    os.system("git submodule init && git submodule update")
    if not os.path.exists(scratch_dir + "/tmp"):
      os.mkdir(scratch_dir + "/tmp")
    os.chdir(scratch_dir + "/tmp")
    os.system("rm -rf *")
    os.system("module load mpi")
    os.system('cmake  -D CMAKE_INSTALL_PREFIX=' + compiler_toolset_base_dir + '/tpls -D CMAKE_BUILD_TYPE=Release  -D CMAKE_CXX_COMPILER=mpicxx  -D CMAKE_C_COMPILER=mpicc  -D CMAKE_Fortran_COMPILER=mpif90  -D FFLAGS="-fPIC -O3"  -D CFLAGS="-fPIC -O3"  -D CXXFLAGS="-fPIC -O3"  -D LDFLAGS=""  -D ENABLE_SHARED=ON  -D PROCS_INSTALL=8 ../../vera_tpls/TPL_build')
    os.system("make -j8 || make -j8")
  else:
    print("git submodule init && git submodule update")
    print('cmake  -D CMAKE_INSTALL_PREFIX=' + compiler_toolset_base_dir + '/tpls -D CMAKE_BUILD_TYPE=Release  -D CMAKE_CXX_COMPILER=mpicxx  -D CMAKE_C_COMPILER=mpicc  -D CMAKE_Fortran_COMPILER=mpif90  -D FFLAGS="-fPIC -O3"  -D CFLAGS="-fPIC -O3"  -D CXXFLAGS="-fPIC -O3"  -D LDFLAGS=""  -D ENABLE_SHARED=ON  -D PROCS_INSTALL=8 ../vera_tpls/TPL_build')
    print("make -j8")
  if not inOptions.skipOp:
    if inOptions.build_image:
      print("building docker image")
      os.system("docker build -t test-mpact-dev-env " + dev_env_base_dir + "/images")  
  if inOptions.showFinalInstructions:
    print("\nTo use the new dev env, just source the file:\n")
    print("  source " + dev_env_base_dir + "/env/load_dev_env.sh\n")
    print("for sh or bash shells (or load_dev_env.csh for csh shell).\n")
    print("TIP: Add this source to your ~/.bash_profile!")
  else:
    print("Skipping on request ...")
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
