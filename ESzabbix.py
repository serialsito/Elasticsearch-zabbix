#!/usr/bin/env python

# Created by Aaron Mildenstein on 19 SEP 2012
# Switchted from pyes to Elasticsearch for better Health Monitoring by Marcel Alburg on 17 JUN 2014
# Adjusted for ELK 2.3 by Javier Barroso on 17 AUG 2016

from elasticsearch import Elasticsearch

import sys
import json
import shelve
import os
import time

# Define the fail message
def zbx_fail():
    print "ZBX_NOTSUPPORTED"
    sys.exit(2)

def use_cache(file):
    if not os.access(file,os.F_OK):
        return False
    now = int(time.time())
    file_modified = int(os.stat(file).st_mtime)
    if now - file_modified < 60:
       return True
    else:
       return False


searchkeys = ['query_total', 'fetch_time_in_millis', 'fetch_total', 'fetch_time', 'query_current', 'fetch_current', 'query_time_in_millis']
getkeys = ['missing_total', 'exists_total', 'current', 'time_in_millis', 'missing_time_in_millis', 'exists_time_in_millis', 'total']
docskeys = ['count', 'deleted']
indexingkeys = ['delete_time_in_millis', 'index_total', 'index_current', 'delete_total', 'index_time_in_millis', 'delete_current']
storekeys = ['size_in_bytes', 'throttle_time_in_millis']
cachekeys = ['filter_size_in_bytes', 'field_size_in_bytes', 'field_evictions']
clusterkeys_direct = docskeys + storekeys
clusterkeys_indirect = searchkeys + getkeys + indexingkeys
returnval = None
conn = None
user=str(os.getuid())
clustercache_file = "/tmp/clusterstats.cache." + user
nodescache_file = "/tmp/nodestats.cache." + user
lock_file="/tmp/ESzabbix.lock." + user

# now = time.time()
# logging = open("/tmp/whathappens.log."+str(now)+"-"+sys.argv[1]+"-"+sys.argv[2], "w");
# logging.write(" ".join(sys.argv)+"\n")
# Waiting to somebody write the cache
while os.access(lock_file,os.F_OK):
#    logging.write("Waiting a second ...\n")
    time.sleep(1)
    os.remove(lock_file)

# __main__

# We need to have two command-line args:
# sys.argv[1]: The node name or "cluster"
# sys.argv[2]: The "key" (status, filter_size_in_bytes, etc)

if len(sys.argv) < 3:
    zbx_fail()

# Try to establish a connection to elasticsearch
try:
    conn = Elasticsearch('localhost:9200', sniff_on_start=False)
except Exception, e:
    zbx_fail()

if sys.argv[1] == 'cluster' and sys.argv[2] in clusterkeys_direct:
    nodestats = None
#    now=time.strftime("%Y%m%d-%H:%M:%S")
    if use_cache(clustercache_file):
#	logging.write(str(now) + ": Using cluster cache\n")
        nodestats = shelve.open(clustercache_file)
        nodestats = nodestats['stats']
    else:
#	logging.write(str(now) + ": Generate lockfile and cluster cache\n")
        lock=open (lock_file, "w")
        try:
            nodestats = conn.cluster.stats()
            shelf = shelve.open(clustercache_file)
            shelf['stats']=nodestats
            shelf.close()
            lock.close()
        except Exception, e:
            if os.access(lock_file, os.F_OK):
                os.remove(lock_file)
            zbx_fail()
        if os.access(lock_file, os.F_OK):
            os.remove(lock_file)
    if sys.argv[2] in docskeys:
        returnval = nodestats['indices']['docs'][sys.argv[2]]
    elif sys.argv[2] in storekeys:
        returnval = nodestats['indices']['store'][sys.argv[2]]
elif sys.argv[1] == 'cluster' and  sys.argv[2] in clusterkeys_indirect:
    nodestats = None
#    now=time.strftime("%Y%m%d-%H:%M:%S")
    if use_cache(nodescache_file):
#	logging.write(str(now)+": Using node cache\n")
        nodestats = shelve.open(nodescache_file)
        nodestats = nodestats['stats']
    else:
