import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import json
import requests
import os
import struct
import logging
from watson_developer_cloud import TextToSpeechV1
from watson_developer_cloud import ConversationV1
from string import Template
from dotenv import load_dotenv, find_dotenv


logging.basicConfig(level=logging.DEBUG)

# Watson STT Service Credentials, populated from
# VCAP_SERVICES in Bluemix or .env file if running locally
stt_credentials ={}
 
# Watson Conversation Service workspace id
# Loaded automatically from ENV var CONVERSATION_WORKSPACE_ID
conversation_workspace_id = 'NO_WORKSPACE_ID'

#Indicates if running on Bluemix or locally 
running_on_IBM_Cloud = False

language_model = 'en-US_NarrowbandModel' # Specify the Narrowband model for your language
default_voice = 'en-US_AllisonVoice' # Voice used for Text to Speech service


# Will be set  from VCAP_APPLICATION env when running in Bluemix
# or from the .env file when running locally
HOSTNAME = ''

# Get required creds as appropraite 
# when running locally or in Bluemix
if  'VCAP_SERVICES' in os.environ:
   logging.debug('Found VCAP_SERVICES')
   running_on_IBM_Cloud = True
   vcap_app = json.loads(os.getenv('VCAP_APPLICATION'))
   HOSTNAME = vcap_app['uris'][0]
   vcap_services = json.loads(os.getenv('VCAP_SERVICES'))
   if 'speech_to_text' in vcap_services:
      creds = vcap_services['speech_to_text'][0]['credentials']
      stt_credentials['url'] = creds['url']
      stt_credentials['username'] = creds['username']
      stt_credentials['password'] = creds['password']
else:
   load_dotenv(find_dotenv())
   HOSTNAME =  os.getenv('HOSTNAME')                                         
   stt_credentials['url'] = os.getenv('STT_URL')
   stt_credentials['username'] = os.getenv('STT_USERNAME')
   stt_credentials['password'] = os.getenv('STT_PASSWORD')

logging.debug('Using HOSTNAME ' + HOSTNAME) 
                                          
conversation_workspace_id = os.getenv('WORKSPACE_ID')

# Using the Python SDK for Text to Speech (instead of Websockets)
# because the output needs to be broken up into 640 byte chunks
# before sending it to Nexmo 
if running_on_IBM_Cloud:
    text_to_speech = TextToSpeechV1(
        x_watson_learning_opt_out=True)  # Optional flag
else:
    text_to_speech = TextToSpeechV1(
        username=os.getenv('TTS_USERNAME'),
        password=os.getenv('TTS_PASSWORD'),
        x_watson_learning_opt_out=True)  # Optional flag

# Python SDK object for Watson Conversation
if running_on_IBM_Cloud:
    conversation = ConversationV1(
        version='2017-04-21')
else:
    conversation = ConversationV1(
        username=os.getenv('CONVERSATION_USERNAME'),
        password=os.getenv('CONVERSATION_PASSWORD'),
        version='2017-04-21')

# Utility function to get a Watson token from the service instance username and password
def gettoken(credentials):
    resp = requests.get('https://stream.watsonplatform.net/authorization/api/v1/token', auth=(credentials['username'], credentials['password']), params={'url' : credentials['url']})
    token = None
    if resp.status_code == 200:
        token = resp.content
    else:
        print resp.status_code
        print resp.content
    return token


class MainHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.content_type = 'text/plain'
		self.write("Watson STT Example")
		self.finish()

# Handler for incoming phone call notification
class CallHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        data={}
        data['hostname'] = HOSTNAME
        filein = open('ncco.json')
        src = Template(filein.read())
        filein.close()
        ncco = json.loads(src.substitute(data))
        self.write(json.dumps(ncco))
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.finish()

# Handler for events sent via REST from Nexmo
class EventHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        print self.request.body
        self.content_type = 'text/plain'
        self.write('ok')
        self.finish()
			
