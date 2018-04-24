#! /usr/bin/env python3

# coding: utf-8

import sys
import logging
logging.basicConfig (level=logging.WARNING)
import unittest

import argparse

import numpy


from datetime import datetime
import urllib.parse

import squidutils.io

import sklearn.feature_extraction
import sklearn.datasets
import sklearn.preprocessing



def map_range_to_labels (value, range_list, label_mapping):
    
    step_index = 0
    for step_value in range_list:
        if value < step_value:
            break
        else:
            step_index += 1
            
    label = label_mapping[step_index]
    
    return label


# Format:
# [   => list of order features
#    (   => tuple of
#       feature name
#       (  => tuple of
#          ( list of possible labels )
#          (  => tuple of
#             value to label mapping function
#             mapping function argument
#          )
#       )
#    )
# ]

_FEATURE_VALUE_DEFINITION_LIST = [
    ('request_method', (['GET', 'POST', 'PUT', 'CONNECT'], None)),

    ('request_url_scheme', (['http', 'https', 'ftp'], None)),
    
    ('response_time_range', (['IMM', 'FAST', 'MEDIUM', 'LONG'], (map_range_to_labels, [500, 5000, 10000]))),
    
    ('response_size_range', (['EPSILON', 'SMALL', 'MEDIUM', 'LARGE'], (map_range_to_labels, [500, 5000, 10000]))),
    
    ('weekday', ([str(v) for v in range(0,7)], None)),
    ('hour', ([str(v) for v in range(0,24)], None)),    
    ('quarter', (['q1', 'q2','q3','q4'], (map_range_to_labels, [15,30,45]))),
    
]


def get_feature_specification (feature):
    
    global _FEATURE_VALUE_DEFINITION_LIST
    
    # get all matching
    list_of_found_label_sets = [ l for (f, l) in _FEATURE_VALUE_DEFINITION_LIST if f == feature ]
    
    if len(list_of_found_label_sets) == 1:
        return list_of_found_label_sets[0]
    else:
        # nothing or too much found
        # return empty list
        return []

def get_labels_for_feature (feature):
    
    feature_specification = get_feature_specification (feature)
    
    label_list, _  = feature_specification
    return label_list

    
def get_mapping_specification_for_feature_definition (feature):
    
    feature_specification = get_feature_specification (feature)    
 
 
    _, mapping_specification  = feature_specification
    return mapping_specification

def input_value_to_model_value (input_value, feature):
    
    model_value = None
    
    mapping_specification = get_mapping_specification_for_feature_definition (feature)
    
    if mapping_specification:
        
        mapping_function, mapping_function_range_arg = mapping_specification
        label_list = get_labels_for_feature (feature)
        mapped_value = mapping_function (value=input_value, range_list=mapping_function_range_arg, label_mapping=label_list)
        
        model_value = mapped_value
    else:
        model_value = input_value
        
    return model_value
        
        
        

    
    

def squid_log_line_to_model (log_line_dict):
    """ Constructs a model from the log line represented as a dict
    
    The model contains all input fields, mapped to values acceptable by the model
    """
    
    log_line_model = {}
    
    #==============
    #
    # ts.tu => day + time slot
    #
    #==============
    
    req_time_string = log_line_dict['ts.tu']
    f = float (req_time_string)
    req_datetime = datetime.fromtimestamp (f)
    
    weekday = req_datetime.isoweekday()
    hour = req_datetime.hour
    minute = req_datetime.minute
    
    log_line_model['weekday'] = str(weekday)
    log_line_model['hour'] = str(hour)
    log_line_model['quarter'] = input_value_to_model_value (minute, 'quarter')
    
    #==============
    #
    # tr => discrete values
    #
    #==============
    
    response_time_string = req_time_string = log_line_dict['tr']
    response_time_ms = int(response_time_string)
    log_line_model['response_time_range'] = input_value_to_model_value (response_time_ms, 'response_time_range')
    
    #==============
    #
    # >a
    #
    #==============
    
    log_line_model['client_ip_source'] = log_line_dict['>a']

    #==============
    #
    # Ss/Hs
    #
    #==============
    
    request_status = log_line_dict['Ss/Hs']
    squit_request_status, http_status_code = request_status.split('/')
    
    log_line_model['http_status_code'] = http_status_code
    
    #==============
    #
    # <st
    #
    #==============
    
    response_size_string = log_line_dict['<st']
    response_size= int(response_size_string)

    log_line_model['response_size_range'] = input_value_to_model_value (response_size, 'response_size_range')         

    #==============
    #
    # rm
    #
    #==============
    
    request_method = log_line_dict['rm']    
    log_line_model['request_method'] = request_method
    
    #==============
    #
    # ru
    #
    #==============
    
    request_url = log_line_dict['ru']
    
    url = urllib.parse.urlparse (request_url,scheme='http')
    
    log_line_model['request_url_scheme'] = url.scheme
    log_line_model['request_url_hostname_len'] = len(url.hostname)
    log_line_model['request_url_port'] = url.port
    log_line_model['request_url_path_len'] = len(url.path)
    
    #==============
    #
    # [un
    #
    #==============
    
    user_name = log_line_dict['[un']
    
    #==============
    #
    # Sh/<a
    #
    #==============
    
    _ = log_line_dict['Sh/<a'] 

    #==============
    #
    # mt
    #
    #==============
     
    mime_content_type = log_line_dict['mt']
    log_line_model['request_mime_content_type'] = mime_content_type
    
    #==============
        
    return log_line_model



