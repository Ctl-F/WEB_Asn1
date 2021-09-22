from http.server import HTTPServer, BaseHTTPRequestHandler


"""
Plan:
    0-Requirements:
        * Host blog website on local host
        * Make it responsive to a wide array of requests
        * Use http.server library
        * Must be a subclass of BaseHTTPRequestHandler
        * Must return a complete and correct HTTP Response.
        * Must include following headers:
            * [Server] followed by id string
            * [Date] followed by current time and date
            * Connection: close
            * Cache-Control: max-age=x
            * Content-Length : Required for resources on disk
            * Content-Type: should be text/html
            * Location: only for 301 redirect responses
        * Gracefully complete almost complete resource names using 301 responses.
        
        * path: / should redirect to index.html using a 301 response.
        * Following Files should return about.html:
            * about
            * about.html
            * bio
            * bio.html
            * anything starting with "bio"
        * /tips and /help results in 301 --> techtips
        * favicon (/favicon.ico) (32x32)
        * /debugging --> on the fly
            * Server's version string
            * current date and time
            * client ip address and port number
            * path requested by client
            * HTTP Request type
            * HTTP version of the request
            * Ordered list of HTTP Request Headers
        * 418 I'm a teapot (/teapot)
        * 403 forbidden (/forbidden)
        * all other requests result in 404 response
    1-Analysis:
        * This is going to require a lot of generalization, and to be done right we should implement some sort
            of easy way to generate responses.
        * We need to have access to the local files (html and resource files like the favicon)
    2-Design:
        * Response class (probably)
        * store files in a root/ folder
        * exception action class
        * request first searches of filename, then filename.html, then checks for any exception matches
        * [GotRequest] -> Match To Type ---> Response
        
    3-Implementation:
        * Implemented
    4-Testing & Debugging:
        *
    5-Deployment:
        *
    6-Maintenance:
        *
"""




class CS2610Assn1(BaseHTTPRequestHandler):
    def do_GET(self):

        path = self.path;
        self.send_error(404);

        return;


print("Entered file");

if __name__ == '__main__':
    server_address = ('localhost', 8000)
    print(f"Serving from http://{server_address[0]}:{server_address[1]}")
    print("Press Ctrl-C to quit\n")
    try:
        HTTPServer(server_address, CS2610Assn1).serve_forever()
    except KeyboardInterrupt:
        print(" Exiting")
        exit(0)