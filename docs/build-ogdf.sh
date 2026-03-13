git clone https://github.com/ogdf/ogdf.git ogdf
cd ogdf
git checkout foxglove-202510 # latest release
mkdir build-debug build-release

# this already sets most confinguration options to sensible values for ease of development
# alternatively, change them via `ccmake .`
cmake -B build-debug -S . \
  -DBUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=Debug \
  -DOGDF_MEMORY_MANAGER=POOL_NTS -DOGDF_SEPARATE_TESTS=ON \
  -DOGDF_USE_ASSERT_EXCEPTIONS=ON \
  -DOGDF_USE_ASSERT_EXCEPTIONS_WITH_STACK_TRACE=ON_LIBUNWIND
# if libunwind is not found, install it first or remove the last flag
# https://pkgs.org/search/?q=libunwind-dev
cmake --build build-debug --parallel

# the performance-oriented version of the above configuration
cmake -B build-release -S . \
  -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DOGDF_MEMORY_MANAGER=POOL_NTS -DOGDF_USE_ASSERT_EXCEPTIONS=OFF \
  -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=TRUE -DCMAKE_POLICY_DEFAULT_CMP0069=NEW
cmake --build build-release --parallel

cd ..
mkdir example-project
# copy the example project
cp -r ogdf/doc/examples/special/* example-project/
cd example-project/
mkdir build-debug build-release

# we need to tell cmake where our matching ogdf build is located via OGDF_DIR
cmake -B build-debug -S . \
  -DCMAKE_BUILD_TYPE=Debug -DOGDF_DIR=../../ogdf/build-debug
cmake --build build-debug --parallel

cmake -B build-release -S . \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo -DOGDF_DIR=../../ogdf/build-release \
  -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=TRUE -DCMAKE_POLICY_DEFAULT_CMP0069=NEW
cmake --build build-release --parallel
