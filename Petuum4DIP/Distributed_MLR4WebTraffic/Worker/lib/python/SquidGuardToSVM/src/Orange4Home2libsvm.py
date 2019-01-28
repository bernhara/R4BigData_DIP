import sys

import pandas as pd
import numpy as np
import sklearn.feature_extraction
import sklearn.datasets
import sklearn.preprocessing

import csv

from datetime import datetime

#!! df = pd.read_csv('samples/Orange4Home/in/filtered_states_orange4home.csv', header=0, sep=',')
df = pd.read_csv('samples/Orange4Home/in/states_orange4home_tenlines.csv', header=0, sep=',')


               
used_features = [
#'Time',
'bathroom_shower_coldwater_instantaneous',
'kitchen_washingmachine_partial_energy',
'kitchen_sink_coldwater_total',
'global_waterheater_voltage',
'global_waterheater_partial_energy',
'kitchen_oven_voltage',
'livingroom_presence_table',
'bathroom_sink_coldwater_total',
'bathroom_heater_effective_setpoint',
'bathroom_shower_coldwater_total',
'global_shutters_voltage',
'bedroom_AC_setpoint',
'kitchen_cooktop_current',
'global_waterheater_status',
'kitchen_oven_power',
'entrance_heater_base_setpoint',
'kitchen_dishwasher_voltage',
'livingroom_heater1_base_setpoint',
'livingroom_presence_couch',
'livingroom_heater1_effective_mode',
'bathroom_CO2',
'kitchen_hood_partial_energy',
'bathroom_presence',
'global_pressure_trend_ext',
'global_condition_id_ext',
'global_temperature_feel_ext',
'global_humidity_ext',
'global_wind_speed_ext',
'global_condition_ext',
'global_pressure_ext',
'global_rain_ext',
'global_temperature_ext',
'global_wind_direction_ext',
'global_commonID_ext',
'global_snow_ext',
'global_clouds_ext',
'office_luminosity',
'global_shutters_current',
'global_coldwater_instantaneous',
'livingroom_heater2_effective_mode',
'kitchen_fridge_power',
'kitchen_sink_hotwater_total',
'livingroom_heater2_temperature',
'bathroom_heater_effective_mode',
'global_current',
'global_power_factor',
'global_voltage',
'global_active_power',
'global_gas_total',
'global_active_energy',
'global_frequency',
'bathroom_sink_coldwater_instantaneous',
'bathroom_heater_temperature',
'bedroom_heater2_effective_setpoint',
'bedroom_heater1_temperature',
'entrance_heater_temperature',
'office_presence',
'global_waterheater_total_energy',
'entrance_heater_effective_setpoint',
'livingroom_heater2_base_setpoint',
'livingroom_couch_plug_consumption',
'livingroom_table_luminosity',
'livingroom_tv_plug_consumption',
'livingroom_heater1_effective_setpoint',
'office_desk_plug_consumption',
'bedroom_luminosity',
'kitchen_cooktop_total_energy',
'entrance_heater_effective_mode',
'global_shutters_total_energy',
'livingroom_table_plug_consumption',
'bedroom_CO2',
'bathroom_temperature',
'bedroom_heater1_effective_mode',
'office_tv_plug_consumption',
'livingroom_temperature',
'bathroom_sink_hotwater_total',
'kitchen_humidity',
'kitchen_luminosity',
'bedroom_heater1_effective_setpoint',
'global_shutters_partial_energy',
'kitchen_hood_voltage',
'global_shutters_power',
'kitchen_dishwasher_current',
'livingroom_AC_setpoint',
'kitchen_oven_total_energy',
'kitchen_hood_current',
'bedroom_heater2_effective_mode',
'kitchen_washingmachine_total_energy',
'bathroom_heater_base_setpoint',
'kitchen_cooktop_voltage',
'office_heater_effective_mode',
'global_waterheater_power',
'livingroom_luminosity',
'office_AC_setpoint',
'office_heater_effective_setpoint',
'kitchen_fridge_partial_energy',
'kitchen_sink_hotwater_instantaneous',
'livingroom_heater2_effective_setpoint',
'global_lighting_voltage',
'kitchen_hood_power',
'kitchen_sink_coldwater_instantaneous',
'bathroom_luminosity',
'bedroom_temperature',
'kitchen_dishwasher_partial_energy',
'kitchen_dishwasher_total_energy',
'global_coldwater_total',
'bedroom_humidity',
'kitchen_dishwasher_power',
'kitchen_washingmachine_power',
'bathroom_shower_hotwater_instantaneous',
'kitchen_fridge_total_energy',
'global_waterheater_current',
'bathroom_shower_hotwater_total',
'bedroom_light1',
'bedroom_light2',
'bathroom_light1',
'entrance_light1',
'livingroom_light1',
'staircase_light',
'bedroom_light3',
'toilet_light',
'office_heater_base_setpoint',
'livingroom_light2',
'bedroom_light4',
'walkway_light',
'office_light',
'kitchen_light1',
'bathroom_light2',
'kitchen_CO2',
'kitchen_light2',
'kitchen_oven_current',
'bathroom_humidity',
'global_lighting_total_energy',
'kitchen_fridge_voltage',
'office_heater_command',
'global_heaters_setpoint',
'kitchen_washingmachine_current',
'bedroom_heater1_base_setpoint',
'livingroom_heater1_temperature',
'bedroom_heater2_base_setpoint',
'bedroom_heater2_temperature',
'office_heater_temperature',
'kitchen_hood_total_energy',
'toilet_coldwater_total',
'livingroom_humidity',
'toilet_coldwater_instantaneous',
'kitchen_cooktop_partial_energy',
'kitchen_washingmachine_voltage',
'global_lighting_current',
'bathroom_heater_command',
'bedroom_presence',
'bathroom_sink_hotwater_instantaneous',
'kitchen_fridge_current',
'global_lighting_partial_energy',
'livingroom_CO2',
'kitchen_presence',
'global_lighting_power',
'global_heaters_temperature',
'office_AC_mode',
'kitchen_temperature',
'bedroom_heater1_command',
'kitchen_cooktop_power',
'kitchen_oven_partial_energy',
'bedroom_heater2_command',
'entrance_heater_command',
'livingroom_heater2_command',
'livingroom_heater1_command',
'livingroom_tv_status',
'office_tv_status',
'livingroom_couch_noise',
'office_noise',
'bedroom_noise',
'walkway_noise',
'livingroom_table_noise',
'livingroom_switch1_bottom_left',
'livingroom_shutter2',
'livingroom_shutter3',
'livingroom_shutter4',
'livingroom_shutter5',
'livingroom_switch1_top_right',
'livingroom_switch2_top_right',
'livingroom_shutter1',
'kitchen_cupboard1',
'kitchen_noise',
'kitchen_switch_bottom_right',
'entrance_noise',
'kitchen_switch_top_right',
'entrance_door',
'entrance_switch_left',
'walkway_switch1_bottom_right',
'bedroom_shutter1',
'office_shutter',
'bedroom_shutter2',
'kitchen_fridge_door',
'kitchen_cupboard2',
'kitchen_cupboard3',
'kitchen_cupboard4',
'staircase_switch_left',
'walkway_switch1_bottom_left',
'walkway_switch1_top_left',
'walkway_switch1_top_right',
'walkway_switch2_top_left',
'walkway_switch2_bottom_left',
'walkway_switch2_bottom_right',
'walkway_switch2_top_right',
'bathroom_switch_top_left',
'bathroom_switch_bottom_left',
'bathroom_switch_bottom_right',
'bathroom_switch_top_right',
'bathroom_door',
'bedroom_switch_top_left',
'bedroom_switch_top_right',
'bedroom_switch_bottom_left',
'bedroom_switch_bottom_right',
'bedroom_closet_door',
'bedroom_door',
'office_switch_left',
'office_switch_right',
'office_door',
'staircase_switch_right',
'kitchen_switch_top_left',
'kitchen_switch_bottom_left',
'toilet_switch_left',
'toilet_switch_right',
'bedroom_bed_pressure',
'livingroom_switch2_top_left',
'bathroom_shower_door',
'livingroom_switch1_top_left',
'office_switch_middle',
'kitchen_cupboard5',
'bedroom_switch_middle_left',
'bedroom_drawer1',
'bedroom_drawer2',
'bedroom_switch_middle_right',
'livingroom_window1',
'office_window',
]

