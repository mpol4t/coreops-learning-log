from urllib.request import urlopen 
from urllib.error import HTTPError, URLError
import sys
import argparse
from socket import gaierror
from ssl import SSLCertVerificationError

def request_json(url):
    try:
        with urlopen(url, timeout=5) as response:
            status = response.status
            body = response.read().decode()
            return status, body
    
    except TimeoutError as hata:
        print("Timeout meydana geliyor!", file=sys.stderr)
        sys.exit(1)
    
    except HTTPError as hata: 
        status = hata.code
        body = hata.read().decode()
        return status, body
    
    except URLError as hata:
        reason = hata.reason
        if isinstance(reason, gaierror):
            print("DNS çözümlemesi sırasında hata meydana geldi!", hata, file=sys.stderr)
            sys.exit(1)
            
        elif isinstance(reason, ConnectionRefusedError):
            print("TCP bağlanma sırasında problem meydana geldi!", hata, file=sys.stderr)
            sys.exit(1)
            
        elif isinstance(reason, SSLCertVerificationError):
            print("TLS aşamasında problem meydana geldi!", hata, file=sys.stderr)
            sys.exit(1)
    
        print("Bir hata meydana geldi incelemenizi öneririz!", hata, file=sys.stderr)
        sys.exit(1)
    
def main():
    parser = argparse.ArgumentParser() 
    parser.add_argument("url")
    args = parser.parse_args()
    status, body = request_json(args.url)
    print("Response status:",status)
    print("Body:",body)
    
    if 200 <= status < 300 :
       return 0
    else:
        return 47
    
if __name__ == "__main__":
    sys.exit(main())