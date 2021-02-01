### SAML Cert Tooling

Create x509 certs to be used for SAML AuthN request signing and verification.

Note that X509 certs contain meta-data about the signature algorithm to use.
We hard code rsa-sha256. The `saml.pem` file is just the public key extracted
from the X509 cert. The `saml.pem` file does not contain the meta-data necessary
to know the encryption method. This is why you will see rsa-sha256 specified
when the `saml.pem` file is used and why we don't need to include the algorithm 
when using the X509 cert.

`make certs` will create X509 public/private key pairs as well a PEM key. Note that openssl deals with the PEM key.

`make sign` given `sign_me`, which should be the GET params of the initial AuthN request (chrome debug tools -> networking tab) i.e. `SAMLRequest=abcdef1234&RelayState=idp&SigAlg=http://wc3.com/something#rsa-256`, outputs `signature.binary`

`make verify` given `signature.binary`, `sign_me`, and `saml.pem` will output `signature.base64` then verify.

Example output:
```
make verify
openssl dgst -sha256 -verify ../saml.pem -signature signature.binary sign_me
Verified OK
```

`fuzz.py` Sign permutations of AuthN GET params. This is useful if you think the
payload the IDP is verifying the signature for is only a subset of the entire
AuthN request params. Note that I have not seen this to be the case. But it was
a crazy theory.
