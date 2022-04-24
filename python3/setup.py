import sys
from setuptools import setup, find_packages, Extension


# Require at least python 3.5
if sys.version_info < (3, 5):
    raise Exception("Python >= 3.5 required!\nYou are using: {}".format(sys.version))


# Python C extensions
if sys.platform == 'linux':
    # Use HugePages for linux
    memory_ext = Extension('hugepages',
                           define_macros=[('MAJOR_VERSION', '0'),
                                          ('MINOR_VERSION', '1')],
                           include_dirs=[],
                           libraries=[
                               'hugetlbfs',
                           ],
                           extra_compile_args=[],
                           extra_link_args=[],
                           sources=['stdk/system/linux/hugepages.c'])

setup(name='stdk',
      version='0.1',
      description='Python Userspace Storage Device Test Framework',
      url=None,
      author='Edoardo Daelli',
      author_email='edoardo.daelli@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
          'tox4',
          'ioctl_opt',
          'pytest-cov',
          'pytest-mock',
          'pylama',
          'pyudev',
      ],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'stdk_setup = stdk.tools.stdk_setup:main',
          ],
      },
      setup_requires=[
          'wheel',
          'pytest-runner'
      ],
      tests_require=[
          'pytest-cov',
          'pytest-mock',
      ],
      ext_modules=[
          memory_ext,
      ],
      cmdclass={
      },)
