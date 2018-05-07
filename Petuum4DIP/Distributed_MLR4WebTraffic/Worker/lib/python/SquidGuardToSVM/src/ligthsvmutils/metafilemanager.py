import logging
_logger = logging.getLogger(__name__)

class LightSVMMetaExtentions():
    
    '''
    classdocs: TbD
    '''
    

    _num_train_total = None
    _num_train_this_partition = None
    _num_test = None
    _feature_dim = None
    _num_labels = None
                     

    _feature_one_based = None
    _label_one_based = None
    
    # unhandled constants
    _snappy_compressed = 0    

    def __init__(self,
                 num_train_total,
                 num_train_this_partition,
                 num_test,
                 feature_dim,
                 num_labels,
                 feature_one_based = False,
                 label_one_based = False):
        '''
        Constructor
        '''
        
        self._num_train_total = num_train_total
        self._num_train_this_partition = num_train_this_partition
        self._num_test = num_test
        self._feature_dim = feature_dim
        self._num_labels = num_labels
        self._feature_one_based = feature_one_based
        self._label_one_based = label_one_based        
        
    def dump_svmlight_metaparamsfile(self, libSVMMetaFileName, comment=None):
        
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
            
