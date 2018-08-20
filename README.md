# mpact-dev-env
<b>Overview</b>

This repository contains scripts to install the MPACT development environment into a specified directory. The following tools are installed, using user-specified versions: autoconf, cmake, gitdist, gcc, mpi (mpich or mvapich). Additionally, the VERA third party libraries (tpls) are included as a submodule and installed. Lastly, a Dockerfile is written and optionally built into a container with an MPACT development environment with SSH access. Installation of VERA tpls requires Python 2 and will fail if Python 3 is used.

The installation creates the following directory structure:

* <install_dir>/
  * common_tools/
    * autoconf-<i>autoconf-version</i>/
    * cmake-<i>cmake-version</i>/
    * gitdist/
  * gcc-<gcc-version>/
    * load_dev_env.[sh,csh]
    * toolset/
      * gcc-<i>gcc-version</i>/
      * mpich-<i>mpich-version</i>/
    * tpls/
  * images/
    * dev_env/
    * install/

    
<b>Versioning</b>

mpact-dev-env-<major_version>.<minor_version>.<patch>-tag

Major version: incremented if TPLs or toolchain changes

Minor version: incremented if toolchain changes

Patch: incremented if a TPL version changes

Tag: set for any devations from major.minor.patch
