import unittest
import math

# =======================================================================================================

def fastpow2 (p):
    """Implements C++ function:
    
    """    
    r = math.pow(2.0, p)
    return r

def fastexp (p):
    """Implements C++ function:
    
    """    
    return fastpow2 (1.442695040 * p)

# =======================================================================================================

def LogSum(log_a, log_b):
    """Implements C++ function:
 
 float LogSum(float log_a, float log_b) {
  return (log_a < log_b) ? log_b + fastlog(1 + fastexp(log_a - log_b)) :
    log_a + fastlog(1 + fastexp(log_b-log_a));
}
    """    
    if (log_a < log_b):
        r = log_b + fastlog(1 + fastexp(log_a - log_b))
    else:   
        r = log_a + fastlog(1 + fastexp(log_b-log_a))
        
    return r

def LogSumVec(vec_as_list):
    """Implements C++ function:
    
float LogSumVec(const std::vector<float>& logvec) {
        float sum = 0.;
        sum = logvec[0];
        for (int i = 1; i < logvec.size(); ++i) {
                sum = LogSum(sum, logvec[i]);
        }
        return sum;
}
    """    
    
    accumulated_sum = vec_as_list[0]
    for i in range(1, len(vec_as_list)):
        accumulated_sum = LogSum(accumulated_sum, vec_as_list[i])
        
    return accumulated_sum

# =======================================================================================================

def fastlog2 (x):
    """Implements C++ function:
    

fastlog2 (float x)
{
  union { float f; uint32_t i; } vx = { x };
  union { uint32_t i; float f; } mx = { (vx.i & 0x007FFFFF) | 0x3f000000 };
  float y = vx.i;
  y *= 1.1920928955078125e-7f;

  return y - 124.22551499f
           - 1.498030302f * mx.f
           - 1.72587999f / (0.3520887068f + mx.f);
} 
    """
       
    r = math.log(x, 2)
    return (r)

def fastlog (x):
    """Implements C++ function:
    
fastlog (float x)
{
  return 0.69314718f * fastlog2 (x);
}
    """    
    return 0.69314718 * fastlog2 (x)

# =======================================================================================================

def Softmax(vec_as_list):
    """Implements C++ function:
    
const float kCutoff = 1e-15;

void Softmax(std::vector<float>* vec) {
  CHECK_NOTNULL(vec);
  // TODO(wdai): Figure out why this is necessary. Doubt it is.
    for (int i = 0; i < vec->size(); ++i) {
        if (std::abs((*vec)[i]) < kCutoff) {
            (*vec)[i] = kCutoff;
        }
    }
    double lsum = LogSumVec(*vec);
    for (int i = 0; i < vec->size(); ++i) {
        (*vec)[i] = fastexp((*vec)[i] - lsum);
        (*vec)[i] = (*vec)[i] > 1 ? 1. : (*vec)[i];
  }
}"""
    
    lsum = LogSumVec(vec_as_list)
    softmax_vector_as_list = [0.0 for _ in vec_as_list]
    for i, val_for_i in enumerate(vec_as_list):
        softmax_vector_item =  fastexp(val_for_i - lsum)
        if softmax_vector_item > 1:
            softmax_vector_item = 1.0
        softmax_vector_as_list[i] = softmax_vector_item
    
    return softmax_vector_as_list

# =======================================================================================================

def Sigmoid (x):
    
    sigmoid_val = 1.0 / (1.0 + math.exp(-x))
    
    return sigmoid_val

# =======================================================================================================


def SparseDenseFeatureDotProduct(f1_feature_dict, f2_feature_dict):
    """Implements C++ function:
    
float SparseDenseFeatureDotProduct(const AbstractFeature<float>& f1,
    const AbstractFeature<float>& f2) {
  CHECK_EQ(f1.GetFeatureDim(), f2.GetFeatureDim());
  float sum = 0.;
  for (int i = 0; i < f1.GetNumEntries(); ++i) {
    int32_t f1_fid = f1.GetFeatureId(i);
    sum += f1.GetFeatureVal(i) * f2[f1_fid];
  }
  return sum;
}"""   
    
    accumulated_sum = 0.0
    for f1_key, f1_value in f1_feature_dict.items():
        f2_value = f2_feature_dict.get(f1_key)
        if f2_value:
            factor = f1_value * f2_value
            accumulated_sum += factor
       
    return (accumulated_sum)

