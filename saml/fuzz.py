#!/usr/bin/env python3

import subprocess
from urllib.parse import parse_qs
import tempfile
import os
import requests


FNAMES = ['sign_me_samlrequest', 'sign_me_samlrequest_sigalg', 'sign_me_samlrequest_relaystate_sigalg']
OUTPUT_DIR = 'out'

def run(cmd):
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print('===============================================')
        print(f'Error executing "{cmd}"')
        print(res.stdout)
        print(res.stderr)
        print('===============================================')
        print('')
    else:
        print(f"Success: {cmd}")
    return res.returncode

def openssl_run(cmd):
    return run(f'openssl {cmd}')

def exec_sign(file_to_sign='./sign_me', signature_file='./signature.binary', private_key='./key'):
    return run(f'openssl dgst -sha256 -sign {private_key} -out {signature_file} {file_to_sign}')

def exec_bin2base64(infile, outfile):
    return run(f'openssl base64 -A -in {infile} -out {outfile}')

def exec_verify(data_file, signature_file, public_key):
    return run(f'openssl dgst -sha256 -verify {public_key} -signature {signature_file} {data_file}')

def do_openssl():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open('request') as f:
        get_query = f.read()

    parsed_qs = parse_qs(get_query)

    saml_request = parsed_qs['SAMLRequest'][0]
    relay_state = parsed_qs['RelayState'][0]
    sig_alg = parsed_qs['SigAlg'][0]

    # Create data files to be signed
    with open(os.path.join(OUTPUT_DIR, FNAMES[0]), 'w') as f:
        f.write(f'SAMLRequest={saml_request}')
    with open(os.path.join(OUTPUT_DIR, FNAMES[1]), 'w') as f:
        f.write(f'SAMLRequest={saml_request}&SigAlg={sig_alg}')
    with open(os.path.join(OUTPUT_DIR, FNAMES[2]), 'w') as f:
        f.write(f'SAMLRequest={saml_request}&RelayState={relay_state}&SigAlg={sig_alg}')

    # Sign the created data files
    for fname in FNAMES:
        exec_sign(file_to_sign=os.path.join(OUTPUT_DIR, fname),
                signature_file=os.path.join(OUTPUT_DIR, f'signature_{fname}.binary'),
                private_key='key')
        exec_bin2base64(os.path.join(OUTPUT_DIR, f'signature_{fname}.binary'),
                      os.path.join(OUTPUT_DIR, f'signature_{fname}.base64'))

    # Verify the signatures
    for fname in FNAMES:
        exec_verify(data_file=os.path.join(OUTPUT_DIR, fname),
                  signature_file=os.path.join(OUTPUT_DIR, f'signature_{fname}.binary'),
                  public_key='pem')

do_openssl()
