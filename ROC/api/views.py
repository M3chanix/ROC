from django.http import HttpResponse, HttpRequest, JsonResponse

from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas

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
