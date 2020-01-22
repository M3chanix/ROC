from django.http import HttpResponse, HttpRequest, JsonResponse

from json import JSONEncoder
import time
from typing import Dict

from django.shortcuts import render
from .forms import NameForm

from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas
import numpy

from core import ROC_curve_data, normalization, roc_analyze
from model import Sample

engine = create_engine('sqlite:///Data.db')
MySession = sessionmaker(bind=engine)
session: Session  = MySession()

# this class is used for validation of HTTP GET parameters
class Filter_values:
    def __init__(self,
                 Sample                : str = '',
                 Tissue                : str = '',
                 Diagnosis             : str = '',
                 Date                  : str = '',
                 File                  : str = '',
                 Source                : str = '',
                 Material              : str = '',
                 Operator_RNA_Isolation: str = '',
                 Operator_PCR          : str = '',
                 RNA_Concentration     : str = ''):
        self.Sample                 : str = Sample
        self.Tissue                 : str = Tissue
        self.Diagnosis              : str = Diagnosis
        self.Date                   : str = Date
        self.File                   : str = File
        self.Source                 : str = Source
        self.Material               : str = Material
        self.Operator_RNA_Isolation : str = Operator_RNA_Isolation
        self.Operator_PCR           : str = Operator_PCR
        self.RNA_Concentration      : str = RNA_Concentration
    
    def __str__(self):
        return str(self.__dict__)

# curl '.../test?Tissue=Breast'
def filter_entries(request: HttpRequest):
    filter_values = Filter_values(**request.GET.dict())
    columns = [
        Sample.Sample,
        Sample.Tissue,
        Sample.Diagnosis,
        Sample.Date,
        Sample.File,
        Sample.Source,
        Sample.Material,
        Sample.Operator_RNA_Isolation,
        Sample.Operator_PCR,
        Sample.RNA_Concentration,
    ]

    query = session.query(Sample)
    for col in columns:
        filter_value = filter_values.__dict__[col.name]
        if filter_value:
            query = query.filter(col == filter_value)
    data: pandas.DataFrame = pandas.read_sql(query.statement, session.bind).dropna(axis=1, how="all")

    return HttpResponse(data.to_json(), content_type='application/json')

# curl '.../normalize --data '{
#   "Class" : {
#       "0": 1,
#       "1": 0,
#       "2": 1,
#       "3": 1
#   },
#   "Diagnosis": {
#     "0": "Therapy",
#     "1": "Placebo",
#     "2": "Therapy",
#     "3": "Therapy"
#   },
#   ...
# }'
#
# normalized data
def normalize(request: HttpRequest):
    raw_data: pandas.DataFrame = pandas.read_json(request.body)

    raw_data = pandas.concat([
        raw_data.pop('Class'),
        raw_data.pop('Sample'),
        raw_data.pop('Tissue'),
        raw_data.pop('Diagnosis'),
        raw_data.pop('Date'),
        raw_data.pop('File'),
        raw_data.pop('Source'),
        raw_data.pop('Material'),
        raw_data.pop('Operator_RNA_Isolation'),
        raw_data.pop('Operator_PCR'),
        raw_data.pop('RNA_Concentration'),
        raw_data
    ], axis='columns')

    start = time.process_time()
    norm_data = normalization(raw_data)
    roc_data = roc_analyze(norm_data["Class"], norm_data.iloc[:,11:])
    print(time.process_time() - start)
    return JsonResponse(roc_data, encoder=Roc_data_JSONEncoder)

def class_and_append(request: HttpRequest):
    class1_data: pandas.DataFrame = pandas.read_json.(request.body.first)
    class1_data: pandas.DataFrame = pandas.read_json(request.body.second)
    class1_data.insert(0, "Class", 1)
    class2_data.insert(0, "Class", 0)
    result_data: pandas.DataFrame = class1_data.append(class2_data)
    json_data = result_data.to_json()
    return JsonResponse(json_data)


class Roc_data_JSONEncoder(JSONEncoder):

    def default(self, obj: ROC_curve_data):
        assert isinstance(obj, ROC_curve_data)
        return {
            'fpr'       : list(obj.fpr),
            'tpr'       : list(obj.tpr),
            'threshold' : list(obj.threshold),
            'auc'       : obj.auc
        }

