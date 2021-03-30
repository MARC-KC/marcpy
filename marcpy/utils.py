"""This module holds general helper functions.
"""

def query_yesNo(question):
    """Queries and parses the response to a provided yes/no question.
    
    Prompts user to input the answer to a yes/no question and defaults to 
    looking for a 'y' or 'n' as the first character in the response. If not 
    found it reprompts in a while loop until an acceptable response is given.

    Parameters
    ----------
    question : str 
        The question you want to prompt a response to.

    Returns
    -------
    str
        Either a 'y' or a 'n'.

    Example
    -------
    query_yesNo("Do you like Python?")
    """

    while True: 
        query = input(question + " (yes/no): ") 
        out = query[0].lower() 
        if query == '' or out not in ['y','n']: 
            print('Please answer with yes or no.') 
        else: 
            break 

    return out

