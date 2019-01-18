import sys

import pandas as pd
import sklearn.feature_extraction
import sklearn.datasets

import csv

from datetime import datetime

df = pd.read_csv('samples/input_test/csv2libsvm_example.csv', header=1, sep=',', 
                 names=['labels', 'f1', 'f2', 'f3'])   # columns names if no header
# df = pd.read_csv('samples/input_test/csv2libsvm_example.csv', header='infer', sep=',', verbose=True)

X_df = df.loc[:, 'f1':'f3']
y_df = df[['labels']]

fd = open('samples/input_test/csv2libsvm_example.csv')
input_file_csv_reader = csv.DictReader(fd)
matrix_as_dict_list = []
for row in input_file_csv_reader:
    striped_row = {fieldname.strip('\t'): value.strip('\t') for (fieldname, value) in row.items()}
    matrix_as_dict_list.append(striped_row)


feature_vectorizer = sklearn.feature_extraction.DictVectorizer(sparse=False, sort=False)
feature_mapper = feature_vectorizer.fit ([{'f1':0}, {'f1':1}, {'f2':0}, {'f2':1}, {'f3':0}, {'f3':1}])
                                          
label_vectorizer = sklearn.feature_extraction.DictVectorizer(sparse=False, sort=False)
label_mapper = label_vectorizer.fit ([{'label':0}, {'label':1}, {'label':2}])

matrix_as_dict_list = X_df.to_dict('records')
X = feature_mapper.transform (matrix_as_dict_list)

y_df_as_dict_list = y_df.to_dict('records')
y_matrix = label_mapper.transform(y_df_as_dict_list)
y = y_matrix[:,0]

with open ('samples/tmp/csv2libsvm_out.txt', 'wb') as libSVMFile:
    
    now = datetime.now()
    hr_now = now.strftime("%A %d/%m/%Y %Hh%M")    
    
    sklearn.datasets.dump_svmlight_file(X=X, y=y, f=libSVMFile, zero_based=True, comment='Generated at: {}'.format (hr_now), query_id=None, multilabel=False)
         


sys.exit(0)


