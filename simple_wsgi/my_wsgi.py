def simple_app(environ, start_response):
    query_params = environ.get('QUERY_STRING', '')
    print(query_params)
    get_params = dict(pair.split('=') for pair in query_params.split('&') if '=' in pair)
    print('GET params are:', get_params)

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError, TypeError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
    post_params = dict(pair.split('=') for pair in request_body.split('&') if '=' in pair)

    body = f"GET params: {get_params}\nPOST params: {post_params}"
    body = body.encode('utf-8')

    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(body))),
    ]
    start_response(status, response_headers)
    return [body]

application = simple_app
