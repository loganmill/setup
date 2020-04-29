
import subprocess

subprocess.check_call(
    'openssl req  -nodes -new -x509  -keyout import.pem -out import.pem -days 36500 -subj "/C=US/ST=Colorado/L=Louisville/O=Cardinal Peak Technologies LLC/OU=Org/CN=www.tectosoft.com"',
    shell=True)
