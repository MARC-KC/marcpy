#Import submodules so that you can directly access them after importing the main package
import marcpy.conda
import marcpy.gitcreds
import marcpy.sql
import marcpy.utils

#Import select functions to the main package
from marcpy.keyring_wrappers import key_set
from marcpy.keyring_wrappers import key_get
from marcpy.keyring_wrappers import key_delete

#Defines what supmodules should be imported when using $ from marcpy import *
# __all__ = ['conda', 'sql']
