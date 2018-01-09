import json
import os
import re
import requests
from chalice import Chalice, Response
from jinja2 import Environment, FileSystemLoader
from urllib.parse import parse_qs

app = Chalice(app_name='x2chatwork')

@app.route('/{path}', methods=['POST'], content_types=['application/x-www-form-urlencoded', 'application/json'])
def index(path):
    try:
        config = __load_config(path)
        template = __load_template(config)
        payloads = parse_qs(app.current_request.raw_body.decode()).get('payload')
        payload = app.current_request.json_body if payloads is None else json.loads(payloads[0])
        requests.post(
            'https://api.chatwork.com/v2/rooms/' + str(config['room_id']) + '/messages',
            {'body': template.render(json=payload, base_url=__get_base_url(config))},
            headers={'X-ChatWorkToken': config['api_token']}
        )
        return Response(body='ok', status_code=200)
    except Exception as e:
        app.log.error(str(type(e)) + ':' + str(e))
        return Response(body='error', status_code=500)

def __load_config(path):
    config_file = open(os.environ['X2_CONFIG_FILE_PATH'], 'r')
    config = json.load(config_file)[path]
    config_file.close()
    return config

def __load_template(config):
    env = Environment(loader=FileSystemLoader('./chalicelib/templates/' + config['locale'], encoding='utf8'))
    env.filters['replace'] = __replace
    return env.get_template(config['service'] + __get_event_suffix(config) + '.j2')

def __get_event_suffix(config):
    if config['service'] == 'github':
        return '_' + app.current_request.headers['X-GitHub-Event']
    return ''

def __get_base_url(config):
    if config['service'] == 'backlog':
        return config['base_url']
    return ''

def __replace(subject, pattern, replacement):
    return re.sub(pattern, replacement, subject)
