import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.1'
PACKAGE_NAME = 'marcpy'
AUTHOR = 'MARC Research Services'
AUTHOR_EMAIL = 'marc_gis@email.com'
URL = 'https://github.com/MARC-KC/marcpy'

LICENSE = ''
DESCRIPTION = 'Collection of useful function used by MARC Research Services'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'numpy', #conda
      'pandas', #conda, keyringHelper
      'keyring', #keyringHelper
      'pyodbc' #keyringHelper
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )