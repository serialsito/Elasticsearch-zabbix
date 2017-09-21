import requests
import sys
import json


if __name__ == '__main__':
    if sys.argv[1] == 'discovery':
        r = requests.get('http://localhost:9200/_cat/indices?v')
        strings = r.text.strip().split('\n')
        res_data = {'data': []}
        for string in strings[1:]:
            res_data['data'].append({'{#ES_INDEX}': ''.format(string.split()[2])})
        print(json.dumps(res_data))
