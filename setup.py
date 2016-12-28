'''
@author: jimfan
'''
import os
from setuptools import setup

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(name='dpts1',
      version='0.0.1',
      author='Linxi (Jim) Fan',
      author_email='jimfan@cs.stanford.edu',
      url='http://github.com/LinxiFan/DPT-S1',
      description='Script for Sony e-reader DPT-S1.',
      long_description=read('README.rst'),
      keywords='DPT-S1 pdf',
      license='GPLv3',
      packages=['dpts1'],
      entry_points={
        'console_scripts': [
            'dpts1 = dpts1.monitor'
        ]
      },
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Topic :: Utilities",
          "Environment :: Console",
          "Environment :: MacOS X",
          "Programming Language :: Python :: 3"
      ],
      install_requires=read('requirements.txt').strip().splitlines(),
      include_package_data=True,
#       package_data={
# #         # If any package contains *.txt files, include them:
# #         '': ['*.txt'],
#         'dpst1': ['bin/*'],
#       },
      zip_safe=False
)