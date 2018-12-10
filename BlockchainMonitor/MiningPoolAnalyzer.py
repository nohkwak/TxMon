from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import time
import os.path
import re
import json
# from jsonrpc import ServiceProxy
import ssl
import pymysql

start_time = time.time()

dbread_time = 0
dbwrite_time = 0

db = pymysql.connect("localhost","root","application3","TxMonDB" )

def exist_whitelist(addr):
	global dbread_time

	strt_time = time.time()
	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	# Drop table if it already exist using execute() method.
	sql = "SELECT addr FROM white_lists WHERE addr = '" + addr + "'"
	try:
		# Execute the SQL command
		row_count = cursor.execute(sql)
		dbread_time += time.time() - strt_time
		if row_count > 0:
			return True
		else:
			return False
	except:
	   print( "DB error" )

def exist_blacklist(addr):
	global dbread_time

	strt_time = time.time()
	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	# Drop table if it already exist using execute() method.
	sql = "SELECT addr FROM black_lists WHERE addr = '" + addr + "'"
	try:
		# Execute the SQL command
		row_count = cursor.execute(sql)
		dbread_time += time.time() - strt_time
		if row_count > 0:
			return True
		else:
			return False
	except:
	   print( "DB error" )

def insert_alarmlist( input, out ):
	global dbwrite_time

	strt_time = time.time()
	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	# Drop table if it already exist using execute() method.
	sql = "INSERT INTO alarm_lists VALUES ('%s', '%s')" % (input, output)
	try:
	   # Execute the SQL command
	   cursor.execute(sql)
	   # Commit your changes in the database
	   db.commit()
	except:
	   # Rollback in case there is any error
	   db.rollback()
	dbwrite_time += time.time() - strt_time


PORT = 8154
ANALYZE = "/rest/analyze"

class MyHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		print("%s: Just received a GET request" % time.ctime())

		qs = {}
		path = self.path
		if '?' in path:
			path, tmp = path.split('?', 1)
			qs = urlparse.parse_qs(tmp)
		print path, qs

		#if os.path.dirname(path) == ANALYZE:
		if path == ANALYZE:
			self.analyze_transaction(qs)
		else:
			self.send_headers(400)
			self.wfile.write("Unknown request")

		return

	def send_headers(self, code):
		self.send_response(code)
		self.send_header("Accept", "application/json")
		self.end_headers()

	def analyze_transaction(self, qs):
		in_addr = qs["input"][0]
		out_addr = qs["out"][0]

		print( '-----  input %s -> output %s ----- \n\n' %(in_addr, out_addr) )
		if ( exist_whitelist( in_addr ) == True and exist_blacklist( out_addr ) == True):
			print( 'found ' + in_addr + ", " + out_addr + "\n" )
			insert_alarmlist( in_addr, out_addr )
			count += 1

		msg = "Success"
		code = 200

		self.send_headers(code)
		self.wfile.write(msg)

if __name__ == "__main__":
	try:
		server = HTTPServer(('0.0.0.0', PORT), MyHandler)
		# for https server
		server.socket = ssl.wrap_socket (server.socket, keyfile="./key.pem", certfile='./cert.pem', server_side=True)
		print('Started http server at port %d' % PORT)
		server.serve_forever()
	except KeyboardInterrupt:
		print('^C received, shutting down server')
		server.socket.close()