#	logging.write(str(now)+": Generate lockfile and node cache\n")
        lock=open (lock_file, "w")
        try:
            nodestats = conn.nodes.stats()
            shelf = shelve.open(nodescache_file)
            shelf['stats']=nodestats
            shelf.close()
            lock.close()
        except Exception, e:
            if os.access(lock_file, os.F_OK):
                os.remove(lock_file)
            zbx_fail()
        if os.access(lock_file, os.F_OK):
            os.remove(lock_file)
        else:
            pass # something is wrong if this is executed ...
    subtotal = 0
    for nodename in conn.nodes.info()['nodes'].keys():
        try:
    	    if sys.argv[2] in indexingkeys:
    		    indexstats = nodestats['nodes'][nodename]['indices']['indexing']
    	    elif sys.argv[2] in getkeys:
    		    indexstats = nodestats['nodes'][nodename]['indices']['get']
    	    elif sys.argv[2] in searchkeys:
    		    indexstats = nodestats['nodes'][nodename]['indices']['search']
        except Exception, e:
            pass
        try:
    	    if sys.argv[2] in indexstats:
    		    subtotal += indexstats[sys.argv[2]]
        except Exception, e:
            pass
    returnval = subtotal

elif sys.argv[1] == "cluster":
    # Try to pull the managers object data
    try:
        escluster = conn.cluster
    except Exception, e:
        if sys.argv[2] == 'status':
            returnval = "red"
        else:
            zbx_fail()
    # Try to get a value to match the key provided
    try:
        returnval = escluster.health()[sys.argv[2]]
    except Exception, e:
        if sys.argv[2] == 'status':
            returnval = "red"
        else:
            zbx_fail()
    # If the key is "status" then we need to map that to an integer
    if sys.argv[2] == 'status':
        if returnval == 'green':
            returnval = 0
        elif returnval == 'yellow':
            returnval = 1
        elif returnval == 'red':
            returnval = 2
        else:
            zbx_fail()

# Mod to check if ES service is up
elif sys.argv[1] == 'service':
    if sys.argv[2] == 'status':
        if conn.ping():
            returnval = 1
        else:
            returnval = 0

else: # Not clusterwide, check the next arg
    nodestats = None
#    now=time.strftime("%Y%m%d-%H:%M:%S")
    if use_cache(nodescache_file):
#	logging.write(str(now)+": Usando cache nodos\n")
        nodestats = shelve.open(nodescache_file)
        nodestats = nodestats['stats']
    else:
#	logging.write(str(now)+": Creando lockfile y cache nodo\n")
        lock=open (lock_file, "w")
        try:
            nodestats = conn.nodes.stats()
            shelf = shelve.open(nodescache_file)
            shelf['stats']=nodestats
            shelf.close()
            lock.close()
        except Exception, e:
            if os.access(lock_file, os.F_OK):
                os.remove(lock_file)
            zbx_fail()
        if os.access(lock_file, os.F_OK):
            os.remove(lock_file)

    for nodename in conn.nodes.info()['nodes'].keys():
        if sys.argv[1] in nodestats['nodes'][nodename]['name']:
            if sys.argv[2] in indexingkeys:
                stats = nodestats['nodes'][nodename]['indices']['indexing']
            elif sys.argv[2] in storekeys:
                stats = nodestats['nodes'][nodename]['indices']['store']
            elif sys.argv[2] in getkeys:
                stats = nodestats['nodes'][nodename]['indices']['get']
            elif sys.argv[2] in docskeys:
                stats = nodestats['nodes'][nodename]['indices']['docs']
            elif sys.argv[2] in searchkeys:
                stats = nodestats['nodes'][nodename]['indices']['search']
            try:
                returnval = stats[sys.argv[2]]
            except Exception, e:
                pass

# now=time.strftime("%Y%m%d-%H:%M:%S")
# logging.write(str(now)+": Finalizando ("+str(returnval)+")\n")
# logging.close()

# If we somehow did not get a value here, that's a problem.  Send back the standard
# ZBX_NOTSUPPORTED
if returnval is None:
    zbx_fail()
else:
    print returnval
# End
