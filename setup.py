import os
import re
import sys
import sysconfig
import platform
import subprocess

from distutils.version import LooseVersion
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                     "CMake must be installed to build the following extensions: " +
                      ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)',
                                         out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable,
#                      '-DCMAKE_CXX_COMPILER=/software/gcc-4.9-el6-x86_64/bin/g++'
        ]

        cfg = 'Debug' #if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
                cfg.upper(),
                extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -std=c++11 -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        print('got files in root:')
        print(os.listdir())
        print('got files in lib:')
        print(os.listdir('./lib'))
        print('got files in lib/pybind11:')
        print(os.listdir('./lib/pybind11'))
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args,
                              cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args,
                              cwd=self.build_temp)
        print()  # Add an empty line for cleaner output

readme = open('README.md').read()
history = open('HISTORY.md').read().replace('.. :changelog:', '')
requirements = open('requirements.txt').read().splitlines()

setup(
    name='nestpy_test2',
    version='1.5.13',
    author='Sophia Farrell',
    author_email='sja5@rice.edu',
    description='Python bindings for the NEST noble element simulations',
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    # packages=find_packages(include=['src', 'lib']),
    packages=['src', 'lib'],
    install_requires=requirements,
    # Include lib such that recompilation under e.g. different numpy versions works
    package_dir={'src': 'src', 'lib': 'lib'},
    package_data={'lib': ['lib/*', ]},
    ext_modules=[CMakeExtension('nestpy/nestpy')],
    cmdclass=dict(build_ext=CMakeBuild),
    test_suite='tests',
    zip_safe=True,
    include_package_data=True,
    project_urls={
        'nestpy source': 'https://github.com/NESTCollaboration/nestpy',
        'NEST library': 'https://github.com/NESTCollaboration/nest',
        'NEST collaboration' : 'http://nest.physics.ucdavis.edu/'
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: C++',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Physics',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux'
    ]
)
