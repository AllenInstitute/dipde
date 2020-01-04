import time
import zmq
import threading

context = zmq.Context()

class PublishCallback(object):
    
    def __init__(self, port, topic, message_callback):
        
        self.port = port
        self.topic = topic
        self.message_callback = message_callback        
        self.socket = context.socket(zmq.PUB)
        
    def __call__(self, obj):
        message_to_send = list(self.message_callback(obj))
        message_to_send.insert(0,"%s" % self.topic)
        self.socket.send_multipart(map(str, message_to_send))
        
class PublishCallbackConnect(PublishCallback):
    
    def __init__(self, port, topic, message_callback):
        super(PublishCallbackConnect, self).__init__(port, topic, message_callback)
        self.socket.connect("tcp://localhost:%s" % self.port)
        

# class PublishCallbackBind(PublishCallback):
#     
#     def __init__(self, port, topic, message_callback):
#         super(self.__class__, self).__init__(port, topic, message_callback)
#         self.socket.bind("tcp://*:%s" % self.port)
        
class CallbackSubscriber(object): 
    
    def __init__(self, port, receive_callback=None): 
        self.port = port  
        self.socket = context.socket(zmq.SUB) 
        self.socket.bind("tcp://*:%s" % self.port) 
        self.socket.setsockopt(zmq.SUBSCRIBE, 'test')
        
        if receive_callback is None:
            def receive_callback(received_message):
                print(received_message)
        self.receive_callback = receive_callback 

    def run(self):     
        while True: 
            received_message_multipart = self.socket.recv_multipart() 
            topic = received_message_multipart[0]
            received_message = received_message_multipart[1:]
            self.receive_callback(received_message)

class CallbackSubscriberThread(threading.Thread): 
    def __init__(self, port): 
        super(CallbackSubscriberThread, self).__init__()
        self.daemon = True 
        self.port = port  

    def run(self): 
        self.subscriber = CallbackSubscriber(self.port) 
        self.subscriber.run() 


class RequestFiringRate(object):
    
    def __init__(self, port):
        
        self.port = port        
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % port)
        
    def __call__(self, t):
        self.socket.send('%s' % t)
        message = self.socket.recv_multipart()
        return float(message[0])
    
class ReplyFiringRateServer(object):
    
    def __init__(self, port, reply_function):
        self.port = port
        self.reply_function = reply_function
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % self.port)
        
    def run(self):
        
        while True:
            message = self.socket.recv()
            if message == 'SHUTDOWN':
                break
            requested_t = float(message)
            self.socket.send_multipart([b"%s" % self.reply_function(requested_t)])
        self.socket.send('DOWN')

class ReplyServerThread(threading.Thread):
    def __init__(self, port, reply_function):
        super(self.__class__, self).__init__()
        self.daemon = True
        self.port = port
        self.reply_function = reply_function
    
    def run(self):
        self.server = ReplyFiringRateServer(self.port, self.reply_function)
        self.server.run()


