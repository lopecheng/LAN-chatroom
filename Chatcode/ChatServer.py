import socket
import select
from threading import *

class ChatServer:
  def __init__( self, port ):
    self.port = port;

    self.onlinemember = []

    self.srvsock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    self.srvsock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
    self.srvsock.bind((socket.gethostbyname(socket.getfqdn(socket.gethostname())), port) )
    self.srvsock.listen( 5 )

    self.descriptors = [self.srvsock]
    print 'ChatServer started on port %s' % port

  def run( self ):
      while 1:

        # Await an event on a readable socket descriptor
          (sread, swrite, sexc) = select.select( self.descriptors,[],[])
          for sock in sread:

            # Received a connect to the server (listening) socket
              if sock == self.srvsock:
                  self.accept_new_connection()
              else:

              # Received something on a client socket
                  str = sock.recv(1024)

                  if str.startswith('Register'):
                      broadcastthread = Thread(target = self.register_login_broadcast,args=(self.return_to_register(str),sock))
                      broadcastthread.start()
                      broadcastthread.join()
            
                  elif str.startswith('Login'):
                      broadcastthread = Thread(target = self.register_login_broadcast,args=(self.return_to_login(str),sock))
                      broadcastthread.start()
                      broadcastthread.join()
                  elif str.startswith('Flag'):
                      newstr = '%s' % (str)
                      broadcastthread = Thread(target = self.broadcast_string,args=(newstr,sock))
                      broadcastthread.start()
                      temp = newstr.split(' ')
                      if temp[2] == 'join':
                        self.onlinemember.append(temp[1])
                      if temp[2] == 'exit':
                        self.onlinemember.remove(temp[1])
                  elif str.startswith('Message'):
                      newstr = '%s' % (str)
                      broadcastthread = Thread(target = self.broadcast_message,args=(newstr,))
                      broadcastthread.start()
                  elif str.startswith('MemberList'):
                      newstr = ','.join(self.onlinemember)
                      broadcastthread = Thread(target = self.register_login_broadcast,args=('MemberList '+newstr,sock))
                      broadcastthread.start()
                  elif str == '':
                      host,port = sock.getpeername()
                      str = 'Client left %s:%s\r\n' % (host, port)
                      self.broadcast_string( str, sock )
                      sock.close
                      self.descriptors.remove(sock)

  def broadcast_string( self, str, omit_sock ):
      for sock in self.descriptors:
          if sock != self.srvsock and sock != omit_sock:
              sock.send(str)
      print str

  def broadcast_message( self, str):
      for sock in self.descriptors:
          if sock != self.srvsock:
              sock.send(str)
      print str

  def register_login_broadcast( self, str, omit_sock ):
      for sock in self.descriptors:
          if sock != self.srvsock and sock == omit_sock:
          #if sock == omit_sock:
              sock.send(str)
      print str

  def accept_new_connection( self ):
      newsock, (remhost, remport) = self.srvsock.accept()
      self.descriptors.append( newsock )

      newsock.send("You're connected to the Python chatserver\r\n")
      str = 'Client joined %s:%s\r\n' % (remhost, remport)
      self.broadcast_string( str, newsock )

  def return_to_register(self,str):
      data = []
      data = str.split(' ')
      if data[1] in (self.readuserinformationfile()).keys():
          returnstr = 'Register '+data[1]+' '+'1'
          return returnstr
      else:
          self.writeuserinformationfile(data[1],data[2])
          returnstr = 'Register '+data[1]+' '+'0'
          return returnstr
  def return_to_login(self,str):
      data = []
      data = str.split(' ')
      if data[1] in (self.readuserinformationfile()).keys():
          if (self.readuserinformationfile())[data[1]]==data[2]:
              if data[1] not in self.onlinemember:
                  returndata = 'Login '+data[1]+' '+'0'
                  return returndata
              else:
                  returndata = 'Login '+data[1]+' '+'3'
                  return returndata
          else:
              returndata = 'Login '+data[1]+' '+'1'
              return returndata
      else:
          returndata = 'Login '+data[1]+' '+'2'
          return returndata

  def readuserinformationfile(self):
      fp = open(r'UserInfo.txt','r')
      s = fp.readlines()
      fp.close()
      userinformation = {}
      for item in s:
          temp = (item.strip()).split(':')
          userinformation[temp[0]] = temp[1]
      return userinformation

  def writeuserinformationfile(self,username,password):
      fp = open(r'UserInfo.txt','a')
      string = str(username)+':'+str(password)+'\n'
      fp.write(string)
      fp.close()
      
      
if __name__ == '__main__':
    myServer = ChatServer( 2640 )
    myServer.run()

