import json
import sys
import re
import textwrap
from functools import partial
from more_itertools import chunked


def convert(arguments):
    url = arguments[1]

    other_arguments = arguments[2:-1] if arguments[-1] == '--compressed' else arguments[2:]

    method = None
    headers = {}
    body = None
    json_data = None

    for option, value in chunked(other_arguments, 2):
        if option in ['-X', '--request']:
            method = value

        elif option in ['-H', '--header']:
            key, key_value = re.compile(r'\s*?:\s*').split(value, maxsplit=1)
            headers[key] = key_value

        elif option == '--data-raw':
            try:
                json_data = json.loads(value)

            except json.decoder.JSONDecodeError:
                body = value

    indent = ' ' * 16

    subs = [
        partial(re.compile(r'("user-agent":)', re.IGNORECASE).sub, r'# \1'),
        partial(re.compile(r'("dnt":)', re.IGNORECASE).sub, r'# \1'),
        partial(re.compile(r'("connection":)', re.IGNORECASE).sub, r'# \1'),
        partial(re.compile(r'("cookie":)', re.IGNORECASE).sub, r'# \1'),
        partial(re.compile(r'("proxy-authorization":)', re.IGNORECASE).sub, r'# \1'),
    ]

    formatted_headers = json.dumps(headers, indent=4).replace('\n', f'\n{indent}')

    for sub in subs:
        formatted_headers = sub(formatted_headers)

    if json_data is not None:
        method = 'POST' if method is None else method

        formatted_json = json.dumps(json_data, indent=4).replace('\n', f'\n{indent}')

        print(textwrap.dedent(
            f'''\
            yield scrapy.http.JsonRequest(
                method='{method}',
                url='{url}',
                headers={formatted_headers},
                data={formatted_json},
            )
            '''
        ))

    elif body is not None:
        method = 'POST' if method is None else method

        body = body.replace('\n', f'\n{indent}')

        print(textwrap.dedent(
            f'''\
            yield scrapy.Request(
                method='{method}',
                url='{url}',
                headers={formatted_headers},
                body={body},
            )
            '''
        ))

    else:
        method = 'GET' if method is None else method

        print(textwrap.dedent(
            f'''\
            yield scrapy.Request(
                method='{method}',
                url='{url}',
                headers={formatted_headers},
            )
            '''
        ))


if __name__ == '__main__':
    convert(sys.argv[1:])