# =======================================================================================================


def Predict (feature_dict_sparse_vector, weigth_dict_table_sparse_matrix, one_based):
    """Implements C++ function:

std::vector<float> MLRSGDSolver::Predict(const petuum::ml::AbstractFeature<float>& feature) const
{
    std::vector<float> y_vec(num_labels_);

#ifdef RAPH
    LOG(INFO) << "RAPH: " << "MLRSGDSolver::Predict for feature: " << feature.ToString();
#endif

    for (int i = 0; i < num_labels_; ++i) {
      y_vec[i] = FeatureDotProductFun_(feature, w_cache_[i]);
#ifdef RAPH
      LOG(INFO) << "RAPH: "<< "num_label = " << i ;
      LOG(INFO) << "RAPH: "<< "y_vec[" << i << "] = " << y_vec[i];
      LOG(INFO) << "RAPH: "<< "w_cache_[" << i << "] = " << w_cache_[i].ToString();
#endif
    }
    LOG(INFO) << "y_vec for all labels: ";
    for (const auto i: y_vec) {
      LOG(INFO) << "RAPH: " << i;
    }
    petuum::ml::Softmax(&y_vec);
    LOG(INFO) << "y_vec after SoftMax: ";
    for (const auto i: y_vec) {
      LOG(INFO) << "RAPH: " << i;
    }

    return y_vec;
  }
    """
    
    FeatureDotProductFun_ = SparseDenseFeatureDotProduct
    
    product_sparse_vector = {}
    
    for label in weigth_dict_table_sparse_matrix.keys():
        
        weights_dict_for_this_label = weigth_dict_table_sparse_matrix[label]
        
        product_for_this_label = FeatureDotProductFun_ (feature_dict_sparse_vector, weights_dict_for_this_label)
        product_sparse_vector[label] = product_for_this_label
        
    product_dense_vector = dict_vector_to_list_vector(product_sparse_vector, one_based)
    softmaxed_product_dense_vector = Softmax (product_dense_vector)
    softmaxed_product_sparse_vector = list_vector_to_dict_vector(softmaxed_product_dense_vector, one_based)
    
    return softmaxed_product_sparse_vector

def dict_vector_to_list_vector (dict_vector, one_based):
    
    keys = dict_vector.keys()
    greatest_index = max(keys)
    
    if one_based:
        list_size = greatest_index
    else:
        list_size = greatest_index + 1
        
    
    list_vector = [ 0.0 ] * list_size
    if one_based:
        for k, val_for_k in dict_vector.items():
            list_vector[k-1] = val_for_k
    else:
        for k, val_for_k in dict_vector.items():
            list_vector[k] = val_for_k        
            
    return list_vector

def list_vector_to_dict_vector (list_vector, one_based):
    
    dict_vector = {}
    
    if one_based:
        dict_range = range (1, len(list_vector) + 1)
    else:
        dict_range = range (0, len(list_vector))
    
    for key,value in zip (dict_range, list_vector):
        if value != 0.0:
            dict_vector[key] = value
            
    return dict_vector
    
