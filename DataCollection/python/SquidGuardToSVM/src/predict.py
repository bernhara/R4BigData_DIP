
import sys



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

def libsvm_data_scalar_vector_product (v1, v2):
    
    product = 0.0
    for v1_key, v1_value in v1.items():
        v2_value = v2.get(v1_key)
        if v2_value:
            factor = v1_value * v2_value
            product += factor
       
    return (product)

def predict_label_index (attribute_dict, petuum_mlr_computed_label_weights):
    
    nb_labels = petuum_mlr_computed_label_weights["num_labels"]
      
    computed_factor_dict = {}
    for label_index in range (nb_labels):
            
            computed_weights_for_label_index = petuum_mlr_computed_label_weights[label_index]
            computed_factor = libsvm_data_scalar_vector_product (attribute_dict, computed_weights_for_label_index)
            computed_factor_dict[label_index] = computed_factor
            
    # trace 
    for label_index in range (nb_labels):
        print ('\t\tChecked weight matrix for label index: {} | Resulting label factor for the checked sample : {}'.format(label_index, computed_factor_dict[label_index]))
        
    # predict label by getting the label index having the greatest factor
    geatest_factor = -sys.float_info.max
    highest_label_index = None
    for label_index in range (nb_labels):
        if computed_factor_dict[label_index] > geatest_factor:
            geatest_factor = computed_factor_dict[label_index]
            highest_label_index = label_index
            
    predicted_label_index = highest_label_index
    
    print ('\t\tPredicted label index {} with score : {}'.format(predicted_label_index, geatest_factor))
    
    return (predicted_label_index)

def main():
    #
    # validate results
    
    # label1_weight = {1:1.27381 2:1.0218 3:-1.08144 4:0.426112 5:0.0271012 6:0.697675 7:-0.26709 8:0.944866 9:0.874575 10:-0.34156 11:1 53:1}
    
    petuum_mlr_computed_label_weights = read_peetuum_mlr_weight_file ('samples/datasets/RESULT/t1.weight')
    test_sample_list = read_libsvm_file ('samples/datasets/covtype.scale.test.small', label_one_based = True, feature_one_based = True)
    
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




if __name__ == '__main__':
    main()