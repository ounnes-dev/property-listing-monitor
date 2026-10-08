import requests

url = "https://api.ouedkniss.com/graphql"

listing_id = input("Enter listing ID: ")
variables = {
    "id": listing_id
}

query = """
query AnnouncementGet($id: ID!) {
    announcement: announcementDetails(id: $id) {
        id
        title
        price
    }
}
"""

data = {
    "operationName": "AnnouncementGet",
    "variables": variables,
    "query": query
}

response = requests.post(url, json=data)

result = response.json()

listing = result["data"]["announcement"]

print(listing["id"])
print(listing["title"])
print(listing["price"])
