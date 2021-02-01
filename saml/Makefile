sign:
	openssl dgst -sha256 -sign saml.key -out signature.binary sign_me
	openssl base64 -in signature.binary -out signature.base64

verify:
	openssl dgst -sha256 -verify saml.pem -signature signature.binary sign_me

certs:
	openssl req -new -x509 -days 365 -nodes -subj "/C=US/ST=NC/L=Durham/O=RedHat/CN=www.redhat.com" -out saml.crt -keyout saml.key
	openssl x509 -pubkey -noout -in saml.crt > saml.pem

clean:
	rm -f saml.crt saml.key saml.pem
	rm -f signature.binary signature.base64
