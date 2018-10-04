#!/bin/bash

check_path() {
	if [ ! -d "$1" ]; then
		echo "Provided path does not exist!"
		exit 1
	fi
	if [ -L "$1" ] || [ ! -w "$1" ]; then
		echo "No write access, or provided path is a symlink"
		exit 1
	fi
}

check_gcc() {
	if [ ! $(find $base_dir -type f -name 'gcc' | wc -l) -eq 1 ] || 
	   [ ! $(find $base_dir -type f -name 'g++' | wc -l) -eq 1 ] || 
	   [ ! $(find $base_dir -type f -name 'gfortran' | wc -l) -eq 1 ]; then
		echo "User specified a pre-installed gcc but one could not be found"
		exit 1
	fi
}

print_help() {
	echo "Usage: ./VERA_install.sh <INSTALL_DIR> [-options]"
	echo "Where valid options are:"
	echo "    -j <int> 	for the number of processes to build on (default 4)"
	echo "    -s <path> 	is the scratch directory 		(default current directory)"
	echo "    -g <ver>	is the gcc version. 5.4.0 or 4.8.3.	(default 5.4.0)"
	echo "    -n		to skip installation of gcc		(will check <install_dir>/toolset/gcc*)"
	echo "    -h		to print this help"
	echo ""
	echo "Note that the install directory path may not have a symlink in it, and you must have write access"
	echo "Skipping the gcc installation is not recommended."
}

# Argument processing

if [ "$#" -lt  1 ]; then
	echo "You must provide an installation directory as the first argument"
	exit 1
fi

if [ "$1" = "-h" ]; then
	print_help
	exit 0
fi

check_path $1
base_dir=`readlink -f $1`
shift

# Set default values to vars
ver="5.4.0"
mpich_ver="3.2.1"
cmake_ver="3.10.2"
build_procs=4
skip_gcc=0
start_dir=${PWD}

while getopts "j:g::cs:nhd" opt; do
	case $opt in
		j) build_procs=$OPTARG;;
		s) check_path $OPTARG; start_dir=$OPTARG;;
		g)
			if [ $OPTARG -eq "5.4.0" ]; then
				ver = $OPTARG
				mpich_ver="3.2.1"
			fi
			if [ $OPTARG -eq "4.8.3" ]; then
				ver = $OPTARG
				mpich_ver="unsure"
			fi
			;;
		n) check_gcc; skip_gcc=1;;
		h) print_help; exit 0;;
		\?)
			echo "Invalid option: -$OPTARG" >&2
			exit 1
			;;
		:)
			echo "Option -$OPTARG requires an argument." >&2
			exit 1
			;;
	esac
done

echo "This script will compile gcc 5.4.0 or 4.8.3"
echo "Your system must be running with a compiler that can compile your chosen version of the dev environment"
echo "We recommend running the same compiler you will be installing."
echo "RHEL/Ubuntu users should install the correct compiler with their package manager and set the PATH accordingly."
echo "Fedora users may install using --releasever and --installroot"
echo ""
echo "If your compiler cannot compile the chosen version of gcc this installer WILL fail"
read -p "Press enter to continue..."

cd $start_dir
install=${base_dir}/gcc-${ver}/toolset
tpl_install_base=${base_dir}/gcc-${ver}
common_install=${base_dir}/gcc-${ver}/common_tools
mkdir -p ${install}
mkdir -p ${common_install}

# Set the package manager
if command -v apt-get > /dev/null; then
	pacman="apt-get install"
elif command -v yum > /dev/null; then
	pacman="yum install"
elif command -v dnf > /dev/null; then
	pacman="dnf install"
else
	pacman="Error setting package manager"
fi

if [ $EUID -ne 0 ]; then
       	if [ ! command -v sudo ]; then
		echo "You are not running this script as root and sudo is not installed."
		echo "Install sudo before continuing"
		exit 1
	fi
	pacman="sudo "$pacman
fi

echo "To continue, we must verify a few packages are installed."
echo "You may be asked for your password to run the package manager."
$pacman -y wget libxext-devel


###########
##  GCC  ##
###########

if [ $skip_gcc -eq 0 ]; then
	# Download
	wget -N http://ftp.gnu.org/gnu/gcc/gcc-${ver}/gcc-${ver}.tar.gz

	# Untar
	tar zxvf gcc-${ver}.tar.gz
	mv gcc-${ver} gcc-${ver}-source

	# Download gcc prerequisites (gmp etc...)
	cd gcc-${ver}-source
	./contrib/download_prerequisites
	cd ${start_dir}

	# Set up build directory
	mkdir build_gcc
	cd build_gcc && rm -rf *

	# Build and install
	# Check glibc version, and apply patch if necessary
	lddVer=`ldd --version | awk '/ldd/{print $NF}'`
	lddVer=${lddVer: -2}
	if [ "$lddVer" -gt "25" ]; then
		cd ../gcc-${ver}-source
		wget -O compiler.patch https://gcc.gnu.org/git/?p=gcc.git\;a=patch\;h=14c2f22a1877f6b60a2f7c2f83ffb032759456a6
		patch -f -p1 < compiler.patch
		cd ../build_gcc
		../gcc-${ver}-source/configure --disable-multilib --disable-libsanitizer --enable-languages=c,c++,fortran --prefix=${install}/gcc-${ver}
	else
		../gcc-${ver}-source/configure --disable-multilib --enable-languages=c,c++,fortran --prefix=${install}/gcc-${ver}
	fi

	make -j${build_procs}
	make install

	# Set up env for mpich build
	export PATH=${install}/gcc-${ver}/bin:$PATH
	export LD_LIBRARY_PATH=${install}/gcc-${ver}/lib64:$LD_LIBRARY_PATH