def get_model_mapping_for_vectorizer ():
    
    global _FEATURE_VALUE_DEFINITION_LIST
    
    feature_and_value_mapping_lists = []
    
    for feature_value_definition in _FEATURE_VALUE_DEFINITION_LIST:
        feature, label_mapping_specification = feature_value_definition
        labels, _ = label_mapping_specification
        feature_label_list = [{feature:label} for label in labels]
        
        feature_and_value_mapping_lists.extend (feature_label_list)
        
    return feature_and_value_mapping_lists
    
#=======================================================

def init_model_mapper (dense=True):
    
    model_mapper = None
    
    #
    # build model mapper
    #
    
    squid_model_mapping = get_model_mapping_for_vectorizer()
    
    if dense:
    
        # dense version
        
        squid_log_to_dense_vector_mapper = sklearn.feature_extraction.DictVectorizer(sparse=False, sort=False)
        squid_log_to_dense_vector_mapper.fit (squid_model_mapping)
        
        model_mapper = squid_log_to_dense_vector_mapper
    else:
    
        # sparse version
        squid_log_to_sparse_vector_mapper = sklearn.feature_extraction.DictVectorizer(sparse=True, sort=False)
        squid_log_to_sparse_vector_mapper.fit (squid_model_mapping)
        
        model_mapper = squid_log_to_sparse_vector_mapper
    
    return model_mapper 

def main():
    
    
    squid_log_to_vector_mapper = init_model_mapper(dense=True)
    
    #
    # analyze input log line
    #
    _sample1 = '1523278970.216      1 ::1 TCP_MISS/503 4539 GET http://s-eunuc:4040/api/topology? - HIER_NONE/- text/html'
    
    
    
    log_line_field_list = squidutils.io.getLogLineFields (_sample1)
    cleared_log_line = squid_log_line_to_model (log_line_field_list)    
    
    #
    # map to vector
    #
    
    logline_as_matrix = squid_log_to_vector_mapper.transform(cleared_log_line)
    
    #
    # dump to svmlight format
    #
    

    
    l1 = [1, 2, 3, 4, 5]
    l2 = [2, 3, 4, 5, 5]
    l3 = [1, 4, 3, 2, 1]

    Xm = numpy.array([l1, l2, l3])
    
    X = Xm[:, 2:]
    y = Xm[:, :2]    
    
    sklearn.datasets.dump_svmlight_file(X, y, f="toto.txt", zero_based=True, comment="Comment for test", query_id=None, multilabel=True)
    
    
    le = sklearn.preprocessing.LabelEncoder()
    le.fit(["paris", "paris", "tokyo", "amsterdam"])
    list(le.classes_)
    le.transform(["tokyo", "tokyo", "paris"])
    zz = le.inverse_transform([2, 2, 1])
    
    
    sys.exit(1)
    # NOT REACHED
    
    parser = argparse.ArgumentParser(description='Generates a LIB SVM formated file for Squid Access Logs which have been labeled by squidGuard.')
    parser.add_argument("-s", "--squidAccessLogFile", metavar='<squid access log>', type=str, dest="squidAccessLogFile", required=True, 
                        help='The Squid access log file.')
    parser.add_argument("-g", "--squidGuardFile", metavar='<squidGuard out>', type=str, dest="squidGuardFile", required=True,
                        help='The resulting file after applying squidGuard to <squid access log>.')
    parser.add_argument("-p", "--libSVMFile", metavar='<libsvm for Petuum MLR>', type=str, dest="libSVMFile", required=True,
                        help='''The resulting "LIB SVM" formated file, containing the classified content.
    The additional file with "<libSVMFile>.meta" suffix is generated, which contains the information required by Petuum's MLR algorithm.
    These 2 files can be used as input to Petuum's MRL''')
    parser.add_argument("-c", "--squidGuardConf", metavar='<squidGuard configuration file>', type=str, dest="squidGuardConfigurationFile", required=True,
                        help='The squidGuard configuration file used to generate <squidGuard out>.')
    parser.add_argument("-k", "--categoriesDump", metavar='<category dump file>', type=str, dest="categoriesDumpFile", required=True,
                        help='Generated file, containing the list of all matched categories with their LibSVM index. Each category index is considered as a LibSVM label.')
    parser.add_argument("--featureOneBased", action='store_true', dest="featureOneBased", 
                        help='If true, feature indexes start at "1", "0" else (default is false => first feature index is "0"')
    parser.add_argument("--labelOneBased", action='store_true', dest="labelOneBased",
                        help='If true, labels indexes start at "1", "0" else (default is false => first label index is "0"')
    parser.add_argument("-d", "--debug", action='store_true', dest="debug")
    
    args = parser.parse_args()
    
    if args.featureOneBased:
        _feature_one_based = True
    else:
        _feature_one_based = False
        
    if args.labelOneBased:
        _label_one_based = True
    else:
        _label_one_based = False    




