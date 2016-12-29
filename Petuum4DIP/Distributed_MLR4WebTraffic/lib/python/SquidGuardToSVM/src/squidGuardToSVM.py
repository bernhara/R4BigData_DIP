# TdB
import os
import sys
import hashlib

import argparse
from xml.sax.handler import feature_external_ges

#
# Globals
#

_squidGuardCategories = []
_feature_one_based = False
_label_one_based = False

def hashStringToLibSVMValue (string_to_encode):
    
    string_to_encode_utf8 = string_to_encode.encode('utf8')
    md5_holder = hashlib.md5(string_to_encode_utf8)
    md5_hash_value_byte_array = md5_holder.digest()
    
    md5_hash_value_converted_to_decimals = ''.join ('{0:03d}'.format (single_byte) for single_byte in md5_hash_value_byte_array)
    
    md5_hash_as_float_string = '0.' + md5_hash_value_converted_to_decimals
    
    return (md5_hash_as_float_string)
    
   


def buildCategoryTable (squidGuardConfigurationFileName):
    
    global _squidGuardCategories
    
    # 'none' is a predefined category
    _squidGuardCategories = ['none']
        
    with open (squidGuardConfigurationFileName) as squidGuardConfigurationFile:
        for line in squidGuardConfigurationFile:
            splitted_line = line.split(maxsplit=3)
            if len (splitted_line) == 3:
                if splitted_line[0] == 'dest':
                    category = splitted_line[1]
                    _squidGuardCategories.append(category)
                    
                    
def dumpCategoryTable (categoriesDumpFileName):
    
    global _squidGuardCategories
    global _label_one_based
    
    if _label_one_based:
        startIndex = 1
    else:
        startIndex = 0
    
    with open (categoriesDumpFileName, 'w') as categoriesDumpFile:
        
        for indexed_category in enumerate (_squidGuardCategories, start=startIndex):
            print ('{} {}'.format(indexed_category[0], indexed_category[1]), file = categoriesDumpFile)
  


httpMethodsList = [
    'GET',
    'HEAD',
    'POST',
    'PUT',
    'DELETE',
    'CONNECT',
    'OPTIONS',
    'TRACE'
]

def read_libsvm_file(data_file_name):
    """
    svm_read_problem(data_file_name) -> [y, x]

    Read LIBSVM-format data from data_file_name and return labels y
    and data instances x.
    """
    prob_y = []
    prob_x = []
    for line in open(data_file_name):
        line = line.split(None, 1)
        # In case an instance with all zero features
        if len(line) == 1: line += ['']
        label, features = line
        xi = {}
        for e in features.split():
            ind, val = e.split(":")
            xi[int(ind)] = float(val)
        prob_y += [float(label)]
        prob_x += [xi]
    return (prob_y, prob_x)

_access_log_field_names = [
    'time',
    'delay',
    'source_host',
    'squid_cache_result',
    'what1',
    'http_method',
    'full_url',
    'what2',
    'destination_method_and_host',
    'mime_type'
]

def analyzeSingleLogLine (squidguardLine, squidAccesLogLine):
    
    web_request_analysis_dict = {}

    # analyse squidGuard input line
    squidguard_tags_for_web_request = squidguardLine.split('&')

    for squidguard_tag in squidguard_tags_for_web_request:
        tag_name_and_value_list = squidguard_tag.split ('=', maxsplit=1)
        tag_name_and_value_tuple = tuple (tag_name_and_value_list)
        tag_name, tag_value = tag_name_and_value_tuple
        web_request_analysis_dict[tag_name] = tag_value
    
    # analyse squidAccesslog input line
    squid_access_log_field_list = squidAccesLogLine.split()
    squid_access_log_field_list_len = len(squid_access_log_field_list)
    
    for index in range (squid_access_log_field_list_len):
        field_name = _access_log_field_names[index]
        field_value = squid_access_log_field_list[index]
        web_request_analysis_dict[field_name] = field_value
        
    return web_request_analysis_dict

