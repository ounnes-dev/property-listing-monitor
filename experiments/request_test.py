import requests
url = "https://www.ouedkniss.com/villa-vente-mostaganem-algerie-d58126401"
response = requests.get(url)

print(response.text)