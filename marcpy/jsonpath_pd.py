import sys
import re

#conda
import pandas as pd
import jsonpath_ng #conda-forge



def _formatFullPath(path, key = None, generalizeIDs = False):
    """Format a jsonpath_ng full_path to a string
    
    Parameters
    ----------
    path : jsonpath_ng.jsonpath.DatumInContext.full_path
    key : jsonpath_ng.jsonpath.DatumInContext.path
    generalizeIDs : bool
        True/False on whether to generalize path (insert '*' for id's in a list)
    
    Return
    ------
    str
        A string with the path in a json-like format.
    """
    
    if key is not None and re.search("\\.", key):
        raise RuntimeError("A key value has a period '.' which will cause errors in the formatFullPath function.")
    if generalizeIDs:
        out = "".join(['["' + field + '"]' if not bool(re.search("^\\[|\\]$", field)) else re.sub("\\[\\d*\\]", "[*]", field) for field in re.split("\\.", path)])
    else:
        out = "".join(['["' + field + '"]' if not bool(re.search("^\\[|\\]$", field)) else field for field in re.split("\\.", path)])
    return(out)


def _getDatumInformation(datum):
    '''Get information about a jsonpath_ng datum
    
    Parameters
    ----------
    datum : jsonpath_ng.jsonpath.DatumInContext
    
    Return
    ------
    dict
        A dictionary with 6 keys: 'Key', 'FullPath', 'FullPathGeneralized', 
        'Value', 'isDict', 'isList'.
    '''
    
    #Pull data
    key = str(datum.path)
    value = str(datum.value)
    fullPath = str(datum.full_path)
    
    #Format data
    formattedFullPath = _formatFullPath(path = fullPath, key = key, generalizeIDs=False)
    formattedFullPath_generalized = _formatFullPath(path = fullPath, key = key, generalizeIDs=True)
    isDict = True if re.search("^\\{", value) and re.search("\\}$", value) else False
    isList = True if re.search("^\\[", value) and re.search("\\]$", value) else False
    
    return({"Key":key, "FullPath":formattedFullPath, "FullPath_Generalized":formattedFullPath_generalized, "Value":value, "isDict":isDict, "isList":isList})





def JSONtoLongDataFrame(jsonObject, parseString = "$..*"):
    '''Parse JSON into a data frame
    
    Takes every value in a JSON file and parses it into a pandas dataframe.
    
    Parameters
    ----------
    jsonObject : JSON object / dictionary
        The input json you want to parse.
    parseString : string
        Passed to jsonpat_ng.parse(). Default ("$..*") returns all keys in the 
        json object.
    
    Return
    ------
    pandas.DataFrame
        Returns a pandas dataframe for all the objects found.
    '''
    
    return(pd.DataFrame([_getDatumInformation(datum) for datum in jsonpath_ng.parse(parseString).find(jsonObject)]))


def test_formatFullPath():
    assert _formatFullPath(path = "test.[3].test1.test2.[0].[1].test4", key = "test4", generalizeIDs = False) == '["test"][3]["test1"]["test2"][0][1]["test4"]'
    assert _formatFullPath(path = "test.[3].test1.test2.[0].[1].test4", key = "test4", generalizeIDs = True) == '["test"][*]["test1"]["test2"][*][*]["test4"]'

def main(argv=None):
    itemData = item.get_data()
    datum = jsonpath_ng.parse("$..*").find(itemData)[0]
    _formatFullPath(path = str(datum.full_path), key = str(datum.path))
    _getDatumInformation(datum)
    JSONtoLongDataFrame(jsonObject = itemData, parseString = "$..*")




if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))