import sys
import logging

from datetime import datetime
import urllib.parse

import squidutils.io

import sklearn.feature_extraction

_sample1 = '1523278970.216      1 ::1 TCP_MISS/503 4539 GET http://s-eunuc:4040/api/topology? - HIER_NONE/- text/html'
_sample2 = '1523871301.106      0 2a01:cb1d:1ba:ec00:e0a5:5723:d989:12c1 TCP_MEM_HIT/200 677 GET http://tab-live.orange.fr/live-webapp/TAB/live/tile3.xml - HIER_NONE/- application/xml'
_sample3 = '1523871148.490    270 2a01:cb1d:1ba:ec00:e0a5:5723:d989:12c1 TCP_TUNNEL/200 5556 CONNECT sso.orange.fr:443 - HIER_DIRECT/80.12.255.65 -'

_SQUID_ACCESS_LOG_LINE = _sample1

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
    ('quarter', (['q1', 'q2','q3','q4'], (map_range_to_labels, [15,30,45]))),    
    ('request_url_scheme', (['http', 'https', 'ftp'], None)),
    
    ('response_time_range', (['IMM', 'FAST', 'EVERAGE', 'LONG'], (map_range_to_labels, [500, 5000, 10000]))),
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
    
    response_time_delay_steps = [ 500, 5000, 10000 ]
    response_time_feature_value = float_to_discrete_labels (response_time_delay_steps, response_time_ms)
    log_line_model['response_time_range'] = str(response_time_feature_value)
    
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

    response_size_steps = [ 500, 5000, 10000 ]
    response_size_feature_value = float_to_discrete_labels (response_size_steps, response_size)
    log_line_model['response_size_range'] = str(response_size_feature_value)         

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
    
    #-------------
  
    for feature_value_definition in _FEATURE_VALUE_DEFINITION_LIST:
        feature, label_mapping_specification = feature_value_definition
        labels, _ = label_mapping_specification
        feature_label_list = [{feature:label} for label in labels]
        
        feature_and_value_mapping_lists.extend (feature_label_list)
        
 
        
        
        
    #-------------

    feature_and_value_mapping_lists.extend ([{'request_method':'GET'}, {'request_method':'POST'}, {'request_method':'PUT'}, {'request_method':'CONNECT'}])

    feature_and_value_mapping_lists.extend ([{'request_url_scheme':'http'}, {'request_url_scheme':'https'}, {'request_url_scheme':'ftp'}])
    
    weekday_dict_list = [{'weekday':str(weekday_number)} for weekday_number in range(0,7)]
    feature_and_value_mapping_lists.extend (weekday_dict_list)

    hour_dict_list = [{'hour':str(hour)} for hour in range(0,24)]
    feature_and_value_mapping_lists.extend (hour_dict_list)

    quarter_dict_list = [{'quarter':str(quarter)} for quarter in range(0,4)]
    feature_and_value_mapping_lists.extend (quarter_dict_list)
    
    return feature_and_value_mapping_lists
    
#=======================================================

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

#
# build model mapper
#

squid_model_mapping = get_model_mapping_for_vectorizer()

# dense version

squid_log_to_dense_vector_mapper = sklearn.feature_extraction.DictVectorizer(sparse=False, sort=False)
squid_log_to_dense_vector_mapper.fit (squid_model_mapping)

# sparse version
squid_log_to_sparse_vector_mapper = sklearn.feature_extraction.DictVectorizer(sparse=True, sort=False)
squid_log_to_sparse_vector_mapper.fit (squid_model_mapping)

# test
encoded_features = squid_log_to_dense_vector_mapper.get_feature_names()

#
# analyze input log line
#


log_line_fields = squidutils.io.getLogLineFields (_SQUID_ACCESS_LOG_LINE)
sample = squid_log_line_to_model (log_line_fields)

#
# map to vector
#

dense_vector_sample = squid_log_to_dense_vector_mapper.transform (sample)
sparse_vector_sample = squid_log_to_sparse_vector_mapper.transform (sample)

sys.exit(1)


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
