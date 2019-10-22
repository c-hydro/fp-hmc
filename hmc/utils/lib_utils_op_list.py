"""
Library Features:

Name:          lib_utils_op_list
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20180521'
Version:       '2.0.7'
"""

#######################################################################################
# Library
import logging

from numpy import where, asarray

from hmc.default.lib_default_args import sLoggerName
from hmc.driver.manager.drv_manager_debug import Exc

# Log
oLogStream = logging.getLogger(sLoggerName)

# Debug
# import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Method to convert list 2 dicitonary
def convertList2Dict(var_list, var_fill='var'):

    var_dict = {}
    for step, var in enumerate(var_list):
        var_dict[step] = var

    return var_dict
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to find element indexing
def findIndexElement(main_list, elements=None):
    idx_tot = []
    if main_list and elements is not None:

        if isinstance(elements, str):
            elements = [elements]

        for element in elements:
            if element in main_list:
                idx = main_list.index(element)
                idx_tot.append(idx)
            else:
                idx_tot.append(None)
    return idx_tot
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get list element(s) using indexes
def getListElement(main_list=[], indexes=None):

    if main_list and indexes is not None:
        sel_list = [main_list[x] for x in indexes]
    else:
        sel_list = None
    return sel_list
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to enumerate list boolean element(s) [True/False]
def enumListBool(oList=[True]):
    if oList:
        oElem = asarray(oList)
        oElemT = where(oElem == True)[0]
        oElemF = where(oElem == False)[0]
    else:
        oElemT = None
        oElemF = None
    return oElemT, oElemF
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to check if list element(s) are all the same
def checkListAllSame(items=False):
    if items:
        items_check = all(x == items[0] for x in items)
    else:
        items_check = False
    return items_check
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to reduce list unique value(s)
def reduceListUnique(oList=[]):
    return list(set(oList))
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to convert list to string (given an delimiter)
def convertList2Str(oListData, sListDel=','):
    sListData = sListDel.join(str(oL) for oL in oListData)
    return sListData
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to filter list empty element ("")
def filterListEmpty(oListData):
    return list(filter(None, oListData))
# -------------------------------------------------------------------------------------
