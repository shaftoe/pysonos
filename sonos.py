#!/usr/bin/env python
from bottle import route, run, request, response


@route('/destroyawsinstance')
def destroyawsinstance():
    return 'blah'


if __name__ == '__main__':
    run(host='0.0.0.0', port=80, quiet=False)