#=====================================================================================================================================
#
# imports from SquidGuard example
#
#=====================================================================================================================================

_FEATURE_VALUE_DEFINITION_LIST = []
_FEATURE_VALUE_DEFINITION_LIST.append ( ('global_waterheater_status', (['ON', 'OFF'], None)) )
_FEATURE_VALUE_DEFINITION_LIST.append ( ('livingroom_presence_table', (['ON', 'OFF'], None)) )


_LABEL_LIST = [
    'START:Bathroom|Cleaning',
    'START:Bathroom|Showering',
    'START:Bathroom|Using_the_sink',
    'START:Kitchen|Cleaning',
    'START:Kitchen|Cooking',
    'START:Kitchen|Preparing',
    'START:Kitchen|Washing_the_dishes',
    'START:Living_room|Cleaning',
    'START:Living_room|Computing',
    'START:Living_room|Eating',
]

_LABEL_LIST.append('START:Entrance|Entering')

#---

def get_model_mapping_for_vectorizer ():
    
    global _FEATURE_VALUE_DEFINITION_LIST
    
    feature_and_value_mapping_lists = []
    
    for feature_value_definition in _FEATURE_VALUE_DEFINITION_LIST:
        feature, label_mapping_specification = feature_value_definition
        labels, _ = label_mapping_specification
        feature_label_list = [{feature:label} for label in labels]
        
        feature_and_value_mapping_lists.extend (feature_label_list)
        
    return feature_and_value_mapping_lists  

