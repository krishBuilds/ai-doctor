import http.server
import socketserver
import os

# Change to the directory with our static files
os.chdir(r'C:\Users\krish\source\repos\ai-doctor')

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/templates/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

Handler = MyHTTPRequestHandler

print(f"Starting simple HTTP server on port {PORT}")
print(f"Access your AI Doctor Avatar at: http://localhost:{PORT}")
print("Note: This is a simple file server - full Django features need Django server")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.shutdown()