import sys
from datetime import datetime
import urllib.parse

import squidutils.io

from sklearn.feature_extraction import DictVectorizer

squid_access_log_line = '1523278970.216      1 ::1 TCP_MISS/503 4539 GET http://s-eunuc:4040/api/topology? - HIER_NONE/- text/html'

orderedHttpMethodsList = [
    'GET',
    'HEAD',
    'POST',
    'PUT',
    'DELETE',
    'CONNECT',
    'OPTIONS',
    'TRACE'
]



tt = squidutils.io.parseLogLine (squid_access_log_line)

def getValueStepIndex (step_list, v):
    
    step_index = 0
    for step in step_list:
        if v < step:
            break
        else:
            step_index += 1
            
    return step_index
    
    

def logLineDictToFeatures (log_line_dict):
    
    feature_dict = {}
    
    # ts.tu => day + time slot
    
    req_time_string = log_line_dict['ts.tu']
    f = float (req_time_string)
    #!!! req_timestamp = time.gmtime (f)
    req_datetime = datetime.fromtimestamp (f)
    
    weekday = req_datetime.isoweekday()
    hour = req_datetime.hour
    minute = req_datetime.minute
    
    hourly_quarter = getValueStepIndex ([15, 30, 45], minute)
    
    feature_dict['weekday'] = str(weekday)
    feature_dict['hour'] = str(hour)
    feature_dict['quarter'] = str(hourly_quarter)
    
    #--------
    
    response_time_string = req_time_string = log_line_dict['tr']
    response_time_ms = int(response_time_string)
    
    response_time_delay_steps = [ 500, 5000, 10000 ]
    response_time_feature_value = getValueStepIndex (response_time_delay_steps, response_time_ms)
    feature_dict['response_time_range'] = str(response_time_feature_value)
    
    #--------
    
    feature_dict['client_ip_source'] = log_line_dict['>a']

    #--------
    
    request_status = log_line_dict['Ss/Hs']
    squit_request_status, http_status_code = request_status.split('/')
    
    feature_dict['http_status_code'] = http_status_code
    
    #--------
    
    response_size_string = log_line_dict['<st']
    response_size= int(response_size_string)

    response_size_steps = [ 500, 5000, 10000 ]
    response_size_feature_value = getValueStepIndex (response_size_steps, response_size)
    feature_dict['response_size_range'] = str(response_size_feature_value)         

    #--------
    
    request_method = log_line_dict['rm']    
    feature_dict['request_method'] = request_method
    
    #--------
    
    request_url = log_line_dict['ru']
    
    url = urllib.parse.urlparse (request_url,scheme='http')
    
    feature_dict['request_url_scheme'] = url.scheme
    feature_dict['request_url_hostname_len'] = len(url.hostname)
    feature_dict['request_url_port'] = url.port
    feature_dict['request_url_path_len'] = len(url.path)
    
    #--------
    
    user_name = log_line_dict['[un']
    
    #--------     
    
    _ = log_line_dict['Sh/<a'] 

    #--------
     
    mime_content_type = log_line_dict['mt']
    feature_dict['request_mime_content_type'] = mime_content_type
        
    return feature_dict
    
zz = logLineDictToFeatures (tt)

#=======================================================

v_dense = DictVectorizer(sparse=False, sort=False)
v_sparse = DictVectorizer(sparse=True, sort=False)

feature_index_lists = []

feature_index_lists.extend ([{'request_method':'GET'}, {'request_method':'POST'}, {'request_method':'PUT'}, {'request_method':'CONNECT'}])

feature_index_lists.extend ([{'request_url_scheme':'http'}, {'request_url_scheme':'https'}, {'request_url_scheme':'ftp'}])

weekday_dict_list = [{'weekday':str(weekday_number)} for weekday_number in range(0,7)]
feature_index_lists.extend (weekday_dict_list)

hour_dict_list = [{'hour':str(hour)} for hour in range(0,24)]
feature_index_lists.extend (hour_dict_list)

quarter_dict_list = [{'quarter':str(quarter)} for quarter in range(0,4)]
feature_index_lists.extend (quarter_dict_list)

v_dense.fit (feature_index_lists)
encoded_features = v_dense.get_feature_names()

dense_sample = v_dense.transform (zz)

sys.exit(1)


predefined_feature_list = ['toto', 'foo', 'tt', 'bar', 'baz' ]
feature_index_dict1 = { l:None for l in predefined_feature_list}

#feature_index_dict1 = {'toto':0, 'foo':0, 'tt':0, 'bar':0, 'baz':0 }
#feature_index_dict1 = {'toto':None, 'baz':None}
feature_index_lists = [feature_index_dict1]

v_dense.fit (feature_index_lists)
v_sparse.fit (feature_index_lists)


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
