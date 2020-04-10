from python:3-alpine

run pip install sopel inflect pytest-mock mock pytest

copy etc/entrypoint.sh /home/hellmuth/entrypoint.sh

copy tests /home/hellmuth/tests

copy test.py /home/hellmuth

run adduser -u 1000 -D hellmuth

run chown -R hellmuth /home/hellmuth

user hellmuth

entrypoint ["/home/hellmuth/entrypoint.sh"]