class moduleTestCases (unittest.TestCase):
    
    def floatTruncatedString (self, f, n_digits = 14):
        
        # float formating function rounds the value
        # use string manipulation instead
        
        f_as_string = str(float(f))
        (natural_part, decimal_part) = f_as_string.split(sep='.')
        
        str_containing_only_zeros = ''.zfill(20) # assert that n_digits is < than 20
        decimal_part += str_containing_only_zeros
        # truncate decimal_part
        decimal_part = decimal_part[:n_digits]

        rounded_string_for_f = natural_part + '.' + decimal_part
        return rounded_string_for_f
    
    
    def test_dict_vector_to_list_vector (self):
        
        # test zero_based version
        sample = {0:0.629833, 1:3.12866, 5:-0.415136, 11:-1.54497, 2:0.300126, 9:-0.132952, 8:-1.98521}
        ref_result = [
            0.629833, #0
            3.12866, #1
            0.300126, #2
            0.0, #3
            0.0, #4
            -0.415136, #5
            0.0, #6
            0.0, #7
            -1.98521, #8
            -0.132952, #9
            0.0, #10
            -1.54497, #11
        ]
        
        computed_result = dict_vector_to_list_vector(sample, one_based=False)    
        for r,c in zip(ref_result, computed_result):
            self.assertEqual(r, c, 'dict_vector_to_list_vector')


        # test one_based version            
        sample = {1:3.12866, 5:-0.415136, 11:-1.54497, 2:0.300126, 9:-0.132952, 8:-1.98521}
        ref_result = [
            3.12866, #1
            0.300126, #2
            0.0, #3
            0.0, #4
            -0.415136, #5
            0.0, #6
            0.0, #7
            -1.98521, #8
            -0.132952, #9
            0.0, #10
            -1.54497, #11
        ]
        
        computed_result = dict_vector_to_list_vector(sample, one_based=True)    
        for r,c in zip(ref_result, computed_result):
            self.assertEqual(r, c, 'dict_vector_to_list_vector')            

            
            
    def test_list_vector_to_dict_vector (self):

        # test zero_based version
        sample = [
            0.629833, #0
            3.12866, #1
            0.300126, #2
            0.0, #3
            0.0, #4
            -0.415136, #5
            0.0, #6
            0.0, #7
            -1.98521, #8
            -0.132952, #9
            0.0, #10
            -1.54497, #11
        ]
        ref_result = {0:0.629833, 1:3.12866, 5:-0.415136, 11:-1.54497, 2:0.300126, 9:-0.132952, 8:-1.98521}        
        
        computed_result = list_vector_to_dict_vector(sample, one_based=False) 
        self.assertEqual(ref_result, computed_result)
        
        sample.append (0.0)
        computed_result = list_vector_to_dict_vector(sample, one_based=False) 
        self.assertEqual(ref_result, computed_result)
        
        sample.append (1.0)
        computed_result = list_vector_to_dict_vector(sample, one_based=False) 
        self.assertNotEqual(ref_result, computed_result)   
        
        # test one_based version
        sample = [
            3.12866, #1
            0.300126, #2
            0.0, #3
            0.0, #4
            -0.415136, #5
            0.0, #6
            0.0, #7
            -1.98521, #8
            -0.132952, #9
            0.0, #10
            -1.54497, #11
        ]
        ref_result = {1:3.12866, 5:-0.415136, 11:-1.54497, 2:0.300126, 9:-0.132952, 8:-1.98521}        
        
        computed_result = list_vector_to_dict_vector(sample, one_based=True) 
        self.assertEqual(ref_result, computed_result)             
        

     
    def test_LogSumVec (self):
        tested_precision = 3
        
        sample = [2.32699, 2.70564, 0.70979, -1.65623, -1.32633, -0.59962, -2.18235]
        sample_LogSumVec = 3.34482
        
        logSum = LogSumVec(sample)
        diff = (logSum - sample_LogSumVec)
        
        diff_as_string = self.floatTruncatedString (diff, tested_precision)
        zero_as_string = self.floatTruncatedString (0.0, tested_precision)
        self.assertEqual(diff_as_string, zero_as_string, 'non zero difference with sample')
         
    def test_Softmax (self):
        tested_precision = 3
        
        sample = [0.629833, 3.12866, -0.415136, -1.54497, 0.300126, -0.132952, -1.98521]
        ref_result = [0.0671654, 0.817307, 0.0236235, 0.00763237, 0.0483034, 0.0313251, 0.00491428]
        
        computed_result = Softmax(sample)    
        for r,c in zip(ref_result, computed_result):
            self.assertEqual(self.floatTruncatedString(r, tested_precision), self.floatTruncatedString(c, tested_precision), 'Softmax did not compute equivalent values')
            
    def test_SparseDenseFeatureDotProduct(self):
        tested_precision = 4
        
        v1_sample = {0:-0.722766, 1:1.6205, 2:0.12016, 3:-0.0631851, 4:-0.761921, 5:-0.922334, 6:-0.97684, 7:-0.269095, 8:0.743925, 9:-0.654204, 12:1, 44:1}
        v2_sample = {0:1.59727, 1:0.0593455, 2:-0.0893879, 3:-0.151879, 4:-0.210145, 5:-0.197497, 6:-0.173927, 7:-0.326345, 8:0.0456448, 9:0.166405, 10:2.36239, 11:0.521288, 12:1.84793, 13:-0.031775, 14:-0.00115621, 15:-0.0904455, 16:-0.00524351, 17:-0.171253, 18:-0.00025415, 19:-0.0118456, 20:-0.0842596, 21:0, 22:0.260991, 23:0.0506531, 24:-0.0482705, 25:0.0425302, 26:0.474681, 27:0, 28:0, 29:-0.00536855, 30:-0.0630568, 31:-0.0276387, 32:-0.046064, 33:0.556238, 34:0, 35:1.04189, 36:1.36368, 37:0.0144527, 38:0, 39:-0.220127, 40:0, 41:0, 42:0.887994, 43:0.320543, 44:1.0134, 45:0.339152, 46:0.635149, 47:-0.114862, 48:0.137085, 49:0, 50:0, 51:-0.352742, 52:-0.585151, 53:-0.610863}
        ref_result = 2.32699
        
        computed_result = SparseDenseFeatureDotProduct(v1_sample, v2_sample)
        self.assertEqual(self.floatTruncatedString (computed_result, tested_precision),
                         self.floatTruncatedString (ref_result, tested_precision))
        # commutative computation
        computed_result = SparseDenseFeatureDotProduct(v2_sample, v1_sample)
        self.assertEqual(self.floatTruncatedString (computed_result, tested_precision),
                         self.floatTruncatedString (ref_result, tested_precision))
        
    def test_Predict1 (self):
        tested_precision = 3
        
        # data copied from a Petuum MLR run
        # =================================
        
        w_cache_ = {}
        y_vec = {}
        
        input_data_for_prediction_sparse_vector = { 0:-0.747768, 1:-0.273881, 2:1.58879, 3:-0.985321, 4:-0.436021, 5:0.5367, 6:1.52596, 7:-0.673748, 8:-1.94748, 9:-0.158051, 10:1, 42:1 }
        
        y_vec[0] = 1.94323
        
        w_cache_[0] = { 0:1.58858, 1:0.0394467, 2:-0.0906082, 3:-0.156067, 4:-0.216681, 5:-0.2029, 6:-0.160053, 7:-0.33446, 8:0.0307443, 9:0.16801, 10:2.3607, 11:0.518244, 12:1.84575, 13:-0.0321007, 14:-0.00103631, 15:-0.0897541, 16:-0.0053794, 17:-0.17068, 18:-0.000180907, 19:-0.0120043, 20:-0.0844871, 21:0, 22:0.261211, 23:0.0495062, 24:-0.0464753, 25:0.0444576, 26:0.472011, 27:0, 28:0, 29:-0.00507786, 30:-0.0630788, 31:-0.027099, 32:-0.0445324, 33:0.555346, 34:0, 35:1.04113, 36:1.36229, 37:0.014477, 38:0, 39:-0.218825, 40:0, 41:0, 42:0.891142, 43:0.318359, 44:1.01087, 45:0.336174, 46:0.635311, 47:-0.113666, 48:0.137528, 49:0, 50:0, 51:-0.353905, 52:-0.588246, 53:-0.612788 }
        
        y_vec[1] = 4.28705
        
        w_cache_[1] = { 0:-0.372105, 1:-0.0569459, 2:0.245376, 3:0.159996, 4:0.00162248, 5:0.0218235, 6:-0.0742978, 7:0.13684, 8:0.133016, 9:-0.0349739, 10:3.17683, 11:1.28466, 12:2.30496, 13:0.0415056, 14:-0.0242421, 15:-0.41543, 16:-0.248828, 17:0.146032, 18:-0.00816899, 19:0.144923, 20:0.128267, 21:0, 22:-0.0239538, 23:0.70997, 24:0.816235, 25:0.894121, 26:0.209569, 27:0, 28:0, 29:-0.182105, 30:-0.0680093, 31:0.0875756, 32:0.266324, 33:-0.238146, 34:0, 35:0.364996, 36:0.309124, 37:0.782253, 38:0, 39:-0.15926, 40:0, 41:0, 42:1.03225, 43:0.409461, 44:0.112833, 45:1.08715, 46:1.05619, 47:0.25719, 48:-0.0116541, 49:0, 50:0, 51:-0.331892, 52:-0.15396, 53:-0.140849 }
        
        y_vec[2] = 0.852043
        
        w_cache_[2] = { 0:-1.71609, 1:0.460316, 2:0.694215, 3:0.317663, 4:-0.0436938, 5:0.0560919, 6:0.220136, 7:0.396483, 8:-0.144809, 9:-0.3519, 10:-1.17654, 11:-0.232488, 12:-0.98585, 13:0.227937, 14:0.141731, 15:0.62851, 16:0.415743, 17:0.160694, 18:0.0312685, 19:-0.237649, 20:-0.00291545, 21:0, 22:-0.0798158, 23:-0.414649, 24:-0.215931, 25:-0.206469, 26:-0.344068, 27:0, 28:0, 29:-0.0936494, 30:0.244163, 31:-0.0102133, 32:-0.0122954, 33:-0.0333992, 34:0, 35:-0.208001, 36:-0.260296, 37:-0.141848, 38:0, 39:-0.0330215, 40:0, 41:0, 42:-0.374113, 43:-0.20366, 44:-0.134936, 45:-0.326533, 46:-0.363144, 47:-0.0167314, 48:-0.00131143, 49:0, 50:0, 51:-0.0334361, 52:-0.0298213, 53:-0.0111441 }
        
        y_vec[3] = -1.39972
        
        w_cache_[3] = { 0:-0.0467873, 1:-0.000422931, 2:0.0477765, 3:0.0201929, 4:0.0321186, 5:0.18055, 6:0.00332516, 7:0.010359, 8:-0.0158681, 9:0.0230101, 10:-1.19637, 11:-0.346745, 12:-1.32, 13:-0.196186, 14:-0.0113297, 15:-0.0656588, 16:-0.0181811, 17:-0.0697971, 18:-0.00219892, 19:-0.0687804, 20:-0.00860879, 21:0, 22:-0.022438, 23:-0.169364, 24:-0.0930835, 25:-0.153014, 26:-0.0718467, 27:0, 28:0, 29:-0.00621855, 30:-0.0194221, 31:-0.00783251, 32:-0.0329371, 33:-0.0571472, 34:0, 35:-0.237331, 36:-0.260916, 37:-0.162063, 38:0, 39:-0.0322166, 40:0, 41:0, 42:-0.402716, 43:-0.1866, 44:-0.149097, 45:-0.313604, 46:-0.24314, 47:-0.0196189, 48:-0.00873793, 49:0, 50:0, 51:-0.0757643, 52:-0.0531012, 53:-0.0365446 }
        
        y_vec[4] = -1.9706
        
        w_cache_[4] = { 0:-0.329017, 1:-0.362123, 2:-0.609502, 3:-0.245089, 4:0.135473, 5:-0.382766, 6:0.0944758, 7:0.167531, 8:0.0381152, 9:0.0785147, 10:-0.825952, 11:-0.390477, 12:-0.830045, 13:-0.243419, 14:-0.0146887, 15:-0.0966675, 16:-0.025914, 17:-0.0879826, 18:-0.00230601, 19:-0.111343, 20:-0.0131886, 21:0, 22:-0.0588903, 23:-0.187986, 24:-0.177397, 25:-0.235153, 26:-0.0633859, 27:0, 28:0, 29:-0.0128674, 30:-0.0442193, 31:-0.023239, 32:-0.0506758, 33:-0.0759166, 34:0, 35:-0.277488, 36:-0.354464, 37:0.124518, 38:0, 39:0.532644, 40:0, 41:0, 42:-0.44313, 43:0.0922977, 44:-0.178971, 45:-0.071664, 46:-0.241847, 47:-0.0183509, 48:-0.0118131, 49:0, 50:0, 51:-0.0724332, 52:-0.0500657, 53:-0.0373102 }
        
        y_vec[5] = -0.540319
        
        w_cache_[5] = { 0:-1.29342, 1:-0.0412769, 2:-0.0984066, 3:-0.0476152, 4:0.324678, 5:0.0803213, 6:0.0921855, 7:-0.00311152, 8:-0.0594161, 9:-0.168614, 10:-1.21136, 11:-0.23644, 12:-0.973712, 13:0.252509, 14:-0.0878088, 15:0.0709505, 16:-0.110879, 17:0.0668006, 18:-0.0177562, 19:0.303115, 20:-0.00575582, 21:0, 22:-0.0678261, 23:0.103707, 24:-0.203565, 25:-0.20494, 26:-0.11165, 27:0, 28:0, 29:0.30184, 30:-0.0383038, 31:-0.0158276, 32:-0.0206919, 33:-0.0473019, 34:0, 35:-0.204264, 36:-0.251854, 37:-0.158631, 38:0, 39:-0.0493676, 40:0, 41:0, 42:-0.384685, 43:-0.188743, 44:-0.14205, 45:-0.30339, 46:-0.272919, 47:-0.0224024, 48:-0.00337456, 49:0, 50:0, 51:-0.0435229, 52:-0.0403268, 53:-0.01758 }
        
        y_vec[6] = -3.18516
        
        w_cache_[6] = { 0:2.169, 1:-0.0386469, 2:-0.187937, 3:-0.0486434, 4:-0.232442, 5:0.249379, 6:-0.175115, 7:-0.374052, 8:0.0172173, 9:0.286413, 10:-1.14096, 11:-0.599187, 12:-0.0571573, 13:-0.051879, 14:-0.00272957, 15:-0.0325815, 16:-0.00674746, 17:-0.0457624, 18:-0.000694955, 19:-0.0186994, 20:-0.0133817, 21:0, 22:-0.00863092, 23:-0.0932004, 24:-0.0810231, 25:-0.140895, 26:-0.0914675, 27:0, 28:0, 29:-0.00198982, 30:-0.0113531, 31:-0.0034718, 32:-0.105409, 33:-0.103993, 34:0, 35:-0.481471, 36:-0.547005, 37:-0.460263, 38:0, 39:-0.0402379, 40:0, 41:0, 42:-0.323404, 43:-0.243114, 44:-0.52065, 45:-0.411668, 46:-0.573006, 47:-0.0666031, 48:-0.100697, 49:0, 50:0, 51:0.910116, 52:0.914921, 53:0.855931 }
        
        ref_result = { 0:0.0840387,  1:0.875732,  2:0.0282205,  3:0.00296929,  4:0.00167768,  5:0.00701246,  6:0.000498008 }
        # =================================        

        input_weight_sparse_matrix = w_cache_
       
        predicted_labelization = Predict (input_data_for_prediction_sparse_vector, input_weight_sparse_matrix, one_based=False)
        
        for label in ref_result.keys():
            computed_result_item = predicted_labelization[label]
            ref_result_item = ref_result[label]
            self.assertEqual(self.floatTruncatedString(computed_result_item, tested_precision), self.floatTruncatedString(ref_result_item, tested_precision), 'Predict did not compute equivalent values for label %s' % label)
        
    def test_Predict2 (self):
        tested_precision = 4
        
        # data copied from a Petuum MLR run
        # =================================
        
        sample = { 0:1.27381, 1:1.0218, 2:-1.08144, 3:0.426112, 4:0.0271012, 5:0.697675, 6:-0.26709, 7:0.944866, 8:0.874575, 9:-0.34156, 10:1, 52:1}
        
        w_cache_ = {}
        w_cache_[0] = {0:1.57285, 1:0.0694593, 2:-0.109966, 3:-0.147938, 4:-0.220996, 5:-0.225058, 6:-0.186356, 7:-0.349958, 8:0.0675006, 9:0.127393, 10:2.29787, 11:0.559457, 12:1.82041, 13:-0.0297298, 14:-0.00164359, 15:-0.0872096, 16:-0.00506236, 17:-0.112912, 18:-0.000310377, 19:-0.0102707, 20:-0.0898989, 21:0, 22:0.26352, 23:0.0704738, 24:-0.0456998, 25:0.064407, 26:0.286278, 27:0, 28:0, 29:-0.00537808, 30:-0.0567078, 31:-0.0188949, 32:-0.0411028, 33:0.602116, 34:0, 35:0.956415, 36:1.35191, 37:0.0588544, 38:0, 39:-0.159712, 40:0, 41:0, 42:0.841279, 43:0.288459, 44:1.05036, 45:0.35092, 46:0.657914, 47:-0.11205, 48:0.131641, 49:0, 50:0, 51:-0.341685, 52:-0.637624, 53:-0.600382}
        w_cache_[1] = {0:-0.391749, 1:-0.109464, 2:0.199008, 3:0.128013, 4:0.00323021, 5:0.0626253, 6:-0.0445322, 7:0.152034, 8:0.0984246, 9:0.0279259, 10:3.12362, 11:1.1626, 12:2.31846, 13:0.0513702, 14:-0.024076, 15:-0.402193, 16:-0.249233, 17:0.0517815, 18:-0.0103553, 19:0.156391, 20:0.13695, 21:0, 22:-0.028417, 23:0.665782, 24:0.749364, 25:0.874561, 26:0.353164, 27:0, 28:0, 29:-0.186114, 30:-0.078449, 31:0.067115, 32:0.258608, 33:-0.296973, 34:0, 35:0.416756, 36:0.297612, 37:0.676403, 38:0, 39:-0.0103437, 40:0, 41:0, 42:1.0504, 43:0.395512, 44:0.0908599, 45:1.05778, 46:1.01611, 47:0.252684, 48:-0.00928758, 49:0, 50:0, 51:-0.317954, 52:-0.149885, 53:-0.148498}
        w_cache_[2] = {0:-1.70118, 1:0.467355, 2:0.682311, 3:0.288705, 4:-0.0545734, 5:0.0562165, 6:0.210472, 7:0.3959, 8:-0.136595, 9:-0.342393, 10:-1.17166, 11:-0.231315, 12:-0.922707, 13:0.205381, 14:0.148955, 15:0.607977, 16:0.421293, 17:0.139741, 18:0.0422017, 19:-0.274741, 20:-0.00390243, 21:0, 22:-0.0783909, 23:-0.399449, 24:-0.194903, 25:-0.209581, 26:-0.325556, 27:0, 28:0, 29:-0.087401, 30:0.240883, 31:-0.00854897, 32:-0.0107899, 33:-0.0325198, 34:0, 35:-0.209817, 36:-0.264754, 37:-0.140906, 38:0, 39:-0.0241301, 40:0, 41:0, 42:-0.36725, 43:-0.199386, 44:-0.139007, 45:-0.311626, 46:-0.344261, 47:-0.0151455, 48:-0.00179589, 49:0, 50:0, 51:-0.0386788, 52:-0.0285282, 53:-0.0102782}
        w_cache_[3] = {0:-0.0497306, 1:-0.0262774, 2:0.0391258, 3:0.0067286, 4:0.0223313, 5:0.176518, 6:-0.00117602, 7:0.0184386, 8:-0.00812272, 9:0.0281463, 10:-1.18557, 11:-0.334488, 12:-1.28968, 13:-0.197452, 14:-0.0121121, 15:-0.0657811, 16:-0.0184359, 17:-0.0605964, 18:-0.00300832, 19:-0.0665959, 20:-0.00967786, 21:0, 22:-0.0239418, 23:-0.168953, 24:-0.088551, 25:-0.156389, 26:-0.0660761, 27:0, 28:0, 29:-0.00674275, 30:-0.0199724, 31:-0.00663435, 32:-0.0333106, 33:-0.0560405, 34:0, 35:-0.231807, 36:-0.261951, 37:-0.151999, 38:0, 39:-0.0223591, 40:0, 41:0, 42:-0.396646, 43:-0.178213, 44:-0.155276, 45:-0.31165, 46:-0.24147, 47:-0.0186563, 48:-0.00867917, 49:0, 50:0, 51:-0.0808708, 52:-0.0484575, 53:-0.0363236}
        w_cache_[4] = {0:-0.294256, 1:-0.241323, 2:-0.489575, 3:-0.16506, 4:0.158085, 5:-0.364008, 6:0.129365, 7:0.150854, 8:-0.00965356, 9:0.036678, 10:-0.757068, 11:-0.370731, 12:-0.943745, 13:-0.246125, 14:-0.0151784, 15:-0.090683, 16:-0.027033, 17:-0.0715896, 18:-0.00320985, 19:-0.105583, 20:-0.0123772, 21:0, 22:-0.0527984, 23:-0.183354, 24:-0.146564, 25:-0.223797, 26:-0.0591351, 27:0, 28:0, 29:-0.0114991, 30:-0.0349733, 31:-0.0164463, 32:-0.04274, 33:-0.0674328, 34:0, 35:-0.258799, 36:-0.32711, 37:0.140729, 38:0, 39:0.279865, 40:0, 41:0, 42:-0.42886, 43:0.109795, 44:-0.175731, 45:-0.061254, 46:-0.241827, 47:-0.0188563, 48:-0.010432, 49:0, 50:0, 51:-0.0793508, 52:-0.0450179, 53:-0.0364319}
        w_cache_[5] = {0:-1.28186, 1:-0.0771625, 2:-0.107176, 3:-0.0580713, 4:0.324977, 5:0.0669998, 6:0.0686197, 7:-0.00596087, 8:-0.0379072, 9:-0.155226, 10:-1.20314, 11:-0.228322, 12:-0.944704, 13:0.266627, 14:-0.0925455, 15:0.0686371, 16:-0.115274, 17:0.0888796, 18:-0.0242764, 19:0.31632, 20:-0.00637828, 21:0, 22:-0.0704635, 23:0.10408, 24:-0.195856, 25:-0.206828, 26:-0.104659, 27:0, 28:0, 29:0.299381, 30:-0.0391435, 31:-0.0141439, 32:-0.0208168, 33:-0.0461231, 34:0, 35:-0.193, 36:-0.255137, 37:-0.158906, 38:0, 39:-0.0346222, 40:0, 41:0, 42:-0.376708, 43:-0.185286, 44:-0.147475, 45:-0.302834, 46:-0.270651, 47:-0.0218629, 48:-0.00357756, 49:0, 50:0, 51:-0.0477568, 52:-0.0354876, 53:-0.0170225}
        w_cache_[6] = {0:2.14587, 1:-0.0827665, 2:-0.212941, 3:-0.0521737, 4:-0.232342, 5:0.22915, 6:-0.175691, 7:-0.361429, 8:0.0254535, 9:0.277935, 10:-1.1177, 11:-0.55954, 12:-0.0534054, 13:-0.0517352, 14:-0.00350427, 15:-0.0313808, 16:-0.00644172, 17:-0.0359169, 18:-0.00108398, 19:-0.0159616, 20:-0.014784, 21:0, 22:-0.00984743, 23:-0.0905288, 24:-0.0789174, 25:-0.144248, 26:-0.0847862, 27:0, 28:0, 29:-0.00231095, 30:-0.0118617, 31:-0.00254349, 32:-0.110065, 33:-0.103576, 34:0, 35:-0.482106, 36:-0.543641, 37:-0.425676, 38:0, 39:-0.0289045, 40:0, 41:0, 42:-0.326991, 43:-0.232817, 44:-0.525721, 45:-0.424829, 46:-0.57828, 47:-0.0662991, 48:-0.0979263, 49:0, 50:0, 51:0.90543, 52:0.944478, 53:0.848658}
        
        y_vec = { 0:3.36225, 1:2.47807, 2:-3.1514, 3:-1.23889, 4:-1.12705, 5:-2.8077, 6:2.47001}
        y_vec_after_softmax = { 0:0.541248, 1:0.223566, 2:0.000802722, 3:0.00543463, 4:0.00607768, 5:0.00113194, 6:0.221772}
        
        # =================================        

        input_data_for_prediction_sparse_vector = sample        
        input_weight_sparse_matrix = w_cache_
        ref_result = y_vec_after_softmax
       
        predicted_labelization = Predict (input_data_for_prediction_sparse_vector, input_weight_sparse_matrix, one_based=False)        

        for label in ref_result.keys():
            computed_result_item = predicted_labelization[label]
            ref_result_item = ref_result[label]
            self.assertEqual(self.floatTruncatedString(computed_result_item, tested_precision), self.floatTruncatedString(ref_result_item, tested_precision), 'Predict did not compute equivalent values for label %s' % label)
 
        
        
           
        
if __name__ == '__main__':
    # not expected to by run
    pass