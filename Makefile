POETRY_TEXT='\#!/bin/sh\ncd $(PWD)\npoetry run python main.py'
PIP_TEXT='\#!/bin/sh\ncd $(PWD)\npython main.py'

runner:
	echo $(POETRY_TEXT) > cpu_monitor.sh

create_pip_script:
	echo $(PIP_TEXT) > cpu_monitor.sh
