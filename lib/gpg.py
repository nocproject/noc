# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## GnuPG integration
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.settings import config
from noc.lib.validators import is_email
import subprocess,os,logging,httplib,urllib,time
##
## email -> in_keyring
##
KEYS=set()
##
## email -> last check for keys not in keyring
##
KEY_LAST_CHECK={}

GPG_PATH=config.get("path","gpg")
GPG_USE_KEY=config.get("pgp","use_key")
KEYSERVER=config.get("pgp","keyserver")
KEYSERVER_PORT=11371

##
## Lookup keyserver for a key
## Returns KEY ID or None
##
def hkp_lookup(email):
    logging.debug("HKP Lookup for '%s' at '%s'"%(email,KEYSERVER))
    c=httplib.HTTPConnection(KEYSERVER,KEYSERVER_PORT)
    c.request("GET","/pks/lookup?op=index&options=mr&search=%s"%urllib.quote(email))
    try:
        response=c.getresponse()
        if response.status!=200:
            logging.debug("HKP Lookup '%s' failed: %s %s"%(email,response.status,response.reason))
            return None
        data=response.read()
        for l in data.split("\n"):
            if l.startswith("pub:"):
                return l.split(":")[1]
    finally:
        c.close()
    return None
##
##
##
def key_in_keychain(email):
    try:
        subprocess.check_call([GPG_PATH,"--list-keys",email],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        pass
    return False
##
## Checks key in the keyring
## Try to import from keyserver if no one
## Return True or False
##
def check_key(email):
    if not is_email(email):
        return
    # Check cache
    if email in KEYS:
        return True
    # Check we do not abuse keychain with faulty requests
    t=time.time()
    if email in KEY_LAST_CHECK and t-KEY_LAST_CHECK[email]<86400:
        return False
    # Check keychain
    if key_in_keychain(email):
        return True
    logging.debug("Key for %s is not found. Trying to retrieve from %s"%(email,KEYSERVER))
    key_id=hkp_lookup(email)
    if key_id is None:
        KEY_LAST_CHECK[email]=t
        return False
    # Try to import key into keyring
    try:
        subprocess.check_call([GPG_PATH,"--keyserver",KEYSERVER,"--recv-keys",key_id],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        KEY_LAST_CHECK[email]=t
        return False
    # Finally check key in keychain
    return key_in_keychain(mail)
##
## Encrypt
## Returns Encrypted message or NULL if no valid PGP key found
def encrypt(email,message):
    if not check_key(email):
        return None
    s=subprocess.Popen([GPG_PATH,"--armor","--encrypt","--sign","-r",email,"-u",GPG_USE_KEY],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    s.stdin.write(message)
    s.stdin.close()
    return s.stdout.read()
    