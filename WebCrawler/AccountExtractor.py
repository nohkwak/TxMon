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

db = pymysql.connect("localhost","root","1234","txmondb" )

def fetch_contents_from_url( addr, index ):
    global blockinfo_time

    time.sleep(1) # time delay for blockchain.info's policy
    strt_time = time.time()
    url = "https://blockchain.info/ko/rawaddr/" + addr + "?key=be706ad0-9f27-4230-84ba-d603528ffde3&offset=" + str(index*50)
    res = urllib.request.urlopen(url)
    res_body = res.read()
    data = json.loads(res_body.decode("utf-8"))
    blockinfo_time += time.time() - strt_time
    return data

def insert_whitelist(addr, depth):
    global dbwrite_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "INSERT INTO white_lists VALUES ('%s', '%s')" % (addr, depth)
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()
    dbwrite_time += time.time() - strt_time

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



depth = 0
count = 0
limit = 2


def get_addr_list( addr, index ):
    data = fetch_contents_from_url( addr, index )
    global depth
    global count
    global limit
    depth = depth + 1

    if ( data["n_tx"] - index * 50 < 50 ) :
        itr = data["n_tx"] % 50
    else:
        itr = 50

    for i in range( itr ) :
        for j in range( data["txs"][i]["vin_sz"] ) :
            if ( data["txs"][i]["inputs"][j]["prev_out"]["addr"] == addr ):
                for k in range(data["txs"][i]["vout_sz"]):
                    print( '----- tx: %d ( input %d -> output %d )--------- ' % (i, j, k) )
                    #print( 'check ' + data["txs"][i]["out"][k]["addr"] + ", %d" %(exist_whitelist( data["txs"][i]["out"][k]["addr"]))  )
                    if ( exist_whitelist( data["txs"][i]["out"][k]["addr"] ) == False):
                        print( 'added ' + data["txs"][i]["out"][k]["addr"] + ", %d\n" %depth )
                        insert_whitelist( data["txs"][i]["out"][k]["addr"], depth)
                        count +=1

                        if ( depth + 1 < limit ) :
                            get_hundred_list(data["txs"][i]["out"][k]["addr"])
                break
    depth = depth - 1

def get_hundred_list( addr ):
    data = fetch_contents_from_url( addr, 0 )
    for i in range(int( data["n_tx"]/50 + 1 )):
        get_addr_list( addr, i )


addr="1Q2ogJniBJLwgnwpRgi5bWRXkKBF3yxrh"
insert_whitelist( addr, depth)
get_hundred_list( addr )


print( "-------------------------")
print("Depth : %s" %limit)
print( "total : %s" %(count))
print( "total time : %s seconds" %(time.time()-start_time) )
print( "blockinfo time : %s seconds" %(blockinfo_time) )
print( "DB read time : %s seconds" %(dbread_time) )
print( "DB write time : %s seconds" %(dbwrite_time) )

# disconnect from server
db.close()