import urllib.parse
import urllib.request
import re
import json
import time
# from jsonrpc import ServiceProxy

import pymysql

start_time = time.time()

blockinfo_time = 0
dbread_time = 0
dbwrite_time = 0

previous_block_hash = 0

db = pymysql.connect("localhost","root","1234","txmondb" )

def fetch_block_from_url():
    global blockinfo_time
    global previous_block_hash

    # get latest block hash
    time.sleep(1) # time delay for blockchain.info's policy
    strt_time = time.time()
    url = "https://blockchain.info/ko/latestblock"
    res = urllib.request.urlopen(url)
    res_body = res.read()
    data = json.loads(res_body.decode("utf-8"))

    # check previous block_hash
    if ( previous_block_hash == data["hash"] ) :
        data = { "changed" : False }
        return data
    else :
        previous_block_hash = data["hash"]

    # get latest block info
    time.sleep(1)
    url = "https://blockchain.info/ko/rawblock/" + data["hash"]
    res = urllib.request.urlopen(url)
    res_body = res.read()
    data = json.loads(res_body.decode("utf-8"))

    blockinfo_time += time.time() - strt_time
    return data

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
    sql = "INSERT INTO alarm_lists VALUES ('%s', '%s')" % (input, out)
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()
    dbwrite_time += time.time() - strt_time

count = 0

def get_block( ):
    global count

    data = fetch_block_from_url()
    if ( hasattr( data, "changed") and data["changed"] == False ):
        print( "-------Same block----------")
        time.sleep(60)
        return

    for i in range( data["n_tx"] ) :
        for j in range( data["tx"][i]["vin_sz"] ) :
            print( '----- tx: %d ( input %d )--------- ' % (i, j) )
            if ( hasattr( data["tx"][i]["inputs"][j], "addr") and exist_whitelist( data["tx"][i]["inputs"][j]["addr"] ) == True ):
                for k in range(data["tx"][i]["vout_sz"]):
                    print( '----- tx: %d ( input %d -> output %d )--------- ' % (i, j, k) )
                    if ( hasattr( data["tx"][i]["out"][k], "addr") and exist_blacklist( data["tx"][i]["out"][k]["addr"] ) == True):
                        print( 'found ' + data["tx"][i]["inputs"][j]["addr"] + ", " + data["tx"][i]["out"][k]["addr"] + "\n" )
                        insert_alarmlist( data["tx"][i]["inputs"][j]["addr"], data["tx"][i]["out"][k]["addr"] )
                        count +=1

while(1) :
    get_block()

print( "-------------------------")
print("Found : %s" %(count))
print( "total time : %s seconds" %(time.time()-start_time) )
print( "blockinfo time : %s seconds" %(blockinfo_time) )
print( "DB read time : %s seconds" %(dbread_time) )
print( "DB write time : %s seconds" %(dbwrite_time) )

# disconnect from server
db.close()