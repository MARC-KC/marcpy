import pathlib
from setuptools import setup, find_packages
import versioneer

HERE = pathlib.Path(__file__).parent

#VERSION = '0.0.1.9001'
PACKAGE_NAME = 'marcpy'
AUTHOR = 'MARC Research Services'
AUTHOR_EMAIL = 'marc_gis@marc.org'
URL = 'https://github.com/MARC-KC/marcpy'

LICENSE = 'GNUv3'
DESCRIPTION = 'Collection of useful function used by MARC Research Services'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'numpy', #conda
      'pandas>=1.0', #conda, sql, jsonpath_pd
      'keyring>=21.8.0', #keyring_wrappers, gitcreds
      'pyodbc', #keyring_wrappers, sql
      'sqlalchemy', #sql
      'jsonpath-ng' # jsonpath_pd
]

setup(name=PACKAGE_NAME,
      #version=VERSION,
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages(),
      keywords='marcpy',
      #classifiers=[
      #  'Programming Language :: Python :: 3.6',
      #  'Programming Language :: Python :: 3.7',
      #]
)