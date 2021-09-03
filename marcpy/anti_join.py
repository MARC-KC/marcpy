"""This module holds the anti_join function to mimic the anti_join in R's 
{dplyr} package.
"""
import re

import pandas as pd

def anti_join(df_left, df_right, on = None):
    """"Does an anti-join similar to the R {dplyr} package.
    
    Finds all records in 'df_left' that don't appear in 'df_right' based on the 
    join criteria dexcribed in the 'on' parameter.
    
    Parameters
    ----------
    df_left, df_right : pandas.Dataframes
        The dataframes you want to perform the anti-join on. The returned 
        records will come from df_left.
    on : list, dictionary, or None
        If given a list, all named columns must appear in both 'df_left' and 
        'df_right' (Uses the 'on' parameter in pandas.merge()). If given a 
        dictionary, the Keys are the names of the columns in df_left and the 
        Values are the names of the columns in 'df_right' (Uses the 'left_on'
        and 'right_on' parmeters in pandas.merge()). If given None (default), 
        the function will set the 'on' parameter to all columns in 'df_left'
        and raise and error if all columns in 'df_left' are not in 'df_right'.
    
    Returns
    -------
    pandas.Dataframe
        The subset of df_left that is not found in df_right based on the 
        matching criteria.
    """
    
    #Add indicies
    df_left = df_left.copy()
    df_right = df_right.copy()
    df_left.loc[:,'_index_left'] = list(df_left.index)
    df_right.loc[:,'_index_right'] = list(df_right.index)
    
    #Do Right Outer Join
    if isinstance(on, dict):
        df_outer = pd.merge(df_left, df_right,  how='left', left_on=list(on.keys()), right_on = list(on.values()), suffixes = ('_SuffixLeft', '_SuffixRight'))
    elif isinstance(on, list):
        df_outer = pd.merge(df_left, df_right,  how='left', on=on, suffixes = ('_SuffixLeft', '_SuffixRight'))
    elif on is None:
        left_cols = list(df_left.columns)
        left_cols.remove('_index_left') if '_index_left' in left_cols else None
        if not all([x in list(df_right.columns) for x in left_cols]):
            raise ValueError("No 'on' value was specified and not all columns in 'df_left' are found in 'df_right'. Specify 'on' with a list or dictionary.")
        df_outer = pd.merge(df_left, df_right,  how='left', on=left_cols, suffixes = ('_SuffixLeft', '_SuffixRight'))
    
    #Filter out missing columns from left and clean up anti_join returning in same format as df_right
    df_outer.columns = list(map(lambda x: re.sub('_SuffixLeft$', '', x), df_outer.columns))
    df_anti = df_outer.loc[pd.isna(df_outer['_index_right']), list(df_left.columns)].set_index('_index_left')
    df_anti.rename_axis(None, axis=0, inplace=True)
    
    return df_anti