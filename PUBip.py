import urllib.request

def get_public_ip():
    url = 'https://api.ipify.org'
    response = urllib.request.urlopen(url)
    if response.status == 200:
        return response.read().decode().strip()
    else:
        return None

# Usage
public_ip = get_public_ip()
if public_ip:
    print(f"Public IP Address: {public_ip}")
else:
    print("Failed to retrieve the public IP address.")
