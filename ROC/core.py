import numpy
import pandas
from sklearn import metrics
from itertools import permutations

from typing import Dict

class ROC_curve_data:

    def __init__(self, fpr: numpy.ndarray, tpr: numpy.ndarray, threshold: numpy.ndarray, auc: float):
        self.fpr : numpy.ndarray = fpr
        self.tpr : numpy.ndarray = tpr
        self.threshold : numpy.ndarray = threshold
        self.auc : float = auc

def normalization(raw_data: pandas.DataFrame) -> pandas.DataFrame:
    # TODO remove 11 from here
    raw_data = raw_data.dropna(axis=1, how="all")
    column_names = list(raw_data)
    norm_data = pandas.DataFrame(raw_data, columns=raw_data.columns[:11])
    result = all_divs(numpy.array(raw_data.iloc[:,11:]))
    result_df = pandas.DataFrame(result, columns=map(lambda pair: '{}/{}'.format(*pair), permutations(column_names[11:], 2)), index=norm_data.index)
    norm_data = pandas.concat([norm_data, result_df], axis='columns')
    norm_data = norm_data.dropna(axis=1, how="all")
    norm_data = norm_data.fillna(0)
    return norm_data

def roc_analyze(classes: pandas.DataFrame, norm_data: pandas.DataFrame) -> Dict[str, ROC_curve_data]:
    result = {}
    for name, column in norm_data.iteritems():
        fpr, tpr, threshold = metrics.roc_curve(classes, column)
        roc_auc = metrics.auc(fpr, tpr)
        result[name] = ROC_curve_data(fpr=fpr, tpr=tpr, threshold=threshold, auc=roc_auc)
    return result

def all_divs(data: numpy.ndarray) -> numpy.ndarray:
    '''
    >>> from numpy import array
    >>> arg = array([[1, 2, 8],   \
                     [3, 4, 6],   \
                     [5, 6, 8]])
    >>> all_divs(arg) == array([[1/2, 1/8, 2/1, 2/8, 8/1, 8/2],  \
                                [3/4, 3/6, 4/3, 4/6, 6/3, 6/4],  \
                                [5/6, 5/8, 6/5, 6/8, 8/5, 8/6]])
    array([[ True,  True,  True,  True,  True,  True],
           [ True,  True,  True,  True,  True,  True],
           [ True,  True,  True,  True,  True,  True]])
    '''
    row_count, col_count = data.shape
    permutations_count = col_count * (col_count - 1)
    result = numpy.zeros((row_count, permutations_count))
    for i, (divident, divider) in enumerate(permutations(range(col_count), 2)):
        result[:,i] = data[:,divident] / data[:,divider]
    return result