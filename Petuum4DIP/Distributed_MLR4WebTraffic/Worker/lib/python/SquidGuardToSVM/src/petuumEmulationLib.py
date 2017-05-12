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
    
    sum = vec_as_list[0]
    for i in range(1, len(vec_as_list)):
        sum = LogSum(sum, vec_as_list[i])
        
    return sum


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
    
    sum = 0.0
    for f1_key, f1_value in f1_feature_dict.items():
        f2_value = f2_feature_dict.get(f1_key)
        if f2_value:
            factor = f1_value * f2_value
            sum += factor
       
    return (sum)

# =======================================================================================================


def Predict (attribute_dict, petuum_mlr_computed_label_weights):
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
   
       
    pass
    

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
    
     
    def test_LogSumVec (self):
        tested_precision = 3
        
        sample = [2.32699, 2.70564, 0.70979, -1.65623, -1.32633, -0.59962, -2.18235]
        sample_LogSumVec = 3.34482
        
        sum = LogSumVec(sample)
        diff = (sum - sample_LogSumVec)
        
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
        
if __name__ == '__main__':
    pass