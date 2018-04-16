import sys
import logging

from datetime import datetime
import urllib.parse

import squidutils.io

import sklearn.feature_extraction

_SQUID_ACCESS_LOG_LINE = '1523278970.216      1 ::1 TCP_MISS/503 4539 GET http://s-eunuc:4040/api/topology? - HIER_NONE/- text/html'

_ORDERED_HTTP_METHODS_LIST = [
    'GET',
    'HEAD',
    'POST',
    'PUT',
    'DELETE',
    'CONNECT',
    'OPTIONS',
    'TRACE'
]





def getValueStepIndex (step_list, v):
    
    step_index = 0
    for step in step_list:
        if v < step:
            break
        else:
            step_index += 1
            
    return step_index
    
    

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
    #!!! req_timestamp = time.gmtime (f)
    req_datetime = datetime.fromtimestamp (f)
    
    weekday = req_datetime.isoweekday()
    hour = req_datetime.hour
    minute = req_datetime.minute
    
    hourly_quarter = getValueStepIndex ([15, 30, 45], minute)
    
    log_line_model['weekday'] = str(weekday)
    log_line_model['hour'] = str(hour)
    log_line_model['quarter'] = str(hourly_quarter)
    
    #==============
    #
    # tr => discrete values
    #
    #==============
    
    response_time_string = req_time_string = log_line_dict['tr']
    response_time_ms = int(response_time_string)
    
    response_time_delay_steps = [ 500, 5000, 10000 ]
    response_time_feature_value = getValueStepIndex (response_time_delay_steps, response_time_ms)
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
    response_size_feature_value = getValueStepIndex (response_size_steps, response_size)
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
    
    feature_and_value_mapping_lists = []

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

squid_log_to_dense_vector_mapper = sklearn.feature_extraction.DictVectorizer(sparse=False, sort=False)
squid_log_to_sparse_vector_mapper = sklearn.feature_extraction.DictVectorizer(sparse=True, sort=False)

squid_log_to_dense_vector_mapper.fit (squid_model_mapping)
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

dense_vector_sample = squid_log_to_sparse_vector_mapper.transform (sample)
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
