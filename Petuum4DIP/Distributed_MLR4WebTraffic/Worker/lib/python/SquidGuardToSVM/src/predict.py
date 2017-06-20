#! /usr/bin/env python3

# coding: utf-8 

import sys

import argparse
import operator

import logging
# FIXME: we force all log to go to stderr. This should be configured in a logger configuration file
logging.basicConfig (stream=sys.stderr, level=logging.WARNING)
_logger = logging.getLogger("predict")

import unittest

import petuumEmulationLib

_feature_one_based = False
_label_one_based = False

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
def libsvm_meta_attribute_string_to_dict (libsvm_meta_attribute_line):
    
    key_string_from_file, value_string_from_file = libsvm_meta_attribute_line.split(':', maxsplit = 1)

    key = key_string_from_file.strip()
    if value_string_from_file.strip().isdecimal():
        value = int(value_string_from_file)
    else:
        value = value_string_from_file
    meta_attribute_dict = {key: value} 
   
    return (meta_attribute_dict)

def libsvm_feature_string_to_dict (libsvm_feature_line):

    weighted_attribute_list = libsvm_feature_line.split()
    
    feature_weigth_dict ={int(k):float(v) for k,v in (x.split(':') for x in weighted_attribute_list)}    
    
    return (feature_weigth_dict)

def labeled_libsvm_vector_to_label_and_sparse_vector (labeled_libsvm_line):
    
    label_string, feature_weigth_string = labeled_libsvm_line.split(maxsplit = 1)

    label = int(label_string)
    
    feature_weigth_sparse_vector = libsvm_feature_string_to_dict (feature_weigth_string)
   
    return (label, feature_weigth_sparse_vector)



#
# Read a libsvm file with meta info
#

def read_libsvm_vectors_file (libsvm_file_name):
    
    file_content_list = []
    
    with open (libsvm_file_name, 'r') as libsvm_file:
        
        while True:
            
            line = libsvm_file.readline()
            if not line:
                break
            line = cleanup_string_read_from_file(line)
            
            # TODO: we assume that the current line is labeled
            # This is only the case when this we this is a training line 
            content = labeled_libsvm_vector_to_label_and_sparse_vector (line)
            file_content_list.append (content)
        
    return (file_content_list)    
    

    
def read_libsvm_meta_file (libsvm_meta_file_name):
    '''
    Reads the "meta" annex file used by Petuum
    '''    
    

    
    libsvm_meta_data = {}
        
    with open (libsvm_meta_file_name, 'r') as libsvm_meta_file:
        
        while True:
            
            line = libsvm_meta_file.readline()
            if not line:
                break
            line = cleanup_string_read_from_file(line)
     
            content = libsvm_meta_attribute_string_to_dict (line)
            libsvm_meta_data.update(content)
        
    return (libsvm_meta_data)

def read_petuum_libsvm_file (libsvm_file_name):
    '''
    Reads the "data" (list of vectors)
    '''    
    
    libsvm_representation = {}
    
    libsvm_meta_file_name = libsvm_file_name + '.meta'
    libsvm_representation['meta'] = read_libsvm_meta_file (libsvm_meta_file_name)
    libsvm_representation['vectors'] = read_libsvm_vectors_file(libsvm_file_name)

    
    return libsvm_representation

def cleanup_string_read_from_file (line):
    '''
    to prevent file format problems (Linix/DOS), with string eventual end line
    '''
    line = line.rstrip ('\n')
    
    return (line)
        
#
# Read a weight matrix file
#
    
def read_peetuum_mlr_weight_matrix_file (weight_file_name):
    
    weight_file_representation = { 'meta': {}, 'matrix': {} }
    
    with open (weight_file_name, 'r') as weight_file:
        
        for _ in range(2):
            line = weight_file.readline()
            line = cleanup_string_read_from_file(line)
                      
            weight_file_as_dict_item = libsvm_meta_attribute_string_to_dict(line)
            weight_file_representation['meta'].update(weight_file_as_dict_item)
            
        
        num_labels = weight_file_representation['meta']["num_labels"]
        for label_number in range (num_labels):
            line = weight_file.readline()
            line = cleanup_string_read_from_file(line)            
            
            vector_dict = libsvm_feature_string_to_dict (line)
            
            weight_file_representation['matrix'][label_number] = vector_dict
                 
    return (weight_file_representation)

#
# utility to rebase a libsvm file representatin
#

