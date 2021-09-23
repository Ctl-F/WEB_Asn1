from http.server import HTTPServer, BaseHTTPRequestHandler
import os.path as path;
import mimetypes;
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
        * This is going to require a lot of generalization
        * Request Handler class (base class for basic functionality and subclasses for each exception)
        * We need to have access to the local files (html and resource files like the favicon)
    2-Design:
        * Request handler class
        * [GotRequest] -> Match To Type ---> Response
        * Request Handler : TryRequest(url) -> bool
            * returns true to consume the request, and is expected to actually perform the operation
            * returns false to pass the response to the next handler
            * if none return true throw a 404
        * BaseFileRequest : Handles correct file responses
        * RootExceptionRequest: handles the case of and empty(/) path
        * SpecialRequest : handles /teapot, /forbidden, etc. Things that aren't actually files
        * GraceExceptionRequest : checks to see if it's an incomplete name and if it can find the html file will send a redirect
        * BIOExceptionRequest : checks if a BIO request has been made to redirect to about.html
        
    3-Implementation:
        * Implemented below
    4-Testing & Debugging:
        * I tested with nc and opera and chrome. nc more in the beginning and the browsers later on when my
            server was working better.
        * tested an array of inputs including /teapot, /, /about, /bio, /forbidden, /debugging, etc
        * favicon appears in browser
        * biggest issue was figuring out the correct order to build the http request for it to be "valid"
    5-Deployment:
        *
    6-Maintenance:
        *
"""



class CS2610Assn1(BaseHTTPRequestHandler):

    def SendResponse(self, code: int, message, extraHeaders = {}):
        #data = bytes("%s\r\n" % message, "utf-8");

        if type(message) == str:
            message = bytes(message, "UTF-8");

        self.send_response(code);
        self.SetBaseHeaders();

        #self.send_header("Content-Length", len(message));
        #self.send_header("Content-Type", "text/html; charset=UTF-8");
        
        for extraHeader in extraHeaders:
            self.send_header(extraHeader, extraHeaders[extraHeader]);
        
        self.end_headers();

        self.wfile.write(message);

        
        

    def SetBaseHeaders(self):
        self.send_header("Server", f"{self.version_string()}");
        self.send_header("Date", self.date_time_string());
        self.send_header("Connection", "close");
        self.send_header("Cache-Control", str(600));

    def do_GET(self):
        if not hasattr(self, "handles"):
            self.handles = [
                BaseFileHandler(self),
                SpecialDirectoryHandler(self),
                RootFileExceptionHandler(self),
                GraceCheckFileExceptionHandler(self),
                BIOExceptionHandler(self)
            ];

        print(f"GET called from {self.client_address[0]}:{self.client_address[1]} FOR [{self.path}]");
        for handle in self.handles:
            if handle.TryRequest(self.path):
                break;
        else:
            self.send_error(404);

        return;


class UrlHandler:
    def __init__(self, requestHandler: CS2610Assn1):
        self.rhHandle = requestHandler;
    
    #@Override
    # returns true if the url matches this exception and has been handled
    def TryRequest(self, url: str) -> bool:
        return False;

    def SendFile(self, filePath: str):
        with open(filePath, "rb") as p:
            data = p.read();
            self.rhHandle.SendResponse(200, data, {"Content-Type":mimetypes.guess_type(filePath)[0], "Content-Length":len(data)});


class BaseFileHandler(UrlHandler):
    def TryRequest(self, url: str) -> bool:
        testPath = f".{url}";

        #do file check
        if path.isfile(testPath):
            print(f"Valid request for {testPath} received");
            self.SendFile(testPath);
            return True;
        
        return False;

class GraceCheckFileExceptionHandler(UrlHandler):
    def TryRequest(self, url: str) -> bool:
        testPath = f".{url}";

        #do grace check
        if not path.isfile(testPath):
            testPath = f"{testPath}.html";
        
        if path.isfile(testPath):
            print(f"Grace Request for {url} received");
            self.rhHandle.SendResponse(301, "", {"Location": testPath[1:]});
            return True;
        return False;


class RootFileExceptionHandler(UrlHandler):
    def TryRequest(self, url: str) -> bool:
        #root to index redirect
        if url == "/" or url == "":
            self.rhHandle.SendResponse(301, "", {"Location": "/index.html"});
            return True;
        return False;


class BIOExceptionHandler(UrlHandler):
    def TryRequest(self, url: str) -> bool:
        # if the url starts with "bio" redirect to about.html
        if url[1:4].lower() == "bio":
            self.rhHandle.SendResponse(301, "", {"Location": "/about.html"});
            return True;
        return False;


#Handle special directory requests
class SpecialDirectoryHandler(UrlHandler):
    def TryRequest(self, url: str) -> bool:
        if url == "/teapot":   
            self.rhHandle.send_error(418);
            self.rhHandle.end_headers();
            return True;

        elif url == "/forbidden":
            self.rhHandle.send_error(403);
            self.rhHandle.end_headers();
            return True;
        
        elif url == "/help" or url == "/tips":
            #send redirect to techtips
            self.rhHandle.SendResponse(301, "", {"Location": "/techtips+css.html"});
            return True;
        
        elif url == "/debugging":
            #generate header list html
            headerInfo = "<ol>";
            for key, value in self.rhHandle.headers:
                headerInfo = "%s<li>%s - %s</li>" % (headerInfo, key, value);
            headerInfo += "</ol>";

            #Send the the debugging webpage with inserted information
            self.rhHandle.SendResponse(200,
            f"""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                <meta charset="utf-8" />
                <link rel="stylesheet" type="text/css" href="style.css" />
                <title>Debug Information</title>
                </head>
                <body>
                    <div id="Side-Bar">
                        <a href="index.html">My Blog</a>
                        <a href="techtips+css.html">My Tech Tips (Now with css!)</a>
                        <a href="techtips-css.html">My Tech Tips (old)</a>
                        <a href="about.html">About Me</a>
                    </div>
                    <div id="Main-Body">
                        <h1>Debug Info - {self.rhHandle.date_time_string()}</h1>
                        <h2>Server - {self.rhHandle.version_string()}</h2>
                        <p>Client Address - <b>{self.rhHandle.client_address[0]}</b>:<i>{self.rhHandle.client_address[1]}</i></p>
                        <p>Request Path - {self.rhHandle.path}</p>
                        <p>Request Type - {self.rhHandle.command}</p>
                        <p>Request Version - {self.rhHandle.request_version}</p>
                        <h3>Request Headers</h3>
                        %s
                    </div>
                </body>
            </html>
            """ % headerInfo
            );
            return True;

        return False;



if __name__ == '__main__':
    server_address = ('localhost', 8080)
    print(f"Serving from http://{server_address[0]}:{server_address[1]}")
    print("Press Ctrl-C to quit\n")
    try:
        HTTPServer(server_address, CS2610Assn1).serve_forever()
    except KeyboardInterrupt:
        print(" Exiting")
        exit(0)