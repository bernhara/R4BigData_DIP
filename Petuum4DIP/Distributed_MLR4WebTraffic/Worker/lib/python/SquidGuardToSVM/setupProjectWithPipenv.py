import re
import sys
import os



from pipenv import cli

os.putenv("PIPENV_VENV_IN_PROJECT", "1")
os.putenv("http_proxy", "http://proxy:8080")
os.putenv("https_proxy", "http://proxy:8080")

PATH = os.getenv('PATH')
new_PATH = sys.base_exec_prefix + os.pathsep + os.path.join(sys.base_exec_prefix, 'Scripts') + os.pathsep + PATH
os.putenv("PATH", new_PATH)


command = sys.executable + ' -m pipenv ' + '--python ' + sys.executable + ' install --dev --verbose'

# tt = sys.path
# sys.path.insert(0, os.path.join(sys.base_exec_prefix, 'Scripts'))
# sys.path.insert(0, sys.base_exec_prefix)
# tt = sys.path

pipenv_bin = os.path.join(sys.base_exec_prefix, 'Scripts', 'pipenv')
pipenv_bin = 'pipenv'
pipenv_command = pipenv_bin + ' --python ' + sys.executable

command =  pipenv_command + ' install --dev'

#!!! command = 'set'

status = os.system(command)
sys.exit (status)

redefined_script_name = os.path.join(sys.base_exec_prefix, 'Scripts', 'pipenv')

sys.argv[0] = redefined_script_name

my_args = ['--python', sys.executable, 'install', '--dev', '--verbose']
sys.argv.extend(my_args)

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    status = cli()
    sys.exit(status)
    