else
	install=$(find $base_dir -type f -name 'gcc')
	install=${install::-7}
	export PATH=$install/bin:$PATH
	export LD_LIBRARY_PATH=$install/lib64:$LD_LIBRARY_PATH
	install=$install/..
fi

cd ${start_dir}


#############
##  mpich  ##
#############


# Download mpich
wget -N http://www.mpich.org/static/downloads/${mpich_ver}/mpich-${mpich_ver}.tar.gz
tar zxvf mpich-${mpich_ver}.tar.gz
mv mpich-${mpich_ver} mpich-${mpich_ver}-source

# Create build directory
mkdir build_mpich
cd build_mpich && rm -rf *

#Build and install
env CC=gcc CXX=g++ FC=gfortran ../mpich-${mpich_ver}-source/configure --prefix=${install}/mpich-${mpich_ver}
make -j${build_procs}
make install

cd ${start_dir}


#############
##  cmake  ##
#############


# Download cmake
wget -N https://cmake.org/files/v3.10/cmake-${cmake_ver}.tar.gz
tar zxvf cmake-${cmake_ver}.tar.gz
mv cmake-${cmake_ver} cmake-${cmake_ver}-source

# Create build directory
mkdir build_cmake
cd build_cmake && rm -rf *

# Build and install
../cmake-${cmake_ver}-source/bootstrap --prefix=${common_install}/cmake-${cmake_ver}
make -j${build_procs}
make install

export PATH=${common_install}/cmake-${cmake_ver}/bin:$PATH
cd ${start_dir}


# Clean-up
rm -rf gcc-${ver}-source
rm -rf build_gcc
rm -rf mpich-${mpich_ver}-source
rm -rf build_mpich
rm -rf cmake-${cmake_ver}-source
rm -rf build_cmake

# Make env load script
echo "#!/bin/sh" > gcc_env.sh
echo ""  >> gcc_env.sh
echo ""  >> gcc_env.sh
echo 'export PATH=${install}/gcc-${ver}/bin:$PATH' >>  gcc_env.sh
echo 'export PATH=${install}/mpich-${mpich_ver}/bin:$PATH' >>  gcc_env.sh
echo 'export PATH=${common_install}/cmake-${cmake_ver}/bin:$PATH' >> gcc_env.sh
echo 'export LD_LIBRARY_PATH=${install}/mpich-${mpich_ver}/lib:$LD_LIBRARY_PATH' >>  gcc_env.sh
chmod 750 gcc_env.sh
source ./gcc_env.sh


##################
##  VERA TPL's  ##
##################

# Since it's a pain to get access to casl-dev outside ORNL, use github.
#git clone git@casl-dev:prerequisites/vera_tpls
git clone https://github.com/CASL/vera_tpls

export VERA_TPL_INSTALL_DIR=$tpl_install_base/tpls/opt
export LOADED_TRIBITS_DEV_ENV=gcc-${ver}
${start_dir}/vera_tpls/TPL_build/install_tpls.sh -DPROCS_INSTALL=${build_procs} -DCMAKE_INSTALL_PREFIX=${VERA_TPL_INSTALL_DIR} -D CMAKE_BUILD_TYPE:STRING=Release -D TPL_LIST:STRING="BOOST;LAPACK;ZLIB;HDF5;NETCDF;SILO;PETSC;SLEPC;SUNDIALS;QT" -DENABLE_STATIC:BOOL=OFF -DENABLE_SHARED:BOOL=ON  2>&1 |tee install_tpls.out


#export VERA_TPL_INSTALL_DIR=$tpl_install_base/tpls/opt_static
#export LOADED_TRIBITS_DEV_ENV=gcc-${ver}
#${start_dir}/vera_tpls/TPL_build/install_tpls.sh -DPROCS_INSTALL=${build_procs} -DCMAKE_INSTALL_PREFIX=${VERA_TPL_INSTALL_DIR} -D CMAKE_BUILD_TYPE:STRING=Release -D TPL_LIST:STRING="BOOST;LAPACK;ZLIB;HDF5;NETCDF;SILO;PETSC;SLEPC;SUNDIALS;QT" -DENABLE_STATIC:BOOL=ON -DENABLE_SHARED:BOOL=OFF  2>&1 |tee install_tpls.out

export VERA_TPL_INSTALL_DIR=$tpl_install_base/tpls/dbg
export LOADED_TRIBITS_DEV_ENV=gcc-${ver}
${start_dir}/vera_tpls/TPL_build/install_tpls.sh -DPROCS_INSTALL=${build_procs} -DCMAKE_INSTALL_PREFIX=${VERA_TPL_INSTALL_DIR} -D CMAKE_BUILD_TYPE:STRING=Debug -D TPL_LIST:STRING="BOOST;LAPACK;ZLIB;HDF5;NETCDF;SILO;PETSC;SLEPC;SUNDIALS;QT" -DENABLE_STATIC:BOOL=OFF -DENABLE_SHARED:BOOL=ON  2>&1 |tee install_tpls.out


#export VERA_TPL_INSTALL_DIR=$tpl_install_base/tpls/dbg_static
#export LOADED_TRIBITS_DEV_ENV=gcc-${ver}
#${start_dir}/vera_tpls/TPL_build/install_tpls.sh -DPROCS_INSTALL=${build_procs} -DCMAKE_INSTALL_PREFIX=${VERA_TPL_INSTALL_DIR} -D CMAKE_BUILD_TYPE:STRING=Debug -D TPL_LIST:STRING="BOOST;LAPACK;ZLIB;HDF5;NETCDF;SILO;PETSC;SLEPC;SUNDIALS;QT" -DENABLE_STATIC:BOOL=ON -DENABLE_SHARED:BOOL=OFF  2>&1 |tee install_tpls.out
