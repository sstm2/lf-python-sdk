from pathlib import Path

from setuptools import find_packages, setup

version_metadata = {}
with open('lfapi/_version.py') as f:
  exec(f.read(), version_metadata)

long_description = (Path(__file__).parent / 'README.md').read_text()

setup(
  name='lfapi',
  version=version_metadata["__version__"],
  author='Joseph Masom',
  author_email='joseph.masom@listenfirstmedia.com',
  url='https://github.com/ListenFirstMedia/lf-python-sdk',
  download_url='https://pypi.org/project/lfapi',
  license='MIT',
  packages=find_packages(include=['lfapi']),
  description='The Python library for the ListenFirst API',
  long_description=long_description,
  long_description_content_type='text/markdown',
  install_requires=[
    'requests'
  ],
  setup_requires=[
    'pytest_runner'
  ],
  tests_require=[
    'pytest'
  ],
  test_suite='tests',
  python_requires='>=3.8, <4',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11'
  ],
  keywords=['listenfirst api sdk']
)
