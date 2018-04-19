import re
import sys
import os

os.putenv("PIPENV_VENV_IN_PROJECT", "1")

# TODO: proxy config should be optional and confirable
os.putenv("http_proxy", "http://proxy:8080")
os.putenv("https_proxy", "http://proxy:8080")

quoted_sys_executable = '"%s"' % sys.executable

#!! zz = 'TT'.join('a', 'b')
path_prefix_element_list = [sys.base_exec_prefix, os.path.join(sys.base_exec_prefix, 'Scripts')]

quoted_path_prefix_list = ["\"%s\"" % p for p in path_prefix_element_list]

path_prefix = os.pathsep.join(quoted_path_prefix_list)
path_prefix = os.pathsep.join(path_prefix_element_list)

PATH = os.getenv('PATH')
new_PATH = os.pathsep.join ([path_prefix, PATH])
os.putenv("PATH", new_PATH)

pipenv_launch_command = quoted_sys_executable + ' -m pipenv ' + '--python ' + quoted_sys_executable

command =  '"' + pipenv_launch_command + ' install --dev numpy"' 
#!!command = '"set"'

if __name__ == '__main__':
    status = os.system(command)
    sys.exit (status)
    