def rebase_libsvm_file_representation (libsvm_file_representation, target_feature_one_based, target_label_one_based):
    
    # initialize a new dict which will hold the rebased version
    rebased_libsvm_file_representation = {}
    
    if 'matrix' in libsvm_file_representation:
        rebased_libsvm_file_representation['matrix'] = {}
    if 'vectors' in libsvm_file_representation:
        rebased_libsvm_file_representation['vectors'] = []        

    #
    # copy first the "meta" information part
    # ======================================
    rebased_libsvm_file_representation['meta'] = libsvm_file_representation['meta'].copy()
    
    # adjust elements to default configuration
    source_feature_one_based_libsvm_meta_attribute_value = libsvm_file_representation['meta'].get('feature_one_based', 0)
    source_label_one_based_libsvm_meta_attribute_value = libsvm_file_representation['meta'].get('label_one_based', 0)

    if not 'feature_one_based' in rebased_libsvm_file_representation['meta']:
        # if field 'feature_one_based' is missing, it is assumed that the file has features "zero based"
        rebased_libsvm_file_representation['meta']['feature_one_based'] = source_feature_one_based_libsvm_meta_attribute_value

    if not 'label_one_based' in rebased_libsvm_file_representation['meta']:
        # if field 'label_one_based' is missing, it is assumed that the file has labels "zero based"
        rebased_libsvm_file_representation['meta']['label_one_based'] = source_label_one_based_libsvm_meta_attribute_value
        
    # provide the information as boolean, to ease computation
    source_feature_one_based = True if source_feature_one_based_libsvm_meta_attribute_value == 1 else False 
    source_label_one_based = True if source_label_one_based_libsvm_meta_attribute_value == 1 else False      
        
    
    # what to rebase and rebase

    # copy label lines, with eventual rebasing if needed    
    if source_label_one_based != target_label_one_based:
    
        # we have to rebase labels
        if target_label_one_based:
            # rebase from zero_based to one_based
            rebased_libsvm_file_representation['meta']['label_one_based'] = 1            
            label_index_delta = +1
        else:
            # rebase from one_based to zero_based
            rebased_libsvm_file_representation['meta']['label_one_based'] = 0          
            label_index_delta = -1
    else:
        label_index_delta = 0
        
    # should we rebase features
    if source_feature_one_based != target_feature_one_based:
        
        # we have to rebase the features
        if target_feature_one_based:
            # rebase from zero_based to one_based
            rebased_libsvm_file_representation['meta']['feature_one_based'] = 1
            feature_index_delta = +1
        else:
            # rebase from one_based to zero_based
            rebased_libsvm_file_representation['meta']['feature_one_based'] = 0
            feature_index_delta = -1
    else:
        feature_index_delta = 0   
        
       
            
    if 'matrix' in libsvm_file_representation:
        
        # copy entries which are identified as "label" lines (ie. key is an int)
        for label_index, value in libsvm_file_representation['matrix'].items():
            rebased_libsvm_file_representation['matrix'][label_index + label_index_delta] = value.copy()

            
        # iterate on entries which are identified as "label" lines
        # TODO: should use "feature vector" variable and replay TEST CASE
        for label_index, feature_vector in rebased_libsvm_file_representation['matrix'].items():
            # line contains a "label" information
            rebased_feature_vector={}
            for feature_index,value in feature_vector.items():
                rebased_feature_vector[feature_index + feature_index_delta]=value
            rebased_libsvm_file_representation['matrix'][label_index] = rebased_feature_vector
                
    if 'vectors' in libsvm_file_representation:
        # rebuild a new list elements containing rebased vectors
        rebased_vector_list = []
        for labeled_vector in libsvm_file_representation['vectors']:
            label, feature_vector = labeled_vector

            if label is not None:
                rebased_label = label + label_index_delta
            else:
                rebased_label = None
            
            rebased_feature_vector={}
            for feature_index,value in feature_vector.items():
                rebased_feature_vector[feature_index + feature_index_delta]=value                
                
            rebased_labeled_vector = (rebased_label, rebased_feature_vector)
            rebased_vector_list.append(rebased_labeled_vector)
            
        rebased_libsvm_file_representation['vectors'] = rebased_vector_list
                        
        
    return rebased_libsvm_file_representation




