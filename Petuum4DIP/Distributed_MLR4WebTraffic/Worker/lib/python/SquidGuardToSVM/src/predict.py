import sys

import argparse

import logging
logging.basicConfig (level=logging.WARNING)

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
    
        [feature_0]={ [label_0]:value_0, [label_1]:value_1 ...}
    }

'''
def libsvm_meta_attribute_string_to_dict (libsvm_meta_attribute_line):

    key_string_from_file, value_string_from_file = libsvm_feature_line.split(':', maxsplit = 1)

    key = key_string_from_file.strip()
    weight_dict[key] = int(value_string_from_file)    
    
    meta_attribute_dict = {key: value} 
   
    return (meta_attribute_dict)

def libsvm_feature_string_to_dict (libsvm_feature_line):

    weighted_attribute_list = libsvm_feature_line.split()
    
    feature_weigth_dict ={int(k):float(v) for k,v in (x.split(':') for x in weighted_attribute_list)}    
    
    return (feature_weigth_dict)

def labeled_libsvm_vector_to_label_and_dict (labeled_libsvm_line):
    
    label_string, feature_weigth_dict = labeled_libsvm_line.split(maxsplit = 1)

    label = int(label_string)
    
    feature_weigth_dict = libsvm_feature_string_to_dict (libsvm_feature_string)
   
    return (label, feature_weigth_dict)



#
# Read a libsvm file with meta info
#

def read_libsvm_matrix_file (libsvm_file_name):
    
    with open (libsvm_file_name, 'r') as libsvm_file:
        
        while True:
            
            line = libsvm_file.readline()
            if not line:
                break
            
            content = labeled_libsvm_vector_to_label_and_dict (line)
            file_content_list.append (content)
        
    return (file_content_list)    
    
    file_content_list =[]
    
def read_libsvm_meta_file (libsvm_file_name):
    '''
    Reads the "meta" annex file used by Petuum
    '''    
    
    libsvm_meta_file_name = libsvm_file_name + '.meta'
    
    libsvm_meta_data = {}
        
    with open (libsvm_meta_file_name, 'r') as libsvm_meta_file:
        
        while True:
            
            line = libsvm_file.readline()
            if not line:
                break
            
            coentent = libsvm_meta_attribute_string_to_dict (line)
            libsvm_meta_data.append(coentent)
        
    return (libsvm_meta_data)

def read_libsvm_file (libsvm_file_name):
    '''
    Reads the "data" (matrix)
    '''    
    
    libsvm_parsed_data = {}
    
    libsvm_parsed_data['matrix'] = read_libsvm_matrix_file (libsvm_file_name)
    libsvm_data['meta'] = read_libsvm_meta_file (libsvm_file_name)
    
    return libsvm_parsed_data

#
# Read a weight matrix file
#
    
def read_peetuum_mlr_weight_file (weight_file_name):
    
    weight_file_representation = { 'meta': {}, 'matrix': {} }
    
    with open (weight_file_name, 'r') as weight_file:
        
        for _ in range(2):
            line = weight_file.readline()
            weight_file_representation['meta'].append(libsvm_meta_attribute_string_to_dict(line))
            
        
        num_labels = weight_file_representation['meta']["num_labels"]
        for label_number in range (num_labels):
            line = weight_file.readline()
            vector_dict = libsvm_feature_string_to_dict (line)
            
            weight_file_representation['matrix'][label_number] = vector_dict
                 
    return (weight_file_representation)

#
# utility to rebase a libsvm file representatin
#

def rebase_libsvm_file_representation (libsvm_file_representation, target_feature_one_based, target_label_one_based):

    rebased_libsvm_file_representation = {'meta': {}, 'matrix': {}}

    # copy first the "meta" information part
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
            
    # copy entries which are identified as "label" lines (ie. key is an int)
    for label_index, value in libsvm_file_representation['matrix'].items():
        rebased_libsvm_file_representation['matrix'][label_index + label_index_delta] = value.copy()
            
    # rebase features
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
            
        # iterate on entries which are identified as "label" lines
        for label_index, feature_vector in rebased_libsvm_file_representation['matrix'].items():
            # line contains a "label" information
            current_feature_vector=rebased_libsvm_file_representation['matrix'][label_index]
            rebased_feature_vector={}
            for feature_index,value in current_feature_vector.items():
                rebased_feature_vector[feature_index + feature_index_delta]=value
            rebased_libsvm_file_representation['matrix'][label_index] = rebased_feature_vector
                        
        
    return rebased_libsvm_file_representation




def predict_label_index (attribute_dict, petuum_mlr_computed_label_weights):
    
    #prepare data for Petuum emulation lib
    list_of_labels_with_a_value = {label_index for label_index in range (0, nb_labels + 1) if petuum_mlr_computed_label_weights.haskeys(label_index)}
        
    weight_sparse_matrix = {}
    for label_index in list_of_labels_with_a_value:
         weight_sparse_matrix[label_index] = petuum_mlr_computed_label_weights[label_index]

    # FIXME: only feature_one_based is used => confusing        
    predicted_labelization_sparse_vector = petuumEmulationLib.Predict (input_data_for_prediction_sparse_vector,
                                                                       input_weight_sparse_matrix,
                                                                       one_based=_feature_one_based)
    
 
 
    # trace 
    for label_index in list_of_labels_with_a_value:
        print ('\t\tChecked weight matrix for label index: {} | Resulting label factor for the checked sample : {}'.format(label_index, computed_factor_dict[label_index]))
        
    # predict label by getting the label index having the greatest factor
    geatest_factor = -sys.float_info.max
    highest_label_index = None
    for label_index in label_index_range:
        if computed_factor_dict[label_index] > geatest_factor:
            geatest_factor = computed_factor_dict[label_index]
            highest_label_index = label_index
            
    predicted_label_index = highest_label_index
    
    print ('\t\tPredicted label index {} with score : {}'.format(predicted_label_index, geatest_factor))
    
    return (predicted_label_index)

def main():
    
    #
    # manage program options
    #
    
    # TODO:
    # add *one_based params
    
    parser = argparse.ArgumentParser(description='Apply the prediction function based on computed weights and check if predicition is OK with already known classification.')
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
    
    
    #
    # validate results
    
    petuum_mlr_computed_label_weights = read_peetuum_mlr_weight_file (args.weitghFile)
    test_sample_list = read_libsvm_file (args.libSVMFile, label_one_based = False, feature_one_based = False)
    
    test_sample_line_number = 1
    for test_sample in test_sample_list:
        sample_label_index, sample_attribute_dict = test_sample
        
        print ('Checking test sample line # {} which has label index {}'.format(test_sample_line_number, sample_label_index))
        
        predicted_label_index = predict_label_index (attribute_dict = sample_attribute_dict,
                                                     petuum_mlr_computed_label_weights = petuum_mlr_computed_label_weights)
        
        if predicted_label_index == sample_label_index:
            print ('\tMATCHED label prediction')
        else:
            print ('\t=== MISSED !!! label prediction')

        
        test_sample_line_number += 1

#     label_index_to_check = 0
#     train_line_to_check = train_line_list[0]
    
#     label_weight_attribute_dict = petuum_mlr_computed_label_weights[label_index_to_check]
#     train_label, train_attribute_dict = labeled_libsvm_vector_to_label_and_dict (train_line_to_check, label_one_based = True, feature_one_based = True)
#     
#     computed_factor = libsvm_data_scalar_vector_product (train_attribute_dict, label_weight_attribute_dict)
#     
#     print (computed_factor)


class moduleTestCases (unittest.TestCase):
    
    def test_rebase_libsvm_file_representation (self):
        
        # based on Petuum generated weight file
        zero_based_feature_and_zero_based_label_sample = {
            'meta': {
                'num_labels': 2,
                'feature_dim': 3
            },
            'matrix': {
                0: {0: 1.1, 1: 1.2, 2:1.3},
                1: {0: 2.1, 2:2.3}
            }
        }
        
        one_based_feature_and_one_based_label_rebased_sample = {
            'meta': {
                'num_labels': 2,
                'feature_dim': 3,
            },
            'matrix': {
                1: {1: 1.1, 2: 1.2, 3:1.3},
                2: {1: 2.1, 3:2.3}
            }
        }
        
        rebased_sample = rebase_libsvm_file_representation(zero_based_feature_and_zero_based_label_sample,
                                                    target_feature_one_based=True,
                                                    target_label_one_based=True)      
        self.assertEqual(one_based_feature_and_one_based_label_rebased_sample, rebased_sample)
         


if __name__ == '__main__':
    
    main()