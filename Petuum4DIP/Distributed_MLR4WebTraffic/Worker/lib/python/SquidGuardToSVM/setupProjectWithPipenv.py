import re
import sys
import os

os.putenv("PIPENV_VENV_IN_PROJECT", "1")
os.putenv("http_proxy", "http://proxy:8080")
os.putenv("https_proxy", "http://proxy:8080")

PATH = os.getenv('PATH')
new_PATH = sys.base_exec_prefix + os.pathsep + os.path.join(sys.base_exec_prefix, 'Scripts') + os.pathsep + PATH
os.putenv("PATH", new_PATH)

pipenv_command = sys.executable + ' -m pipenv ' + '--python ' + sys.executable

command =  pipenv_command + ' install --dev'

if __name__ == '__main__':
    status = os.system(command)
    sys.exit (status)
    
