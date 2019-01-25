import sys

import pandas as pd
import sklearn.feature_extraction
import sklearn.datasets
import sklearn.preprocessing

import csv

from datetime import datetime

df = pd.read_csv('samples/Orange4Home/in/filtered_states_orange4home.csv', header=0, sep=',')
#!!                 names=['labels', 'f1', 'f2', 'f3'])   # columns names if no header
# df = pd.read_csv('samples/input_test/csv2libsvm_example.csv', header='infer', sep=',', verbose=True)

                
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



#!!!X_df = df.loc[:, 'bathroom_shower_coldwater_instantaneous':'kitchen_washingmachine_partial_energy']
X_df = df.loc[:, used_features]
y_df = df[['label']]


#
# create vectorizers
#

feature_vectorizer = sklearn.feature_extraction.DictVectorizer(sparse=False, sort=False)
# enumerate all possible feature values
#!!feature_mapper = feature_vectorizer.fit ([{'f1':0}, {'f1':1}, {'f2':0}, {'f2':1}, {'f3':0}, {'f3':1}])

feature_value_list = []
feature_value_list.append ([{'global_waterheater_status':'ON'}, {'global_waterheater_status':'OFF'}])

feature_mapper = feature_vectorizer.fit ([{'global_waterheater_status':'ON'}, {'global_waterheater_status':'OFF'}])
                                          
matrix_as_dict_list = X_df.to_dict('records')
X = feature_mapper.transform (matrix_as_dict_list)

# ===============================

label_vectorizer = sklearn.feature_extraction.DictVectorizer(sparse=False, sort=False)
# enumerate all possible label values

label_values_dict_list = [
    {'label': 'START:Bathroom|Cleaning'},
    {'label': 'START:Bathroom|Showering'},
    {'label': 'START:Bathroom|Using_the_sink'},
    {'label': 'START:Kitchen|Cleaning'},
    {'label': 'START:Kitchen|Cooking'},
    {'label': 'START:Kitchen|Preparing'},
    {'label': 'START:Kitchen|Washing_the_dishes'},
    {'label': 'START:Living_room|Cleaning'},
    {'label': 'START:Living_room|Computing'},
    {'label': 'START:Living_room|Eating'},
]

label_list = [
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

label_encoder = sklearn.preprocessing.LabelEncoder()
label_encoder.fit(label_list)

#!!! label_as_vector = label_encoder.transform(['START:Bathroom|Cleaning', 'START:Living_room|Eating'])

y_df_as_list = y_df['label'].tolist()
labels_as_vector = label_encoder.transform (y_df_as_list)
y = labels_as_vector



with open ('samples/Orange4Home/out/states_orange4home_libsvm.txt', 'wb') as libSVMFile:
    
    now = datetime.now()
    hr_now = now.strftime("%A %d/%m/%Y %Hh%M")    
    
    sklearn.datasets.dump_svmlight_file(X=X, y=y, f=libSVMFile, zero_based=True, comment='Generated at: {}'.format (hr_now), query_id=None, multilabel=False)
         

print ("Transformation ended")

sys.exit(0)


