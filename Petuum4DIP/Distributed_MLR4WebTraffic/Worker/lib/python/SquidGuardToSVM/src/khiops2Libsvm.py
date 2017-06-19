#! /usr/bin/env python3

# coding: utf-8 

# TdB
import os
import sys
import hashlib

import argparse

import unittest

import logging
logging.basicConfig (level=logging.WARNING)

'''
The dictionary representing a libsvm_file will have (eventually) the following keys:

    [meta] = {
        [num_train_total]=3
        [num_train_this_partition]=3
        [feature_dim]=3
        [num_labels]=5
        [format]=libsvm
        [feature_one_based]=0
        [label_one_based]=0
        [snappy_compressed]=0
    }
    [matrix] = {
    
        [label_0]={ [feature_0]:value_0, [feature_1]:value_1 ...}
    }
    
    [vectors] = [
        # tuple (label, feature vector)
        # label is None if not provided
         
        (label, { [feature_0]:value_0, [feature_1]:value_1 ...})
    ]

'''

_feature_names_list = []

_feature_table = {}
_last_allocated_feature_index = 0

_label_name_to_index_table = {}
_last_allocated_label_index = 0

_input_data_libsvm_representation = []

def feature_name_and_value_to_index (feature_name, feature_string_value):
    global _feature_table
    global _last_allocated_feature_index
    
    if not feature_name in _feature_table:
        _feature_table[feature_name] = {}
    
    possible_feature_values_table = _feature_table[feature_name]
    
    if not feature_string_value in possible_feature_values_table:
        possible_feature_values_table[feature_string_value] = _last_allocated_feature_index
        _last_allocated_feature_index += 1
        
        
    feature_index = possible_feature_values_table[feature_string_value]
    return feature_index
        
    
    
def label_value_name_to_zero_one (label_name):
    global _label_name_to_index_table
    
    
def add_khiops_data_line_to_libsvm_representation (khiops_data_line):
    
    global _input_data_libsvm_representation
    
    khiops_data_line_as_list = khiops_data_line.split()
    label_value = khiops_data_line_as_list[0]
    
    features_values = []
    for (feature_name, feature_value) in zip(feature_names_list, khiops_data_line_as_list[1:]):
        feature_value_index = feature_name_and_value_to_index (feature_name, feature_value)
        features_values[feature_value_index] = 1
        
         _input_data_libsvm_representation['vectors'].app
        

def khiopsFile2LibSvmFile (khiops_file_name, libsvm_file_name_prefix):
    
    global _input_data_libsvm_representation
    

    _input_data_libsvm_representation = {
        'meta' : {
            ['feature_one_based'] : 0,
            ['label_one_based'] : 0
        },
        'matrix' : {}                       
    }
    
    with open (khiops_file_name, 'r') as khiops_file:
        
        header_line = khiops_file.readline()
        headers_as_list = features_line.split()
        
        _feature_names_list = headers_as_list[1:]
        
        while True:
            
            line = khiops_file.readline()
            if not line:
                break
            line = cleanup_string_read_from_file(line)
            
            # TODO: we assume that the current line is labeled
            # This is only the case when this we this is a training line 
            content = labeled_libsvm_vector_to_label_and_sparse_vector (line)
            file_content_list.append (content)
        
    return (file_content_list)    


#
# TEST CASES
# ==========

class moduleTestCases (unittest.TestCase):
    
    def test1 (self):
    
        index = feature_name_and_value_to_index ('CapShape', 'CONVEX')
        self.assertEqual(index, 0)
        
        index = feature_name_and_value_to_index ('CapShape', 'FLAT')
        self.assertEqual(index, 1)
        
        index = feature_name_and_value_to_index ('CapSurface', 'SMOOTH')
        self.assertEqual(index, 2)        
        
    def test2 (self):
    
        index = feature_name_and_value_to_index ('CapShape', 'CONVEX')
        self.assertEqual(index, 0)
        
    def test3 (self):
    
        index = feature_name_and_value_to_index ('CapSurface', 'SMOOTH')
        self.assertEqual(index, 2)             


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
        
    if args.debug:
        logging.getLogger().setLevel (logging.DEBUG)
    

    buildCategoryTable (args.squidGuardConfigurationFile)
    dumpCategoryTable (args.categoriesDumpFile)
    
    squidAccessLogFileName = args.squidAccessLogFile
    squidGuardFileName = args.squidGuardFile
    libSVMFileName = args.libSVMFile
    squidGuardOutputFileToLibSVMInputFile (squidGuardFileName, squidAccessLogFileName, libSVMFileName)

if __name__ == '__main__':
    pass