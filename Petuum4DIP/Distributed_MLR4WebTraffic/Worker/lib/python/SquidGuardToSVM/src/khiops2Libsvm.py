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



class LabelToIndexConverter:
    
    def __init__(self):
        self._last_allocated_label_index = 0
        self._label_classes = {}
        
    def getIndex (self, label_class, label_name):
        
        # if it is the first time we see this class, init a new table for this class
        if not label_class in self._label_classes:
            self._label_classes[label_class] = {}
            
        if not label_name in self._label_classes[label_class]:
            self._label_classes[label_class][label_name] = self._last_allocated_feature_index
            self._last_allocated_feature_index += 1
            
        index_for_label = self._label_classes[label_class][label_name]
        return index_for_label   

_input_data_libsvm_representation = []

_feature_names_list = []
_feature_index_table = LabelToIndexConverter()

def feature_instance_to_index (feature_name, feature_string_value):
    global _feature_index_table
    
    feature_index_for_feature_string_value = _feature_index_table.getIndex(feature_name, feature_string_value)
    
    return feature_index_for_feature_string_value

_label_names_list = []
_label_index_table = LabelToIndexConverter()

def label_instance_to_index (label_class_name, label_instance_string_value):
    global _label_index_table
    
    index = _label_index_table.getIndex(label_class_name, label_instance_string_value)
    
    return index
    
    
   
def add_khiops_data_line_to_libsvm_representation (khiops_data_line):
    
    global _input_data_libsvm_representation
    global _feature_names_list 
    global _label_names_list   
    
    khiops_data_line_as_list = khiops_data_line.split()
    label_instance_value = khiops_data_line_as_list[0]
    feature_string_value_list = khiops_data_line_as_list[1:]
    
    features_values_table = {}
    for (feature_name, feature_string_value) in zip(_feature_names_list, feature_string_value_list):
        feature_value_index = feature_instance_to_index (feature_name, feature_string_value)
        features_values_table[feature_value_index] = 1
        
    # FIXME: compute label_index!!!
    label_class_name = _label_names_list[0]
    label_index = label_instance_to_index(label_class_name, label_instance_value)
    line_representation = (label_index, features_values_table)
        
    _input_data_libsvm_representation['vectors'].append(line_representation)
        

def khiopsFile2LibSvmFile (khiops_file_name, libsvm_file_name_prefix):
    
    global _input_data_libsvm_representation
    global _feature_names_list
    global _label_names_list

    _input_data_libsvm_representation = {
        'meta' : {
            'feature_one_based' : 0,
            'label_one_based' : 0
        },
        'vectors' : []                   
    }
    
    with open (khiops_file_name, 'r') as khiops_file:
        
        header_line = khiops_file.readline()
        headers_as_list = header_line.split()
        
        _label_names_list = headers_as_list[:1]
        _feature_names_list = headers_as_list[1:]
        
        while True:
            
            line = khiops_file.readline()
            if not line:
                break
            
            add_khiops_data_line_to_libsvm_representation (line)
            
    # TODO: save resulting representation
        

#
# TEST CASES
# ==========

class moduleTestCases (unittest.TestCase):
    
    def test1 (self):
    
        index = feature_instance_to_index ('CapShape', 'CONVEX')
        self.assertEqual(index, 0)
        
        index = feature_instance_to_index ('CapShape', 'FLAT')
        self.assertEqual(index, 1)
        
        index = feature_instance_to_index ('CapSurface', 'SMOOTH')
        self.assertEqual(index, 2)        
        
    def test2 (self):
    
        index = feature_instance_to_index ('CapShape', 'CONVEX')
        self.assertEqual(index, 0)
        
    def test3 (self):
    
        index = feature_instance_to_index ('CapSurface', 'SMOOTH')
        self.assertEqual(index, 2)             


def main():
    
    global _feature_one_based
    global _label_one_based
    
    # TODO: rewrite the comment
    parser = argparse.ArgumentParser(description='Generates a LIB SVM formated file for Squid Access Logs which have been labeled by squidGuard.')
#     parser.add_argument("-s", "--squidAccessLogFile", metavar='<squid access log>', type=str, dest="squidAccessLogFile", required=True, 
#                         help='The Squid access log file.')
#     parser.add_argument("-g", "--squidGuardFile", metavar='<squidGuard out>', type=str, dest="squidGuardFile", required=True,
#                         help='The resulting file after applying squidGuard to <squid access log>.')
#     parser.add_argument("-p", "--libSVMFile", metavar='<libsvm for Petuum MLR>', type=str, dest="libSVMFile", required=True,
#                         help='''The resulting "LIB SVM" formated file, containing the classified content.
#     The additional file with "<libSVMFile>.meta" suffix is generated, which contains the information required by Petuum's MLR algorithm.
#     These 2 files can be used as input to Petuum's MRL''')
#     parser.add_argument("-c", "--squidGuardConf", metavar='<squidGuard configuration file>', type=str, dest="squidGuardConfigurationFile", required=True,
#                         help='The squidGuard configuration file used to generate <squidGuard out>.')
#     parser.add_argument("-k", "--categoriesDump", metavar='<category dump file>', type=str, dest="categoriesDumpFile", required=True,
#                         help='Generated file, containing the list of all matched categories with their LibSVM index. Each category index is considered as a LibSVM label.')
    parser.add_argument("--featureOneBased", action='store_true', dest="featureOneBased", 
                        help='If true, feature indexes start at "1", "0" else (default is false => first feature index is "0"')
    parser.add_argument("--labelOneBased", action='store_true', dest="labelOneBased",
                        help='If true, labels indexes start at "1", "0" else (default is false => first label index is "0"')

    parser.add_argument("-k", "--khiopsInputFile", metavar='<what???>', type=str, dest="khiopsInputFile", required=True, 
                        help='The input file use as Khiops input.')
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
    

    khiopsFile2LibSvmFile (args.khiopsInputFile, "/tmp")

if __name__ == '__main__':
    main()