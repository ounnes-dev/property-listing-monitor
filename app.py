
from fastapi import FastAPI, HTTPException

from database import (
    get_all_listings,
    get_listing_by_id,
    get_events_for_listing
)

app = FastAPI(
    title="Property Listing Intelligence API",
    description="API for accessing monitored property listings.",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Property Listing Intelligence API is running."
    }


@app.get("/listings")
def list_listings():
    return get_all_listings()


@app.get("/listings/{listing_id}")
def get_listing(listing_id: str):
    listing = get_listing_by_id(listing_id)

    if listing is None:
        raise HTTPException(
            status_code=404,
            detail="Listing not found."
        )

    return listing

@app.get("/listings/{listing_id}/events")
def listing_events(listing_id: str):
    listing = get_listing_by_id(listing_id)

    if listing is None:
        raise HTTPException(
            status_code=404,
            detail="Listing not found."
        )

    return get_events_for_listing(listing_id)