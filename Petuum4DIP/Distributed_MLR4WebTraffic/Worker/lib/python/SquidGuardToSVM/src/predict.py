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
import io

import petuumEmulationLib

_one_based = False

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

def save_libsvm_representation_to_petuum_file (libsvm_represetation, libsvm_file_name, ordered_features = False):
    
    # write vectors
    with open (libsvm_file_name, 'w') as libsvm_file:
        
        if 'vectors' in libsvm_represetation:
            for vector in libsvm_represetation['vectors']:
                label, feature_dict = vector
                
                label_string = '{0:d}'.format(label)
                
                if ordered_features:
                    features_string = ' '.join('{0:d}:{1:+f}'.format(k, feature_dict[k]) for k in sorted(feature_dict))
                else:
                    features_string = ' '.join('{0:d}:{1:+f}'.format(k, v) for k,v in feature_dict.items())
              
                libsvm_line = '{0:s} {1:s}'.format(label_string, features_string)
                
                print(libsvm_line, file=libsvm_file)
    
    # write meta part
    libsvm_meta_file_name = libsvm_file_name + '.meta'
    
    with open (libsvm_meta_file_name, 'w') as libsvm_meta_file:
        
        for k,v in libsvm_represetation['meta'].items():
            petuum_meta_attribute_line = '{0}: {1}'.format(k, v)
            
            print(petuum_meta_attribute_line, file=libsvm_meta_file)
            

def cleanup_string_read_from_file (line):
    '''
    to prevent file format problems (Linix/DOS), with string eventual end line
    '''
    line = line.rstrip ('\n')
    
    return (line)
        
#
# Read a weight matrix file
#
    
def read_peetuum_mlr_weight_matrix_file (weight_file_name, file_content = None):
    
    weight_file_representation = { 'meta': {}, 'matrix': {} }
    
    if weight_file_name:
        weight_file = open (weight_file_name, 'r')
    else:
        weight_file = io.StringIO (file_content)
        

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
            
    weight_file.close()
                 
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

    return (predicted_label_index, predicted_labelization_sparse_vector)

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
    parser.add_argument("--oneBased", action='store_true', dest="oneBased",
                        help='If true, labels and feature indexing will be one based (initial shifting is performed if necessary -- default is true => first label and feature index is "1"')    
    parser.add_argument("-d", "--debug", action='store_true', dest="debug")       

    args = parser.parse_args()
    
    if args.oneBased:
        _one_based = True        
    else:
        _one_based = False        
        
    if args.debug:
        logging.getLogger().setLevel (logging.DEBUG)
        
        
    
    #
    # validate results
    
    petuum_mlr_computed_label_weights_representation = read_peetuum_mlr_weight_matrix_file(args.weitghFile)
    rebased_weights_representation = rebase_libsvm_file_representation (petuum_mlr_computed_label_weights_representation,
                                                                        target_feature_one_based=_one_based,
                                                                        target_label_one_based=_one_based)
    test_sample_representation = read_petuum_libsvm_file(args.libSVMFile)
    rebased_test_sample_representation = rebase_libsvm_file_representation (test_sample_representation,
                                                                            target_feature_one_based=_one_based,
                                                                            target_label_one_based=_one_based)
    
    # TODO: generate a formated output
    print ('// FORMAT: __PREDICTION_CSV_OUT__;real label;predicted label;label 0 prability;label 1 probability;...')
    test_sample_line_number = 1
    matched_predictions = 0
    unmatched_predictions = 0
    for test_sample in rebased_test_sample_representation['vectors']:
        sample_label_index, sample_feature_sparse_vector = test_sample
        
        _logger.debug ('Checking test sample line # {} which has label index {}'.format(test_sample_line_number, sample_label_index))
        
        predicted_label_index, scores_sparse_vector = predict_label_index (feature_sparse_vector = sample_feature_sparse_vector,
                                                                           petuum_mlr_computed_weight_representation = rebased_weights_representation,
                                                                           one_based = args.oneBased)
        
        # TODO: generate a formated output
        _index_probability_csv_output_format='{0:d}:{1:+f}'
        _index_probability_csv_output_format='{1:+f}'
        
        _scores_as_csv = ';'.join(_index_probability_csv_output_format.format(k, scores_sparse_vector[k]) for k in sorted(scores_sparse_vector))
        _prediction_out = '{0:d};{1:d};'.format(sample_label_index, predicted_label_index) + _scores_as_csv
        print ('__PREDICTION_CSV_OUT__;' + _prediction_out)            
        
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
        

    def test_predict_from_file (self):
        
        weight_file_content = \
