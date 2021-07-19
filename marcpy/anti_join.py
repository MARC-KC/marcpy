"""This module holds the anti_join function to mimic the anti_join in R's 
{dplyr} package.
"""

import pandas as pd

def anti_join(df_left, df_right, on):
    """"Does an anti-join similar to the R {dplyr} package.
    
    Finds all records in 'df_left' that don't appear in 'df_right' based on the 
    join criteria dexcribed in the 'on' parameter.
    
    Parameters
    ----------
    df_left, df_right : pandas.Dataframes
        The dataframes you want to perform the anti-join on. The returned 
        records will come from df_left.
    on : list or dictionary
        If given a list, all named columns must appear in both 'df_left' and 
        'df_right' (Uses the 'on' parameter in pandas.merge()). If given a 
        dictionary, The Keys are the names of the columns in df_left and the 
        Values are the names of the columns in 'df_right' (Uses the 'left_on'
        and 'right_on' parmeters in pandas.merge()).
    
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
        df_outer = pd.merge(df_left, df_right,  how='left', left_on=list(on.keys()), right_on = list(on.values()))
    elif isinstance(on, list):
        df_outer = pd.merge(df_left, df_right,  how='left', on=on)
    
    #Filter out missing columns from left and clean up anti_join returning in same format as df_right
    df_anti = df_outer.loc[pd.isna(df_outer['_index_right']), list(df_left.columns)].set_index('_index_left')
    df_anti.rename_axis(None, axis=0, inplace=True)
    
    return df_anti