# Web Socket handler - Nexmo uses web sockets to stream in audio from  a phone call and
# to receive voice data back .
class WSHandler(tornado.websocket.WebSocketHandler):
    stt_watson_future = None
    
    def open(self):
        logging.info("Websocket Call Connected")
        stt_uri = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?watson-token={}&model={}'.format(gettoken(stt_credentials), language_model)
        self.stt_watson_future = tornado.websocket.websocket_connect(stt_uri, on_message_callback=self.on_stt_watson_message)
        self.context = {}
    @gen.coroutine
    def on_message(self, message):
	# Web socket message from Nexmo 
        stt_watson = yield self.stt_watson_future
        # Binary (ie voice) data is type 'str', text is type 'unicode'
        if type(message) == str:
            stt_watson.write_message(message, binary=True)
        else:            
            data = json.loads(message)
            stt_config = {}
            stt_config['action'] = 'start'
            stt_config['continuous'] = True
            stt_config['interim_results'] = True
            stt_config['content-type'] = data['content-type']
            logging.debug(json.dumps(stt_config))
            stt_watson.write_message(json.dumps(stt_config), binary=False) 
            conv_response = conversation.message(workspace_id=conversation_workspace_id, input={'text': ''})
            self.context = conv_response['context']
            conv_response_audio = text_to_speech.synthesize(conv_response['output']['text'][0], accept='audio/l16;rate=16000', voice=default_voice)
            self.send_audio_to_caller(conv_response_audio)
    @gen.coroutine
    def on_close(self):
        print("Websocket Call Disconnected")
        stt_watson = yield self.stt_watson_future
        data = {'action' : 'stop'}
        stt_watson.write_message(json.dumps(data), binary=False)
        stt_watson.close()
        self.context = {}
        #tts_watson = yield self.tts_watson_future
        #tts_watson.close()
    @gen.coroutine    
    def on_stt_watson_message(self, message):
        # WATSON Speech to Text web socket handler. Receives text trnscription of audio data from Nexmo
        if message is not None:
            #print message
            #print type(message)
            message_dict = json.loads(message)
            if 'results' in message_dict:
                for result in message_dict['results']:
                    if result['final']:
                        logging.debug('found text from stt')
                        caller_audio_text = result['alternatives'][0]['transcript']
                        logging.debug(caller_audio_text)
                        conv_response = conversation.message(workspace_id=conversation_workspace_id, input={'text': caller_audio_text}, context=self.context)
                        conv_response_audio = text_to_speech.synthesize(conv_response['output']['text'][0], accept='audio/l16;rate=16000', voice=default_voice)
                        self.send_audio_to_caller(conv_response_audio)
                        break
   
    def send_audio_to_caller(self, audio):
        # Sends raw audio back to Nexmo
        # Nexmo requires that outgoing voice data 
        # be sent in 640 byte chunks
        
        # Expand audio buffer length (if necessary) to be divisble by 640 by
        # padding with nulls so the last packet is 640 bytes
        logging.debug('audio buffer length ' + str(len(audio)))
        buffer_len = len(audio)
        last_packet_size = buffer_len % 640  if  (buffer_len % 640) > 0 else 640
        if last_packet_size <  640:
            buffer_len += 640 - last_packet_size
            audio = struct.pack(str(buffer_len)+'s', audio)
            logging.debug('expanded audio buffer length ' + str(len(audio)))
        # Send output of the Text to Speech svc back to Nexmo 
        # in 640 byte chunks to be played back to the caller
        pos = 0
        for x in range(0, buffer_len//640):
            newpos = pos + 640
            data = audio[pos:newpos]
            self.write_message(data, binary=True)
            pos = newpos
		
# Main routine setup handlers and wait for HTTP or Websocket requests
def main():
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    application = tornado.web.Application([(r"/", MainHandler),
                                            (r"/event", EventHandler),
                                            (r"/ncco", CallHandler),
                                            (r"/socket", WSHandler),
                                            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
                                        ])
    http_server = tornado.httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 8000))
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
	
	

