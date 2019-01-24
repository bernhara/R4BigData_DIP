import sys
import os
import subprocess
from sys import stdout

os.putenv("PIPENV_VENV_IN_PROJECT", "1")

# TODO: proxy config should be optional and confirable
os.putenv("http_proxy", "http://proxy:8080")
os.putenv("https_proxy", "http://proxy:8080")

quoted_sys_executable = '"%s"' % sys.executable

# compute additional PATH elements
path_prefix_element_list = [sys.base_exec_prefix, os.path.join(sys.base_exec_prefix, 'Scripts')]
path_prefix = os.pathsep.join(path_prefix_element_list)

# prepend PATH system var with new elements, so that current Python has priority while searching in the PATH
PATH = os.getenv('PATH')
new_PATH = os.pathsep.join ([path_prefix, PATH])
os.putenv("PATH", new_PATH)

# prepare the command to launch
pipenv_launch_command = quoted_sys_executable + ' -m pipenv ' + '--python ' + quoted_sys_executable

# check ifo pipenv environment already exists
check_venv_command = pipenv_launch_command + ' --venv'

p = subprocess.run(check_venv_command, shell=False, check=False, universal_newlines=True)
print ("DONE")
print (p.returncode)
print (stdout)

if p.returncode == 1:

    create_venv_command =  pipenv_launch_command + ' install' 
    p = subprocess.run(create_venv_command, shell=False, check=False, universal_newlines=True)
    
else:
    
    update_venv_command =  pipenv_launch_command + ' sync' 
    p = subprocess.run(update_venv_command, shell=False, check=False, universal_newlines=True)    
    


