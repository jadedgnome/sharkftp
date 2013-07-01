'''
sharkFTP v1.00 - My Portable FTP Server utilizing pyftpdlib.

Description:
Originally, this program read from a config file and handled 
multiple users, perm levels, different shares, etc. 

However, this variant is used for a quick FTP solution that is 
cross platform; it's for quick jobs - not meant to hold up an 
enterprise FTP service by any means. Use at your own risk.
'''

#Imports
import os,random,re,socket,stat,string,sys

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

#Handling for Python 3 compatibility.
if sys.version_info >= (3, 0):
  from urllib.request import urlopen
else:
	from urllib import urlopen

#Constants
MSG_LOGIN = "Welcome to the Danger Zone!"
MSG_QUIT = "See Ya."
PORT = 434

#Creates a share directory in CWD if it doesn't already exist.
def initShareDir(sharename):
	if not os.path.exists(sharename):
		os.makedirs(sharename)
		os.chmod(sharename,stat.S_IRWXO)

#Gets the bind IP for supporting an external connection.
def getBindIP():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(('google.com', 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip

#Gets the External IP to share.
def getExternalIP():
    data = str(urlopen('http://checkip.dyndns.com/').read())
    return str(re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1))

#Generates temporary alphanumeric credentials to share.
def genCreds():
	username = ''.join(random.choice(string.ascii_uppercase) for x in range(5))
	password = ''.join(random.choice(string.digits) for x in range(4))
	return username,password

#Sets up the authorizer, loads the user table, inits the ftp handler
def createFTPServer(username,password):
	authorizer = DummyAuthorizer()
	authorizer.add_user(username,password,"./share/",perm="elradfmw",\
		msg_login=MSG_LOGIN,msg_quit=MSG_QUIT)

	#Set up the handler object and link it to our authorizer.
	handler = FTPHandler
	handler.authorizer = authorizer

	return handler,authorizer

#Entry point and runtime.
def main():

	#Create a portable sharing directory
	initShareDir("./share/")

	#Create our temporary credentials.
	username,password = genCreds()
	
	#Create our ftp server handler and authorizer with temp creds.
	handler,authorizer = createFTPServer(username,password)
	
	#Creating the actual connection.
	server = FTPServer((getBindIP(),PORT),handler)
	
	#Sharing connection info with user.
	print ("---------------------------------------------")
	print("External Access: %s port %s" % (getExternalIP(),PORT))
	print("Username: %s" % username)
	print("Password: %s" % password)
	print("Home: ./share/")
	print ("---------------------------------------------")
	
	#Keep server running until terminated.
	server.serve_forever()

if __name__ == '__main__':
	main()