def webRequestToLibSVMLine (web_request_analysis_dict):
    
    global _feature_on_based
    global _label_one_based    
    
    print ('squidGuard group: {}'.format(web_request_analysis_dict['targetgroup']))
    
    # How the resulting line will be formated
    if _feature_one_based:
        first_feature_index = 1
    else:
        first_feature_index = 0
    
    # the squidGuard computed category(ie. label) index
    _libSvmFormat = '{label_index:2d}'
    
    feature_index = first_feature_index
    
    _libSvmFormat += ' ' + str(feature_index) + ':{GET}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{HEAD}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{POST}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{PUT}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{DELETE}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{CONNECT}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{OPTIONS}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{TRACE}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{full_url}'; feature_index += 1
    _libSvmFormat += ' ' + str(feature_index) + ':{source_host}'; feature_index += 1
    
    libSVMLineData = {}
    
    # the label
    category = web_request_analysis_dict['targetgroup']
    # get a "0 based" category index
    category_index = _squidGuardCategories.index(category)
    if _label_one_based:
        libSVMLineData['label_index'] = category_index + 1
    else:
        libSVMLineData['label_index'] = category_index
    
    # features
    
    # ... HTTP method
    http_method_used_in_request = web_request_analysis_dict['http_method']
    for m in httpMethodsList:
        if http_method_used_in_request == m:
            libSVMLineData[m] = 1
        else:
            libSVMLineData[m] = 0
     
    # ... URL
    url_in_request = web_request_analysis_dict['full_url']
    libsvm_encoded_url = hashStringToLibSVMValue(url_in_request)
    libSVMLineData['full_url'] = libsvm_encoded_url
    
    # ... source_host
    source_host_in_request = web_request_analysis_dict['source_host']
    libsvm_encoded_source_host = hashStringToLibSVMValue(source_host_in_request)
    libSVMLineData['source_host'] = libsvm_encoded_source_host    
    
    libsvm_formated_line = _libSvmFormat.format(**libSVMLineData)
    return (libsvm_formated_line)
                
          
def squidGuardOutputFileToLibSVMInputFile (squidGuardFileName, squidAccessLogFileName, libSVMFileName):
    
    global _feature_on_based
    global _label_one_based
    
    input_file_line_numbers = 0
    
    # load
    with open (squidGuardFileName) as squidGuardOuputFile:
        with open (squidAccessLogFileName) as squidAccessLogFile:
            with open (libSVMFileName, 'w') as libSVMFile:
                while True:
                                
                    squidguardLine = squidGuardOuputFile.readline()
                    if not squidguardLine:
                        break
                    
                    input_file_line_numbers += 1
                    squidAccesLogLine = squidAccessLogFile.readline()
                    
                    web_request_analysis_dict = analyzeSingleLogLine (squidguardLine, squidAccesLogLine)
                    
                    print (web_request_analysis_dict)
                    libsvm_formated_line = webRequestToLibSVMLine (web_request_analysis_dict)
                    print (libsvm_formated_line)
                    print (libsvm_formated_line, file=libSVMFile)
    
    # generate "meta" file        
    libSVMMetaFileName = libSVMFileName + '.meta'
    
    num_train_total = input_file_line_numbers
    # TODO: test with one worker, input file not split
    num_train_this_partition = num_train_total
    # FIXME: test file size is currently not computed
    num_test = 1
    # TODO: should not be here
    feature_dim = 11
    num_labels = len (_squidGuardCategories)
    
    if _feature_one_based:
        feature_one_based = 1
    else:
        feature_one_based = 0
    
    if _label_one_based:
        label_one_based = 1
    else:
        label_one_based = 0
          
    snappy_compressed = 0
    
    with open (libSVMMetaFileName, 'w') as libSVMMetaFile:
        print ('num_train_total: {}'.format (num_train_total), file=libSVMMetaFile)
        print ('num_train_this_partition: {}'.format (num_train_this_partition), file=libSVMMetaFile)
        print ('feature_dim: {}'.format (feature_dim), file=libSVMMetaFile)
        print ('num_labels: {}'.format (num_labels), file=libSVMMetaFile)
        print ('format: libsvm', file=libSVMMetaFile)
        print ('feature_one_based: {}'.format (feature_one_based), file=libSVMMetaFile)        
        print ('label_one_based: {}'.format (label_one_based), file=libSVMMetaFile)
        print ('snappy_compressed: {}'.format (snappy_compressed), file=libSVMMetaFile)
        
# TEST META INFO
# num_test: 50
# feature_dim: 54
# num_labels: 7
# format: libsvm
# feature_one_based: 1
# label_one_based: 1
# snappy_compressed: 0

# TRAIN META INFO
# num_train_total: 500
# num_train_this_partition: 500
# feature_dim: 54
# num_labels: 7
# format: libsvm
# feature_one_based: 1
# label_one_based: 1
# snappy_compressed: 0
        
                                       


def main():
    
    global _feature_one_based
    global _label_one_based
    
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
    
    args = parser.parse_args()
    
    if args.featureOneBased:
        _feature_one_based = True
    else:
        _feature_one_based = False
        
    if args.labelOneBased:
        _label_one_based = True
    else:
        _label_one_based = False    
    

    buildCategoryTable (args.squidGuardConfigurationFile)
    dumpCategoryTable (args.categoriesDumpFile)
    
    squidAccessLogFileName = args.squidAccessLogFile
    squidGuardFileName = args.squidGuardFile
    libSVMFileName = args.libSVMFile
    squidGuardOutputFileToLibSVMInputFile (squidGuardFileName, squidAccessLogFileName, libSVMFileName)

if __name__ == '__main__':
    main()