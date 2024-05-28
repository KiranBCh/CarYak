import json
from json import JSONDecodeError
import sys
import re
import textwrap
from datetime import datetime, timedelta
from typing import cast, Any, Optional


datetime_pattern = re.compile(r'^(.*?)(?:Z|([+-]\d\d(?::?\d\d)?))?$')


def parse_request(request: dict):
    has_post_data = 'postData' in request

    return {
        'method': request['method'],
        'url': request['url'],
        'headers': {entry['name']: entry['value'] for entry in request['headers'] if entry['name'] not in [':authority', ':scheme', ':method', ':path', 'Host', 'host']},
        'cookies': request['cookies'],
        'query_string': {entry['name']: entry['value'] for entry in request['queryString']},
        'type': request['postData']['mimeType'] if has_post_data else '',
        'body': (json.loads(request['postData']['text']) if 'application/json' in request['postData']['mimeType'] else request['postData']['text']) if has_post_data else '',
    }


def parse_response_body_content(response: dict):
    text = response['content'].get('text', '')

    if text and 'application/json' in response['content']['mimeType']:
        try:
            return json.loads(text)
        except JSONDecodeError:
            return text

    else:
        return text


def parse_response_body(response: dict):
    return parse_response_body_content(response) if 'content' in response else ''


def parse_response(response: dict):
    return {
        'redirect_url': response['redirectURL'],
        'status': response['status'],
        'headers': {entry['name']: entry['value'] for entry in response['headers']},
        'cookies': response['cookies'],
        'body': parse_response_body(response),
    }


def entry_timing(entry: dict):
    return datetime.fromisoformat(cast(str, datetime_pattern.match(entry['startedDateTime']))[1]) + timedelta(milliseconds=entry['timings'].get('_blocked_queueing', 0))


def main(file_name: str, pure_requests_str: str = 'false'):
    pure_requests = pure_requests_str == 'true'

    user_agent_header_pattern = re.compile(r'(\s*)("(?:[Uu]ser-[Aa]gent|[Cc]ookie|[Cc]ontent-[Ll]ength)":)')
    url_parameters_pattern = re.compile(r'^(.*?)\?.*')

    json_doc: Optional[dict] = None

    with open(file_name) as file:
        json_doc = json.load(file)

    entries = sorted([{'request': parse_request(entry['request']), 'response': parse_response(entry['response']), 'start_time': entry_timing(entry)} for entry in cast(dict[str, Any], json_doc)['log']['entries'] if entry['response']['status']], key=lambda entry: entry['start_time'])

    for entry in entries:
        request = entry['request']

        if not pure_requests:
            print("Request: ")

        num_indent = 20
        formatted_headers = user_agent_header_pattern.sub(r'\1# \2', json.dumps(request['headers'], indent=4)).replace('\n', '\n' + ' ' * num_indent)
        if 'application/json' in request['type']:
            formatted_data = json.dumps(request['body'], indent=4).replace('\n', '\n' + ' ' * num_indent)

            print(textwrap.dedent(
                f'''\
                yield scrapy.http.JsonRequest(
                    method='{request['method']}',
                    url='{request['url']}',
                    headers={formatted_headers},
                    data={formatted_data},
                )
                '''
            ))

        # elif request['method'] == 'POST':
        #     newline = '\n'
        #     carriage_return = '\r'
        #     newline_chars = '\\n'
        #     carriage_return_chars = '\\r'
        #     print(textwrap.dedent(
        #         f'''\
        #         yield scrapy.http.FormRequest(
        #             method='{request['method']}',
        #             url='{request['url']}',
        #             headers={formatted_headers},
        #             formdata='{request['body'].replace(newline, newline_chars).replace(carriage_return, carriage_return_chars)}',
        #         )
        #         '''
        #     ))

        elif request['method'] != 'GET':
            formatted_body = request['body'].replace('\n', '\\n').replace('\r', '\\r')
            print(textwrap.dedent(
                f'''\
                yield scrapy.Request(
                    method='{request['method']}',
                    url='{request['url']}',
                    headers={formatted_headers},
                    body='{formatted_body}',
                )
                '''
            ))

        elif request['query_string']:
            formatted_url = url_parameters_pattern.sub(r'\1', request['url'])
            formatted_data = json.dumps(request['query_string'], indent=4).replace('\n', '\n' + ' ' * num_indent)

            print(textwrap.dedent(
                f'''\
                yield scrapy.http.FormRequest(
                    method='{request['method']}',
                    url='{formatted_url}',
                    headers={formatted_headers},
                    formdata={formatted_data},
                )
                '''
            ))

        else:
            print(textwrap.dedent(
                f'''\
                yield scrapy.Request(
                    method='{request['method']}',
                    url='{request['url']}',
                    headers={formatted_headers},
                )
                '''
            ))

        if not pure_requests:
            print("Response: ")
            print(json.dumps(entry['response'], indent=4))
            print()
            print()


if __name__ == '__main__':
    main(*sys.argv[1:])