def predict_label_index (feature_sparse_vector, petuum_mlr_computed_weight_representation, one_based=True):
    

    # FIXME: only feature_one_based is used => confusing        
    predicted_labelization_sparse_vector = petuumEmulationLib.Predict (feature_sparse_vector,
                                                                       petuum_mlr_computed_weight_representation['matrix'],
                                                                       one_based=one_based)
    
    # trace 
    for label_index in predicted_labelization_sparse_vector.keys():
        prediction_for_this_label = predicted_labelization_sparse_vector[label_index]
        _logger.debug ('\t\tChecked weight matrix for label index: {} | Resulting label factor for the checked sample : {}'.format(label_index, prediction_for_this_label))
        
    # predict label by getting the label index having the greatest factor
    geatest_factor = -sys.float_info.max
    highest_label_index = None
    for label_index in predicted_labelization_sparse_vector.keys():
        prediction_for_this_label = predicted_labelization_sparse_vector[label_index]        
        if prediction_for_this_label > geatest_factor:
            geatest_factor = prediction_for_this_label
            highest_label_index = label_index
            
    predicted_label_index = highest_label_index
    _logger.debug ('\t\tPredicted label index {} with score : {}'.format(predicted_label_index, geatest_factor))
    
    # The same, sorting prediction result    
    predicted_labelization_vector_elements_list = predicted_labelization_sparse_vector.items()
    sorted_predicted_labelization_vector_elements_list = sorted(predicted_labelization_vector_elements_list,
                                                                key=operator.itemgetter(1),
                                                                reverse=True)
    _logger.debug ('\t\tPrediction order for each feature: {}'.format(sorted_predicted_labelization_vector_elements_list))

    return (predicted_label_index)

def main():
    
    #
    # manage program options
    #
    
    # TODO:
    # add *one_based params
    
    parser = argparse.ArgumentParser(description='Apply the prediction function based on computed weights and check if prediction is OK with already known classification.')
    parser.add_argument("-w", "--weitghFile", metavar='<the weight file generated by MLR learning>', type=str, dest="weitghFile", required=True, 
                        help='The weight file generated by MLR learning.')
    parser.add_argument("-p", "--libSVMFile", metavar='<libsvm for Petuum MLR>', type=str, dest="libSVMFile", required=True,
                        help='''The "LIB SVM" formated file, containing the classified content.
    The additional file with "<libSVMFile>.meta" suffix is generated, which contains the information required by Petuum's MLR algorithm.
    These 2 files can be used as input to Petuum's MRL''') 
    parser.add_argument("--featureOneBased", action='store_true', dest="featureOneBased", 
                        help='If true, feature indexes start at "1", "0" else (default is false => first feature index is "0"')
    parser.add_argument("--labelOneBased", action='store_true', dest="labelOneBased",
                        help='If true, labels indexes start at "1", "0" else (default is false => first label index is "0"')
    parser.add_argument("--oneBased", action='store_false', dest="oneBased",
                        help='If true, labels and feature indexing will be one based (initial shifting is performed if necessary -- default is true => first label and feature index is "1"')    
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
        
    if args.oneBased:
        _feature_one_based = True        
        _label_one_based = True
    else:
        _logger.critical ('ZERO BASE unsupported')
        sys.exit(1)
        _feature_one_based = False        
        _label_one_based = False      
        
    if args.debug:
        logging.getLogger().setLevel (logging.DEBUG)
        
        
    
    #
    # validate results
    
    petuum_mlr_computed_label_weights_representation = read_peetuum_mlr_weight_matrix_file(args.weitghFile)
    rebased_weights_representation = rebase_libsvm_file_representation (petuum_mlr_computed_label_weights_representation,
                                                                        target_feature_one_based=_feature_one_based,
                                                                        target_label_one_based=_label_one_based)
    test_sample_representation = read_petuum_libsvm_file(args.libSVMFile)
    rebased_test_sample_representation = rebase_libsvm_file_representation (test_sample_representation,
                                                                            target_feature_one_based=_feature_one_based,
                                                                            target_label_one_based=_label_one_based)
    
    test_sample_line_number = 1
    matched_predictions = 0
    unmatched_predictions = 0
    for test_sample in rebased_test_sample_representation['vectors']:
        sample_label_index, sample_feature_sparse_vector = test_sample
        
        _logger.debug ('Checking test sample line # {} which has label index {}'.format(test_sample_line_number, sample_label_index))
        
        predicted_label_index = predict_label_index (feature_sparse_vector = sample_feature_sparse_vector,
                                                     petuum_mlr_computed_weight_representation = rebased_weights_representation,
                                                     one_based = args.oneBased)
        
        if predicted_label_index == sample_label_index:
            _logger.debug ('\tMATCHED label prediction')
            matched_predictions += 1
        else:
            _logger.debug ('\t=== MISSED !!! label prediction. Predicted index is {} while sample index was {}'. format(predicted_label_index, sample_label_index))
            unmatched_predictions += 1

        
        test_sample_line_number += 1
        
    sample_size = test_sample_line_number - 1
    print ("Sample size: {}".format(sample_size))
    print ("\tamount of matched predictions: {}".format(matched_predictions))
    print ("\tamount of unmatched predictions: {}".format(unmatched_predictions))    


