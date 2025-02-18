## Description

The microservice that is responsible for working with JWT

- Creation
- Validation
- Revocation

## Environment

You need to create the `.env` file in the root dir
```shell
# Create ".env" file
touch ./.env
```

### Example
```dotenv
PRIVATE_KEY_PATH=certs/private.pem
PUBLIC_KEY_PATH=certs/public.pem
ALGORITHM=RS256

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=1
```


## Generate keys

You need to create the keys in the `certs` folder

```shell
# Create "certs" folder
mkdir ./certs
```

```shell
# Generate an RSA private key, of size 2048
openssl genrsa -out ./certs/private.pem 2048
```

```shell
# Extract the public key from the key pair, which can be used in certificate  
openssl rsa -in ./certs/private.pem -outform PEM -pubout -out ./certs/public.pem
```