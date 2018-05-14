import logging
_logger = logging.getLogger(__name__)

class LightSVMTrainMetaExtentions():
    
    '''
    classdocs: TbD
    '''
    
    _num_train_total = None
    _num_train_this_partition = None
    _feature_dim = None
    _num_labels = None
                     
    _feature_one_based = None
    _label_one_based = None
    
    # unhandled constants
    _snappy_compressed = 0    

    def __init__(self,
                 k_num_train_total,
                 k_num_train_this_partition,
                 k_feature_dim,
                 k_num_labels,
                 k_feature_one_based = False,
                 k_label_one_based = False):
        '''
        Constructor
        '''
        
        self._num_train_total = k_num_train_total
        self._num_train_this_partition = k_num_train_this_partition
        self._feature_dim = k_feature_dim
        self._num_labels = k_num_labels
        self._feature_one_based = k_feature_one_based
        self._label_one_based = k_label_one_based        
        
    def dump_svmlight_metafile(self, libSVMMetaFileName, comment=None):
        
        #   
        # sqving "meta" file
        #
        _logger.debug ('Writing "meta" params to file : {}'.format(libSVMMetaFileName))
        
        if self._feature_one_based:
            feature_one_based = 1
        else:
            feature_one_based = 0
    
        if self._label_one_based:
            label_one_based = 1
        else:
            label_one_based = 0
        
        with open (libSVMMetaFileName, 'w') as libSVMMetaFile:
            if comment:
                print ('# {}'.format (comment), file=libSVMMetaFile)
            print ('num_train_total: {}'.format (self._num_train_total), file=libSVMMetaFile)
            print ('num_train_this_partition: {}'.format (self._num_train_this_partition), file=libSVMMetaFile)
            print ('feature_dim: {}'.format (self._feature_dim), file=libSVMMetaFile)
            print ('num_labels: {}'.format (self._num_labels), file=libSVMMetaFile)
            print ('format: libsvm', file=libSVMMetaFile)
            print ('feature_one_based: {}'.format (feature_one_based), file=libSVMMetaFile)        
            print ('label_one_based: {}'.format (label_one_based), file=libSVMMetaFile)
            print ('snappy_compressed: {}'.format (self._snappy_compressed), file=libSVMMetaFile)
            
            
def _cleanup_string_read_from_file (line):
    '''
    to prevent file format problems (Linix/DOS), with string eventual end line
    '''
    cleaned_line = line.rstrip ('\n')

    return (cleaned_line)

def getLightSVMTrainMetaExtentionsFromFile(libSVMMetaFileName):
        
    _logger.debug ('Loading "Train meta" params to file : {}'.format(libSVMMetaFileName))
    
    # TODO: does not check if all values have been provided
    k_num_train_total = None
    k_num_train_this_partition = None
    k_feature_dim = None
    k_num_labels = None
    k_feature_one_based = None
    k_label_one_based = None
    
    with open (libSVMMetaFileName, 'r') as libsvm_meta_file:
        
        while True:
        
            line = libsvm_meta_file.readline()
            if not line:
                break
 
            line = _cleanup_string_read_from_file(line)
            
            lstriped_line = line.lstrip()
            if lstriped_line.startswith ('#'):
                # comment line => ignore
                continue
               
            key_string_from_file, value_string_from_file = line.split(':', maxsplit = 1)
            if key_string_from_file == 'num_train_total':
                k_num_train_total = int(value_string_from_file)
            elif key_string_from_file == 'num_train_this_partition':
                k_num_train_this_partition = int(value_string_from_file)
            elif key_string_from_file == 'feature_dim':
                k_feature_dim = int(value_string_from_file)
            elif key_string_from_file == 'num_labels':
                k_num_labels = int(value_string_from_file)
            elif key_string_from_file == 'format':
                k_format = value_string_from_file
            elif key_string_from_file == 'feature_one_based':
                k_feature_one_based = int(value_string_from_file)
            elif key_string_from_file == 'label_one_based':
                k_label_one_based = int(value_string_from_file)
            elif key_string_from_file == 'snappy_compressed':
                k_snappy_compressed = int(value_string_from_file)
            else:
                _logger.critical('Unknown meta key name: {}'.format(key_string_from_file))
                
    lightsvm_meta_params = LightSVMTrainMetaExtentions (
        k_num_train_total = k_num_train_total,
        k_num_train_this_partition = k_num_train_this_partition,
        k_feature_dim = k_feature_dim,
        k_num_labels = k_num_labels,
        k_feature_one_based = k_feature_one_based,
        k_label_one_based = k_label_one_based)
    
    return (lightsvm_meta_params)
