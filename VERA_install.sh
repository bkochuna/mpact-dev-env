#!/bin/sh

#gcc
ver="5.4.0"
mpich_ver="3.2.1"
cmake_ver="3.10.2"
build_procs=4
base_dir=/opt/mpact-dev-env
install=${base_dir}/gcc-${ver}/toolset
tpl_install_base=${base_dir}/gcc-${ver}
common_install=${base_dir}/gcc-${ver}/common_tools
mkdir -p ${install}
mkdir -p ${common_install}

#download gcc
start_dir=${PWD}
wget http://ftp.gnu.org/gnu/gcc/gcc-${ver}/gcc-${ver}.tar.gz

#untar and move
tar zxvf gcc-${ver}.tar.gz
mv gcc-${ver} gcc-${ver}-source

#download gcc prerequisites (gmp etc...)
cd gcc-${ver}-source
./contrib/download_prerequisites
cd ${start_dir}

#set up build
mkdir build_gcc
cd build_gcc && rm -rf *

#build and install
../gcc-${ver}-source/configure --disable-multilib --enable-languages=c,c++,fortran --prefix=${install}/gcc-${ver}
make -j${build_procs}
make install

#set up env for mpich build
export PATH=${install}/gcc-${ver}/bin:$PATH
export LD_LIBRARY_PATH=${install}/gcc-${ver}/lib64:$LD_LIBRARY_PATH
cd ${start_dir}

#mpich
#download mpich
wget http://www.mpich.org/static/downloads/${mpich_ver}/mpich-${mpich_ver}.tar.gz
tar zxvf mpich-${mpich_ver}.tar.gz
mv mpich-${mpich_ver} mpich-${mpich_ver}-source

#create build directory
mkdir build_mpich
cd build_mpich && rm -rf *
#build and install
env CC=gcc CXX=g++ FC=gfortran ../mpich-${mpich_ver}-source/configure --prefix=${install}/mpich-${mpich_ver}
make -j${build_procs}
make install

#cmake
#cmake download
wget https://cmake.org/files/v3.10/cmake-${cmake_ver}.tar.gz
tar zxvf cmake-${cmake_ver}.tar.gz
mv cmake-${cmake_ver} cmake-${cmake_ver}-source

#create build directory
mkdir build_cmake
cd build_cmake && rm -rf *
#build and install
../cmake-${cmake_ver}-source/bootstrap --prefix=${common_install}/cmake-${cmake_ver}
make -j${build_procs}
make install

#clean-up
cd ${start_dir}
rm -rf gcc-${ver}-source
rm -rf build_gcc
rm -rf mpich-${mpich_ver}-source
rm -rf build_mpich


#make env load script
echo "#!/bin/sh" > gcc_env.sh
echo ""  >> gcc_env.sh
echo ""  >> gcc_env.sh
echo 'export PATH=${install}/gcc-${ver}/bin:$PATH' >>  gcc_env.sh
echo 'export PATH=${install}/mpich-${mpich_ver}/bin:$PATH' >>  gcc_env.sh
echo 'export LD_LIBRARY_PATH=${install}/mpich-${mpich_ver}/lib:$LD_LIBRARY_PATH' >>  gcc_env.sh
chmod 750 gcc_env.sh
source ./gcc_env.sh

cd ${start_dir}
#Since it's a pain to get access to casl-dev outside ORNL, use github.
#git clone git@casl-dev:prerequisites/vera_tpls
git clone https://github.com/CASL/vera_tpls

export VERA_TPL_INSTALL_DIR=tpl_install_base/tpls/opt
export LOADED_TRIBITS_DEV_ENV=gcc-${ver}
${start_dir}/vera_tpls/TPL_build/install_tpls.sh -DPROCS_INSTALL=${build_procs} -DCMAKE_INSTALL_PREFIX=${VERA_TPL_INSTALL_DIR} -D CMAKE_BUILD_TYPE:STRING=Release -D TPL_LIST:STRING="BOOST;LAPACK;ZLIB;HDF5;NETCDF;SILO;PETSC;SLEPC;SUNDIALS;QT" -DENABLE_STATIC:BOOL=OFF -DENABLE_SHARED:BOOL=ON  2>&1 |tee install_tpls.out


export VERA_TPL_INSTALL_DIR=tpl_install_base/tpls/opt_static
export LOADED_TRIBITS_DEV_ENV=gcc-${ver}
${start_dir}/vera_tpls/TPL_build/install_tpls.sh -DPROCS_INSTALL=${build_procs} -DCMAKE_INSTALL_PREFIX=${VERA_TPL_INSTALL_DIR} -D CMAKE_BUILD_TYPE:STRING=Release -D TPL_LIST:STRING="BOOST;LAPACK;ZLIB;HDF5;NETCDF;SILO;PETSC;SLEPC;SUNDIALS;QT" -DENABLE_STATIC:BOOL=ON -DENABLE_SHARED:BOOL=OFF  2>&1 |tee install_tpls.out

export VERA_TPL_INSTALL_DIR=tpl_install_base/tpls/dbg
export LOADED_TRIBITS_DEV_ENV=gcc-${ver}
${start_dir}/vera_tpls/TPL_build/install_tpls.sh -DPROCS_INSTALL=${build_procs} -DCMAKE_INSTALL_PREFIX=${VERA_TPL_INSTALL_DIR} -D CMAKE_BUILD_TYPE:STRING=Debug -D TPL_LIST:STRING="BOOST;LAPACK;ZLIB;HDF5;NETCDF;SILO;PETSC;SLEPC;SUNDIALS;QT" -DENABLE_STATIC:BOOL=OFF -DENABLE_SHARED:BOOL=ON  2>&1 |tee install_tpls.out


export VERA_TPL_INSTALL_DIR=tpl_install_base/tpls/dbg_static
export LOADED_TRIBITS_DEV_ENV=gcc-${ver}
${start_dir}/vera_tpls/TPL_build/install_tpls.sh -DPROCS_INSTALL=${build_procs} -DCMAKE_INSTALL