#
# TEST CASES
# ==========

class moduleTestCases (unittest.TestCase):
    
    _zero_based_feature_and_zero_based_label_sample = {
        'meta': {
            'num_labels': 2,
            'feature_dim': 3
        },
        'matrix': {
            0: {0: 1.1, 1: 1.2, 2:1.3},
            1: {0: 2.1, 2:2.3}
        }
    }    

    def test_rebase_libsvm_file_representation_1 (self):
        
        one_based_feature_and_one_based_label_rebased_sample = {
            'meta': {
                'num_labels': 2,
                'feature_dim': 3,
                'feature_one_based': 1,
                'label_one_based': 1,                
            },
            'matrix': {
                1: {1: 1.1, 2: 1.2, 3:1.3},
                2: {1: 2.1, 3:2.3}
            }
        }
        
        rebased_sample = rebase_libsvm_file_representation(self._zero_based_feature_and_zero_based_label_sample,
                                                    target_feature_one_based=True,
                                                    target_label_one_based=True)      
        self.assertEqual(one_based_feature_and_one_based_label_rebased_sample, rebased_sample)
        
    def test_rebase_libsvm_file_representation_2 (self):
        
        one_based_feature_and_zero_based_label_rebased_sample = {
            'meta': {
                'num_labels': 2,
                'feature_dim': 3,
                'feature_one_based': 1,
                'label_one_based': 0,                
            },
            'matrix': {
                0: {1: 1.1, 2: 1.2, 3:1.3},
                1: {1: 2.1, 3:2.3}
            }
        }
        
        rebased_sample = rebase_libsvm_file_representation(self._zero_based_feature_and_zero_based_label_sample,
                                                    target_feature_one_based=True,
                                                    target_label_one_based=False)      
        self.assertEqual(one_based_feature_and_zero_based_label_rebased_sample, rebased_sample)
 
    def test_rebase_libsvm_file_representation_3 (self):
        
        unchanged_rebased_zero_based_feature_and_zero_based_label_sample = {
        'meta': {
            'num_labels': 2,
            'feature_dim': 3,
            'feature_one_based': 0,
            'label_one_based': 0,                      
            },
        'matrix': {
            0: {0: 1.1, 1: 1.2, 2:1.3},
            1: {0: 2.1, 2:2.3}
            }
        }    
        
        rebased_sample = rebase_libsvm_file_representation(self._zero_based_feature_and_zero_based_label_sample,
                                                    target_feature_one_based=False,
                                                    target_label_one_based=False)      
        self.assertEqual(unchanged_rebased_zero_based_feature_and_zero_based_label_sample, rebased_sample)
        
    def test_rebase_libsvm_file_representation_4 (self):
        
        one_based_vector_sample = {
        'meta': {
            'num_labels': 2,
            'feature_dim': 3,
            'feature_one_based': 1,
            'label_one_based': 1,                      
            },
        'vectors': [
            (1, {1: 1.1, 2: 1.2, 3:1.3}),
            (2, {1: 2.1, 3:2.3})
            ]
        }
        
        zero_based_vector_sample = {
        'meta': {
            'num_labels': 2,
            'feature_dim': 3,
            'feature_one_based': 0,
            'label_one_based': 0,                      
            },
        'vectors': [
            (0, {0: 1.1, 1: 1.2, 2:1.3}),
            (1, {0: 2.1, 2:2.3})
            ]
        }          
        
        rebased_sample = rebase_libsvm_file_representation(one_based_vector_sample,
                                                    target_feature_one_based=False,
                                                    target_label_one_based=False)      
        self.assertEqual(zero_based_vector_sample, rebased_sample)
        
        rebased_sample = rebase_libsvm_file_representation(zero_based_vector_sample,
                                                           target_feature_one_based=True,
                                                           target_label_one_based=True)      
        self.assertEqual(one_based_vector_sample, rebased_sample)        
        

if __name__ == '__main__':
    
    
    main()