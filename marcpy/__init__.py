from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

#Import submodules so that you can directly access them after importing the main package
import marcpy.conda
import marcpy.gitcreds
import marcpy.sql
import marcpy.utils
import marcpy.keeper

#Import select functions to the main package
from marcpy.keyring_wrappers import key_set
from marcpy.keyring_wrappers import key_get
from marcpy.keyring_wrappers import key_delete

from marcpy.sql import connectODBC
from marcpy.anti_join import anti_join

#Defines what supmodules should be imported when using $ from marcpy import *
# __all__ = ['conda', 'sql']
