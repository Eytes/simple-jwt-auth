## Description

The microservice that is responsible for working with JWT

- Creation
- Validation
- Revocation

## Generate keys

You need to create the keys in the `certs` folder

```shell
# Generate an RSA private key, of size 2048
openssl genrsa -out ./certs/private.pem 2048
```

```shell
# Extract the public key from the key pair, which can be used in certificate  
openssl rsa -in ./certs/private.pem -outform PEM -pubout -out ./certs/public.pem
```