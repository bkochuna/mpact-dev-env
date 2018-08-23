# mpact-dev-env
<b>Overview</b>

This repository contains scripts to install the MPACT development environment into a specified directory. The following tools are installed, using user-specified versions: autoconf, cmake, gitdist, gcc, mpi (mpich or mvapich). Additionally, the VERA third party libraries (tpls) are included as a submodule and installed. Installation of VERA tpls requires Python 2 and will fail if Python 3 is used. Lastly, a Dockerfile is written and optionally built into a container with an MPACT development environment with SSH access. 

The installation creates the following directory structure:

    <install-dir>/
    ├── common_tools                      
    │   ├── autoconf-<autoconf-version>
    │   ├── cmake-<cmake-version>
    │   ├── gitdist/
    ├── gcc-<gcc-version>
    │   ├── load_dev_env.[sh,csh]
    │   ├── tpls/
    │   ├── toolset/
    │   │   ├── gcc-<gcc-version>/
    │   │   ├── <mpi>-<mpi-version>/   
    ├── images/
    │   ├── dev_env/
    └── └── install/



    
<b>Quick Install Instructions</b>

To install the default mpact-dev-env, run the following commands:

```bash
  $ git clone https://ners-arc-05.engin.umich.edu/MPACT/mpact-dev-env.git
  $ cd mpact-dev-env/devtools_install
  $ python install_devtools.py --install-dir=<install-dir> --do-all
```
install_devtools.py creates the directory tree within <install dir>, downloads the necessary source code for all tools, then configures and installs the tools.
By default, this installs gcc-4.8.3, mpich-3.1.3, cmake-3.3.2, and autoconf-2.69, i.e, mpact-dev-env-1.0, per the versioning specified below.
For more detailed installation instructions, including specifiying alternate software versions, run python install_devtools.py --help.

    
<b>Versioning</b>

mpact-dev-env-\<major_version>.\<minor_version>.\<patch>-tag

Major version: incremented for dev-envs containing TPL or tool with different major version than used in default

Minor version: incremented for dev-envs containing TPL or tool with different minor version than used in default

Patch: incremented for dev-envs containing TPL or tool with different patch than used in default

Tag: set for any deviations from major.minor.patch

E.g, v1.0 would have gcc-4.8.3 and mpich-3.1.3, v2.0 would have gcc-5.4.0 and mpich-3.1.3, and v1.0-mvapich would have gcc-4.8.3 and mvapich2-2.3.

To build mpact-dev-env-2.0, run:
```bash
  $ python install_devtools.py --install-dir=<install-dir> --compiler-toolset=gcc-5.4.0,mpich --do-all
```

To build mpact-dev-env-3.0, run:
```bash
  $ python install_devtools.py --install-dir=<install-dir> --compiler-toolset=gcc-6.4.0,mpich --do-all
```

<b>Docker and SSH Information</b>

Running install_devtools.py will create the images directory with two subdirectories, each containing a Dockerfile.

Within /images/dev_env will be a Dockerfile to create a containerized mpact development environment with the same parameters that were passed to install_devtools.py (i.e., same versions of gcc, mpi, etc). The image can be built by passing install_devtools the flag -b or --build, or by running "docker build -t \<dev-env image name> ." from within the /images/dev_env/ directory. The container can then be accessed interactively by running "docker run -it \<dev-env image name>". 
 
Within /images/install will be a Dockerfile to create an image that builds off an mpact-dev-env image, adds the contents of /images/install to the /scratch directory of the docker container, and allows ssh access into the development environment to test installation of software. By default, the image builds off an image named "mpact-dev-env:latest". To specify a different image, edit the Dockerfile and change "FROM mpact-dev-env:latest" to "FROM \<dev-env image name>". The image can be built by running "docker build -t \<ssh image name> ." from within the /images/install directory. Note that \<dev-env image name> must have been previously built.
 
To then ssh into the container, run the following commands:
docker run -d -p \<port>:22 \<ssh image name>
ssh mpact-user@\<virtual machine IP> -p \<port>
 
\<port> must be an open port on the virtual machine being used by Docker, and \<virtual machine IP> is the address of that virtual   machine, which can be found by running "docker-machine ip". Alternatively, run "docker run -d -P \<ssh image name>", which causes Docker to automatically map port 22 on the container to an open port on the machine, then run "docker ps -a" to see which port was mapped, then ssh using that port. 