def init_model_feature_mapper (dense=True):
    
    model_mapper = None
    
    #
    # build model mapper
    #
    
    squid_model_mapping = get_model_mapping_for_vectorizer()
    
    if dense:
    
        # dense version
        
        squid_log_to_dense_vector_mapper = sklearn.feature_extraction.DictVectorizer(sparse=False, sort=False)
        squid_log_to_dense_vector_mapper.fit (squid_model_mapping)
        
        model_mapper = squid_log_to_dense_vector_mapper
    else:
    
        # sparse version
        squid_log_to_sparse_vector_mapper = sklearn.feature_extraction.DictVectorizer(sparse=True, sort=False)
        squid_log_to_sparse_vector_mapper.fit (squid_model_mapping)
        
        model_mapper = squid_log_to_sparse_vector_mapper
    
    return model_mapper

def init_label_encoder (label_name_list):
    
    label_encoder = sklearn.preprocessing.LabelEncoder()
    label_encoder.fit(label_name_list)
    
    
    return label_encoder

#---

Orange4Home_to_vector_mapper = init_model_feature_mapper(dense=True)
label_encoder = init_label_encoder(_LABEL_LIST)

#=====================================================================================================================================
#
#=====================================================================================================================================

# Create X
known_features = [ feature_name for (feature_name, _) in _FEATURE_VALUE_DEFINITION_LIST]

X = None
for feature_name in known_features:

    X_df = df.loc[:, [feature_name]]

    matrix_as_dict_list = X_df.to_dict('records')
    encoded_features = Orange4Home_to_vector_mapper.transform (matrix_as_dict_list)
    if X is None:
        X = encoded_features        
    else:
        X = np.append (X, encoded_features, axis=1)        


# Create y
y_df = df['label']
y_df_as_list = y_df.values
encoded_labels = label_encoder.transform (y_df_as_list)
y = encoded_labels

# ===============================


with open ('samples/Orange4Home/out/states_orange4home_libsvm.txt', 'wb') as libSVMFile:
    
    now = datetime.now()
    hr_now = now.strftime("%A %d/%m/%Y %Hh%M")    
    
    sklearn.datasets.dump_svmlight_file(X=X, y=y, f=libSVMFile, zero_based=True, comment='Generated at: {}'.format (hr_now), query_id=None, multilabel=False)
    

#
# dump feature and label name mapping
#

_label_one_based = False
def dump_labels_to_file (label_encoder, categories_dump_file_name, comment = None):
    
    global _label_one_based
    
    all_label_list = list(label_encoder.classes_)
    
    # TODO: !! Manage label_one_based in dump_labels_to_file
    _label_one_based = 0 # FIXME: !! to remove
    if _label_one_based:
        startIndex = 1
    else:
        startIndex = 0
    
    with open (categories_dump_file_name, 'w') as categoriesDumpFile:
        
        print ('# {}'.format (comment), file=categoriesDumpFile)        
        
        for label in all_label_list:
            transformed_label_array = label_encoder.transform([label])
            transformed_label = transformed_label_array[0]
            print ('{} {}'.format(transformed_label, label), file = categoriesDumpFile)   
            
            
dump_labels_to_file (label_encoder, 'samples/Orange4Home/out/LABELS_states_orange4home_libsvm.txt', 'zero based label list')             
         

print ("Transformation ended")

sys.exit(0)