#
# TEST CASES
# ==========

class moduleTestCases (unittest.TestCase):
    
    _sample1 = '1523278970.216      1 ::1 TCP_MISS/503 4539 GET http://s-eunuc:4040/api/topology? - HIER_NONE/- text/html'
    _sample2 = '1523871301.106      0 2a01:cb1d:1ba:ec00:e0a5:5723:d989:12c1 TCP_MEM_HIT/200 677 GET http://tab-live.orange.fr/live-webapp/TAB/live/tile3.xml - HIER_NONE/- application/xml'
    _sample3 = '1523871148.490    270 2a01:cb1d:1ba:ec00:e0a5:5723:d989:12c1 TCP_TUNNEL/200 5556 CONNECT sso.orange.fr:443 - HIER_DIRECT/80.12.255.65 -'

    def test_model_initialization (self):
        
        expected_test_result = ['request_method=GET', 'request_method=POST', 'request_method=PUT', 'request_method=CONNECT', 'request_url_scheme=http', 'request_url_scheme=https', 'request_url_scheme=ftp', 'response_time_range=IMM', 'response_time_range=FAST', 'response_time_range=MEDIUM', 'response_time_range=LONG', 'response_size_range=EPSILON', 'response_size_range=SMALL', 'response_size_range=MEDIUM', 'response_size_range=LARGE', 'weekday=0', 'weekday=1', 'weekday=2', 'weekday=3', 'weekday=4', 'weekday=5', 'weekday=6', 'hour=0', 'hour=1', 'hour=2', 'hour=3', 'hour=4', 'hour=5', 'hour=6', 'hour=7', 'hour=8', 'hour=9', 'hour=10', 'hour=11', 'hour=12', 'hour=13', 'hour=14', 'hour=15', 'hour=16', 'hour=17', 'hour=18', 'hour=19', 'hour=20', 'hour=21', 'hour=22', 'hour=23', 'quarter=q1', 'quarter=q2', 'quarter=q3', 'quarter=q4']

        model_mapper = init_model_mapper(dense=True)
 
        test_result = model_mapper.get_feature_names()        
        self.assertEqual(expected_test_result, test_result)
        
        model_mapper = init_model_mapper(dense=False)
 
        test_result = model_mapper.get_feature_names()
        self.assertEqual(expected_test_result, test_result)
        
    def test_dense_matrix_generation (self):
        
        sample = self._sample1
        
        expected_test_result = numpy.array([[1., 0., 0., 0., 1., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0.,
        1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.,
        0., 0.]])
        
        model_mapper = init_model_mapper(dense=True)
        
        log_line_field_list = squidutils.io.getLogLineFields (sample)
        cleared_log_line = squid_log_line_to_model (log_line_field_list) 
        
        test_result = model_mapper.transform (cleared_log_line)
        numpy.testing.assert_array_equal(expected_test_result, test_result, verbose=True)
        
    def test_sparse_matrix_generation (self):
        
        sample = self._sample1
        
        expected_test_result_as_dense_matrix = numpy.array([[1., 0., 0., 0., 1., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0.,
        1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.,
        0., 0.]])
        
        model_mapper = init_model_mapper(dense=False)
        
        log_line_field_list = squidutils.io.getLogLineFields (sample)
        cleared_log_line = squid_log_line_to_model (log_line_field_list) 
        
        test_result_sparse = model_mapper.transform (cleared_log_line)
        test_result = test_result_sparse.toarray()
        numpy.testing.assert_array_equal(expected_test_result_as_dense_matrix, test_result, verbose=True)        
          

#
# MAIN
# ====
#


if __name__ == '__main__':
    main()
    
################################################################################################

#
# TRASH
#


def _code_to_remove ():

    predefined_feature_list = ['toto', 'foo', 'tt', 'bar', 'baz' ]
    feature_index_dict1 = { l:None for l in predefined_feature_list}
    
    #feature_index_dict1 = {'toto':0, 'foo':0, 'tt':0, 'bar':0, 'baz':0 }
    #feature_index_dict1 = {'toto':None, 'baz':None}
    feature_and_value_mapping_lists = [feature_index_dict1]
    
    v_dense.fit (feature_and_value_mapping_lists)
    v_sparse.fit (feature_and_value_mapping_lists)
    
    
    samples = [{'foo': 1, 'bar': 2}, {'foo': 3, 'baz': 4}]
    
    samples = [{'bar': 3}, {'baz':4, 'foo':7}]
    
    X2_dense = v_dense.transform(samples)
    #X1_dense = v_dense.fit_transform(samples)
    
    X2_sparse = v_sparse.transform(samples)
    #X1_sparse = v_sparse.fit_transform(samples)
    
    
    
    
    pass
    
    F_dense = v_dense.get_feature_names()
    F_sparse = v_sparse.get_feature_names()
    
    ZZ = v_dense.get_params()
    
    pass



