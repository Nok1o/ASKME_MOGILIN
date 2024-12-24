import os

def static_app(environ, start_response):
    static_root = "/home/nok1o/VK/web/ASKME_MOGILIN"
    
    path = environ.get('PATH_INFO', '').lstrip('/')
    file_path = os.path.join(static_root, path)

    if not os.path.exists(file_path):
        status = '404 Not Found'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b"File not found"]
    
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        
        if file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.jpeg') or file_path.endswith('.jpg'):
            content_type = 'image/jpeg'
        elif file_path.endswith('.png'):
            content_type = 'image/png'
        else:
            content_type = 'application/octet-stream'

        status = '200 OK'
        headers = [('Content-Type', content_type), ('Content-Length', str(len(content)))]
        start_response(status, headers)
        return [content]
    
    except Exception as e:
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [f"Error: {e}".encode('utf-8')]
