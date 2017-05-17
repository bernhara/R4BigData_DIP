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

    [num_train_total]=3
    [num_train_this_partition]=3
    [feature_dim]=3
    [num_labels]=5
    [format]=libsvm
    [feature_one_based]=0
    [label_one_based]=0
    [snappy_compressed]0
    
    [feature_0]={ [label_0]:value_0, [label_1]:value_1 ...}

'''



def read_peetuum_mlr_weight_file (weight_file_name):
    
    weight_dict ={}
    
    with open (weight_file_name, 'r') as weight_file:
        
        for _ in range(2):
            line = weight_file.readline()
            line_elements_list = line.split(':')
                 
            key = line_elements_list[0].strip()
            value = line_elements_list[1]     
            weight_dict[key] = int(value)
        
        num_labels = weight_dict["num_labels"]
        for label_number in range (num_labels):
            line = weight_file.readline()
            vector_dict = libsvm_feature_vector_to_dict (line, feature_one_based = False)
            
            weight_dict[label_number] = vector_dict
                 
    return (weight_dict)

def read_libsvm_file (libsvm_file_name, label_one_based, feature_one_based):
    
    file_content_list =[]
        
    with open (libsvm_file_name, 'r') as libsvm_file:
        
        while True:
            
            line = libsvm_file.readline()
            if not line:
                break
            
            content = labeled_libsvm_vector_to_label_and_dict (line, label_one_based, feature_one_based)
            file_content_list.append (content)
        
    return (file_content_list)

def rebase_libsvm_file_as_dict (libsvm_file_as_dict, target_feature_one_based, target_label_one_based):

    rebased_libsvm_file_as_dict = libsvm_file_as_dict.copy()
    
    # adjust elements to default configuration
    if not rebased_libsvm_file_as_disct.haskey('feature_one_based'):
        # if field 'feature_one_based' is missing, it is assumed that the file has features "zero based"
        rebased_libsvm_file_as_disct['feature_one_based'] = False

    if not rebased_libsvm_file_as_disct.haskey('label_one_based'):
        # if field 'label_one_based' is missing, it is assumed that the file has labels "zero based"
        rebased_libsvm_file_as_disct['label_one_based'] = False        
        
    
    # what to rebase and rebase
    if libsvm_file_as_dict['feature_one_based'] != target_feature_one_based:
        
        # we have to rebase the features
        rebased_libsvm_file_as_dict['feature_one_based'] = target_feature_one_based
        if target_feature_one_based:
            # rebase from zero_based to one_based
            feature_index_source_range = range(0, rebased_libsvm_file_as_dict['feature_dim'] - 1)
            feature_index_target_range = range(1, rebased_libsvm_file_as_dict['feature_dim'])
        else:
            # rebase from one_based to zero_based
            feature_index_source_range = range(1, rebased_libsvm_file_as_dict['feature_dim'])
            feature_index_target_range = range(0, rebased_libsvm_file_as_dict['feature_dim'] - 1)
            
        pass
            
        
        
    if libsvm_file_as_dict['target_label_one_based'] != target_label_one_based:
    
        # we have to rebase labels
        rebased_libsvm_file_as_dict['label_one_based'] = target_label_one_based
        if target_label_one_based:
            # rebase from zero_based to one_based
            label_index_source_range = range(0, rebased_libsvm_file_as_dict['num_labels'] - 1)
            label_index_target_range = range(1, rebased_libsvm_file_as_dict['num_labels'])
        else:
            # rebase from one_based to zero_based
            label_index_source_range = range(1, rebased_libsvm_file_as_dict['num_labels'])
            label_index_target_range = range(0, rebased_libsvm_file_as_dict['num_labels'] - 1)
            
        # remove original entries previously copied
        for index_key in label_index_source_range:
            del rebased_libsvm_file_as_dict[index_key]
            
        for source_index, target_index in zip (label_index_source_range, label_index_target_range):
            rebased_libsvm_file_as_dict[target_index] = libsvm_file_as_dict[source_index]
        
    return rebased_libsvm_file_as_dict

def libsvm_feature_vector_to_dict (libsvm_feature_line, feature_one_based):

    weighted_attribute_list = libsvm_feature_line.split()
    
    if feature_one_based:
        attribute_weigth_dict ={int(k)-1:float(v) for k,v in (x.split(':') for x in weighted_attribute_list)}
    else:
        attribute_weigth_dict ={int(k):float(v) for k,v in (x.split(':') for x in weighted_attribute_list)}    
    
    return (attribute_weigth_dict)

def labeled_libsvm_vector_to_label_and_dict (labeled_libsvm_line, label_one_based, feature_one_based):
    
    label_vector_pair = labeled_libsvm_line.split(maxsplit = 1)
    
    if label_one_based:
        label = int(label_vector_pair[0]) - 1
    else:
        label = int(label_vector_pair[0])

    libsvm_feature_string =  label_vector_pair[1]
    attribute_weigth_dict = libsvm_feature_vector_to_dict (libsvm_feature_string, feature_one_based)
   
    return (label, attribute_weigth_dict)


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
    
    def floatTruncatedString (self, f, n_digits = 14):
        
        # float formating function rounds the value
        # use string manipulation instead
        
        f_as_string = str(float(f))
        dot_position = f_as_string.index('.')
        (natural_part, decimal_part) = f_as_string.split(sep='.')
        
        str_containing_only_zeros = ''.zfill(20) # assert that n_digits is < than 20
        decimal_part += str_containing_only_zeros
        # truncate decimal_part
        decimal_part = decimal_part[:n_digits]

        rounded_string_for_f = natural_part + '.' + decimal_part
        return rounded_string_for_f
    
     
    def test_TODO (self):
        tested_precision = 3
        
        self.assertTrue(False, "NOT YES IMPLEMENTED")
         


if __name__ == '__main__':
    
    main()