'''num_labels: 7
feature_dim: 54
0:1.57285 1:0.0694593 2:-0.109966 3:-0.147938 4:-0.220996 5:-0.225058 6:-0.186356 7:-0.349958 8:0.0675006 9:0.127393 10:2.29787 11:0.559457 12:1.82041 13:-0.0297298 14:-0.00164359 15:-0.0872096 16:-0.00506236 17:-0.112912 18:-0.000310377 19:-0.0102707 20:-0.0898989 21:0 22:0.26352 23:0.0704738 24:-0.0456998 25:0.064407 26:0.286278 27:0 28:0 29:-0.00537808 30:-0.0567078 31:-0.0188949 32:-0.0411028 33:0.602116 34:0 35:0.956415 36:1.35191 37:0.0588544 38:0 39:-0.159712 40:0 41:0 42:0.841279 43:0.288459 44:1.05036 45:0.35092 46:0.657914 47:-0.11205 48:0.131641 49:0 50:0 51:-0.341685 52:-0.637624 53:-0.600382 
0:-0.391749 1:-0.109464 2:0.199008 3:0.128013 4:0.00323021 5:0.0626253 6:-0.0445322 7:0.152034 8:0.0984246 9:0.0279259 10:3.12362 11:1.1626 12:2.31846 13:0.0513702 14:-0.024076 15:-0.402193 16:-0.249233 17:0.0517815 18:-0.0103553 19:0.156391 20:0.13695 21:0 22:-0.028417 23:0.665782 24:0.749364 25:0.874561 26:0.353164 27:0 28:0 29:-0.186114 30:-0.078449 31:0.067115 32:0.258608 33:-0.296973 34:0 35:0.416756 36:0.297612 37:0.676403 38:0 39:-0.0103437 40:0 41:0 42:1.0504 43:0.395512 44:0.0908599 45:1.05778 46:1.01611 47:0.252684 48:-0.00928758 49:0 50:0 51:-0.317954 52:-0.149885 53:-0.148498 
0:-1.70118 1:0.467355 2:0.682311 3:0.288705 4:-0.0545734 5:0.0562165 6:0.210472 7:0.3959 8:-0.136595 9:-0.342393 10:-1.17166 11:-0.231315 12:-0.922707 13:0.205381 14:0.148955 15:0.607977 16:0.421293 17:0.139741 18:0.0422017 19:-0.274741 20:-0.00390243 21:0 22:-0.0783909 23:-0.399449 24:-0.194903 25:-0.209581 26:-0.325556 27:0 28:0 29:-0.087401 30:0.240883 31:-0.00854897 32:-0.0107899 33:-0.0325198 34:0 35:-0.209817 36:-0.264754 37:-0.140906 38:0 39:-0.0241301 40:0 41:0 42:-0.36725 43:-0.199386 44:-0.139007 45:-0.311626 46:-0.344261 47:-0.0151455 48:-0.00179589 49:0 50:0 51:-0.0386788 52:-0.0285282 53:-0.0102782 
0:-0.0497306 1:-0.0262774 2:0.0391258 3:0.0067286 4:0.0223313 5:0.176518 6:-0.00117602 7:0.0184386 8:-0.00812272 9:0.0281463 10:-1.18557 11:-0.334488 12:-1.28968 13:-0.197452 14:-0.0121121 15:-0.0657811 16:-0.0184359 17:-0.0605964 18:-0.00300832 19:-0.0665959 20:-0.00967786 21:0 22:-0.0239418 23:-0.168953 24:-0.088551 25:-0.156389 26:-0.0660761 27:0 28:0 29:-0.00674275 30:-0.0199724 31:-0.00663435 32:-0.0333106 33:-0.0560405 34:0 35:-0.231807 36:-0.261951 37:-0.151999 38:0 39:-0.0223591 40:0 41:0 42:-0.396646 43:-0.178213 44:-0.155276 45:-0.31165 46:-0.24147 47:-0.0186563 48:-0.00867917 49:0 50:0 51:-0.0808708 52:-0.0484575 53:-0.0363236 
0:-0.294256 1:-0.241323 2:-0.489575 3:-0.16506 4:0.158085 5:-0.364008 6:0.129365 7:0.150854 8:-0.00965356 9:0.036678 10:-0.757068 11:-0.370731 12:-0.943745 13:-0.246125 14:-0.0151784 15:-0.090683 16:-0.027033 17:-0.0715896 18:-0.00320985 19:-0.105583 20:-0.0123772 21:0 22:-0.0527984 23:-0.183354 24:-0.146564 25:-0.223797 26:-0.0591351 27:0 28:0 29:-0.0114991 30:-0.0349733 31:-0.0164463 32:-0.04274 33:-0.0674328 34:0 35:-0.258799 36:-0.32711 37:0.140729 38:0 39:0.279865 40:0 41:0 42:-0.42886 43:0.109795 44:-0.175731 45:-0.061254 46:-0.241827 47:-0.0188563 48:-0.010432 49:0 50:0 51:-0.0793508 52:-0.0450179 53:-0.0364319 
0:-1.28186 1:-0.0771625 2:-0.107176 3:-0.0580713 4:0.324977 5:0.0669998 6:0.0686197 7:-0.00596087 8:-0.0379072 9:-0.155226 10:-1.20314 11:-0.228322 12:-0.944704 13:0.266627 14:-0.0925455 15:0.0686371 16:-0.115274 17:0.0888796 18:-0.0242764 19:0.31632 20:-0.00637828 21:0 22:-0.0704635 23:0.10408 24:-0.195856 25:-0.206828 26:-0.104659 27:0 28:0 29:0.299381 30:-0.0391435 31:-0.0141439 32:-0.0208168 33:-0.0461231 34:0 35:-0.193 36:-0.255137 37:-0.158906 38:0 39:-0.0346222 40:0 41:0 42:-0.376708 43:-0.185286 44:-0.147475 45:-0.302834 46:-0.270651 47:-0.0218629 48:-0.00357756 49:0 50:0 51:-0.0477568 52:-0.0354876 53:-0.0170225 
0:2.14587 1:-0.0827665 2:-0.212941 3:-0.0521737 4:-0.232342 5:0.22915 6:-0.175691 7:-0.361429 8:0.0254535 9:0.277935 10:-1.1177 11:-0.55954 12:-0.0534054 13:-0.0517352 14:-0.00350427 15:-0.0313808 16:-0.00644172 17:-0.0359169 18:-0.00108398 19:-0.0159616 20:-0.014784 21:0 22:-0.00984743 23:-0.0905288 24:-0.0789174 25:-0.144248 26:-0.0847862 27:0 28:0 29:-0.00231095 30:-0.0118617 31:-0.00254349 32:-0.110065 33:-0.103576 34:0 35:-0.482106 36:-0.543641 37:-0.425676 38:0 39:-0.0289045 40:0 41:0 42:-0.326991 43:-0.232817 44:-0.525721 45:-0.424829 46:-0.57828 47:-0.0662991 48:-0.0979263 49:0 50:0 51:0.90543 52:0.944478 53:0.848658'''
    
        petuum_mlr_computed_weight_representation = read_peetuum_mlr_weight_matrix_file (None, file_content = weight_file_content)
        
        zero_based_sample_representation = {
        'meta': {
            'num_labels': 7,
            'feature_dim': 54,
            'feature_one_based': 0,
            'label_one_based': 0,                      
            },
        'vectors': [
            (0, { 0:1.27381, 1:1.0218, 2:-1.08144, 3:0.426112, 4:0.0271012, 5:0.697675, 6:-0.26709, 7:0.944866, 8:0.874575, 9:-0.34156, 10:1, 52:1}),
            ]
        }
        
        label, v = zero_based_sample_representation['vectors'][0]
        predicted_label_index, predicted_labelization_sparse_vector = predict_label_index (v, petuum_mlr_computed_weight_representation, one_based=False)                
        self.assertEqual(0, predicted_label_index)
        
        one_based_sample_representation = rebase_libsvm_file_representation (zero_based_sample_representation, target_feature_one_based=True, target_label_one_based=True)
        one_based_petuum_mlr_computed_weight_representation = rebase_libsvm_file_representation (petuum_mlr_computed_weight_representation, target_feature_one_based=True, target_label_one_based=True)
        
        label, v = one_based_sample_representation['vectors'][0]
        predicted_label_index, predicted_labelization_sparse_vector = predict_label_index (v, one_based_petuum_mlr_computed_weight_representation, one_based=True)                
        self.assertEqual(1, predicted_label_index)
        
        
        
       

if __name__ == '__main__':
    
    
    main()