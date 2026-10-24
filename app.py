
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from database import (
    get_all_listings,
    get_listing_by_id,
    get_events_for_listing,
)
from analytics import (
    calculate_price_change,
    calculate_market_analytics,
)


app = FastAPI(
    title="Property Listing Intelligence API",
    description="API for accessing monitored property listings.",
    version="1.0.0",
)


# -------------------------
# API ENDPOINTS
# -------------------------

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
            detail="Listing not found.",
        )

    return listing


@app.get("/listings/{listing_id}/events")
def listing_events(listing_id: str):
    listing = get_listing_by_id(listing_id)

    if listing is None:
        raise HTTPException(
            status_code=404,
            detail="Listing not found.",
        )

    events = get_events_for_listing(listing_id)

    for event in events:
        if event.get("event_type") == "PRICE_CHANGED":
            event["price_change"] = calculate_price_change(
                event.get("old_price"),
                event.get("new_price"),
            )
        else:
            event["price_change"] = None

    return events


@app.get("/analytics/market")
def market_analytics():
    listings = get_all_listings()
    return calculate_market_analytics(listings)


# -------------------------
# WEB DASHBOARD
# -------------------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Property Intelligence Dashboard</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                padding: 32px;
                font-family: Arial, sans-serif;
                background: #f3f5f9;
                color: #172033;
            }

            header {
                margin-bottom: 28px;
            }

            h1 {
                margin-bottom: 8px;
            }

            .subtitle {
                color: #687386;
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
                gap: 16px;
                margin-bottom: 24px;
            }

            .stat,
            .panel {
                background: white;
                padding: 22px;
                border-radius: 12px;
                border: 1px solid #e2e7ef;
            }

            .stat-label {
                color: #687386;
                font-size: 14px;
            }

            .stat-value {
                font-size: 28px;
                font-weight: bold;
                margin-top: 10px;
            }

            .controls {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin-bottom: 20px;
            }

            input,
            select,
            button {
                padding: 11px 13px;
                border: 1px solid #d6dce7;
                border-radius: 7px;
                background: white;
                font-size: 14px;
            }

            input {
                flex: 1;
                min-width: 200px;
            }

            button {
                cursor: pointer;
                background: #2448b8;
                color: white;
                border-color: #2448b8;
            }

            button:hover {
                background: #19368f;
            }

            button:disabled {
                cursor: wait;
                opacity: 0.65;
            }

            .table-wrapper {
                overflow-x: auto;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                white-space: nowrap;
            }

            th,
            td {
                padding: 14px 12px;
                text-align: left;
                border-bottom: 1px solid #edf0f5;
            }

            th {
                color: #687386;
                font-size: 12px;
                text-transform: uppercase;
            }

            .status {
                color: #18794e;
                background: #e6f6ed;
                padding: 5px 9px;
                border-radius: 20px;
                font-size: 12px;
            }

            #message {
                color: #687386;
                margin-bottom: 16px;
            }

            #listingDetails {
                margin-top: 24px;
            }

            .history-controls {
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                gap: 12px;
                margin: 16px 0;
            }

            .history-controls label {
                font-weight: 600;
            }

            .history-controls select {
                max-width: 100%;
            }

            #eventCount {
                color: #687386;
                font-size: 14px;
            }

            .event {
                padding: 12px 0;
                border-bottom: 1px solid #edf0f5;
            }

            .event p {
                color: #687386;
                overflow-wrap: anywhere;
                line-height: 1.5;
            }

            .event-title {
                font-weight: bold;
            }

            .price-analysis {
                font-weight: bold;
            }

            .empty-history {
                color: #687386;
                padding: 12px 0;
            }

            .close-button {
                margin-top: 16px;
                background: #586174;
                border-color: #586174;
            }

            @media (max-width: 600px) {
                body {
                    padding: 16px;
                }
            }
        </style>
    </head>

    <body>
        <header>
            <h1>Property Intelligence</h1>
            <div class="subtitle">
                Monitor listings and explore the property market.
            </div>
        </header>

        <section class="stats">
            <div class="stat">
                <div class="stat-label">Active listings</div>
                <div class="stat-value" id="total">—</div>
            </div>

            <div class="stat">
                <div class="stat-label">Listings with known prices</div>
                <div class="stat-value" id="priced">—</div>
            </div>

            <div class="stat">
                <div class="stat-label">Cities represented</div>
                <div class="stat-value" id="cities">—</div>
            </div>
        </section>

        <section class="panel">
            <h2>Property listings</h2>

            <div class="controls">
                <input
                    id="search"
                    type="search"
                    placeholder="Search title or city..."
                    aria-label="Search property listings"
                >

                <select id="type" aria-label="Filter transaction type">
                    <option value="all">All transaction types</option>
                    <option value="sale">For sale</option>
                    <option value="rent">For rent</option>
                    <option value="unknown">Unknown</option>
                </select>

                <button id="refresh" type="button">Refresh data</button>
            </div>

            <div id="message" role="status">Loading listings...</div>

            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>City</th>
                            <th>Transaction</th>
                            <th>Price</th>
                            <th>Status</th>
                            <th>History</th>
                        </tr>
                    </thead>
                    <tbody id="listings"></tbody>
                </table>
            </div>

            <div id="listingDetails" class="panel" hidden>
                <h2 id="detailTitle">Property details</h2>
                <p id="detailInfo"></p>

                <h3>Monitoring history</h3>

                <div class="history-controls">
                    <label for="eventFilter">Filter events:</label>

                    <select id="eventFilter">
                        <option value="ALL">All events</option>
                        <option value="NEW">New listings</option>
                        <option value="REMOVED">Removed listings</option>
                        <option value="PRICE_CHANGED">Price changes</option>
                        <option value="PRICE_MISSING">Price missing</option>
                        <option value="PRICE_ADDED">Price added</option>
                    </select>

                    <span id="eventCount" aria-live="polite">0 events</span>
                </div>

                <div id="eventHistory">
                    Select a listing to view its history.
                </div>

                <button id="closeDetails" class="close-button" type="button">
                    Close details
                </button>
            </div>
        </section>

        <script>
            let allListings = [];
            let currentEvents = [];

            function addCell(row, value) {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
                return cell;
            }

            function formatPrice(price) {
                if (price === null || price === undefined || price === "") {
                    return "Not available";
                }

                const number = Number(price);

                return Number.isFinite(number)
                    ? number.toLocaleString()
                    : String(price);
            }

            function formatEventType(eventType) {
                const labels = {
                    NEW: "New listing",
                    REMOVED: "Listing removed",
                    PRICE_CHANGED: "Price changed",
                    PRICE_MISSING: "Price no longer available",
                    PRICE_ADDED: "Price added"
                };

                return labels[eventType] || String(eventType || "Event")
                    .replaceAll("_", " ");
            }

            function renderListings() {
                const query = document
                    .getElementById("search")
                    .value.trim()
                    .toLowerCase();

                const selectedType = document.getElementById("type").value;

                const filtered = allListings.filter(listing => {
                    const title = String(listing.title || "").toLowerCase();
                    const city = String(listing.city || "").toLowerCase();
                    const transaction = listing.transaction_type || "unknown";

                    const matchesSearch =
                        title.includes(query) || city.includes(query);

                    const matchesType =
                        selectedType === "all" || transaction === selectedType;

                    return matchesSearch && matchesType;
                });

                const table = document.getElementById("listings");
                table.replaceChildren();

                for (const listing of filtered) {
                    const row = document.createElement("tr");

                    addCell(row, listing.title || "Untitled");
                    addCell(row, listing.city || "Unknown");

                    const transaction = listing.transaction_type || "unknown";
                    const transactionLabel =
                        transaction === "sale" ? "For sale" :
                        transaction === "rent" ? "For rent" : "Unknown";

                    addCell(row, transactionLabel);
                    addCell(row, formatPrice(listing.price));

                    const statusCell = addCell(row, "");
                    const badge = document.createElement("span");
                    badge.className = "status";
                    badge.textContent = "Active";
                    statusCell.appendChild(badge);

                    const historyCell = addCell(row, "");
                    const detailsButton = document.createElement("button");
                    detailsButton.type = "button";
                    detailsButton.textContent = "View history";
                    detailsButton.addEventListener("click", () => {
                        showDetails(listing.id);
                    });

                    historyCell.appendChild(detailsButton);
                    table.appendChild(row);
                }

                document.getElementById("message").textContent =
                    `Showing ${filtered.length} of ${allListings.length} listings.`;
            }

            function renderEventHistory() {
                const history = document.getElementById("eventHistory");
                const eventCount = document.getElementById("eventCount");
                const selectedFilter = document.getElementById("eventFilter").value;

                const filteredEvents = currentEvents.filter(event =>
                    selectedFilter === "ALL" ||
                    event.event_type === selectedFilter
                );

                eventCount.textContent =
                    `${filteredEvents.length} ${filteredEvents.length === 1 ? "event" : "events"}`;

                history.replaceChildren();

                if (filteredEvents.length === 0) {
                    const emptyMessage = document.createElement("p");
                    emptyMessage.className = "empty-history";
                    emptyMessage.textContent = currentEvents.length === 0
                        ? "No monitoring events recorded yet."
                        : "No events match this filter.";

                    history.appendChild(emptyMessage);
                    return;
                }

                for (const event of filteredEvents) {
                    const item = document.createElement("div");
                    item.className = "event";

                    const heading = document.createElement("div");
                    heading.className = "event-title";
                    heading.textContent = formatEventType(event.event_type);

                    const property = document.createElement("p");
                    const eventListingId =
                        event.listing_id ?? event.id ?? "Unknown";

                    property.textContent =
                        `Property: ${event.title || "Unknown property"} (ID: ${eventListingId})`;

                    const description = document.createElement("p");
                    description.textContent =
                        `Date: ${event.timestamp || "Unknown"} | ` +
                        `Old price: ${formatPrice(event.old_price)} | ` +
                        `New price: ${formatPrice(event.new_price)}`;

                    item.append(heading, property, description);

                    if (event.event_type === "PRICE_CHANGED") {
                        const analytics = event.price_change;
                        const analysisLine = document.createElement("p");
                        analysisLine.className = "price-analysis";

                        if (analytics) {
                            const amount = formatPrice(
                                Math.abs(analytics.difference)
                            );

                            const percentage =
                                analytics.percentage_change === null
                                    ? "undefined (old price was zero)"
                                    : `${analytics.percentage_change.toFixed(2)}%`;

                            analysisLine.textContent =
                                `Price ${analytics.direction} by ${amount} (${percentage})`;
                        } else {
                            analysisLine.textContent =
                                "Price-change analytics unavailable.";
                        }

                        item.appendChild(analysisLine);
                    }

                    history.appendChild(item);
                }
            }

            async function showDetails(listingId) {
                const panel = document.getElementById("listingDetails");
                const title = document.getElementById("detailTitle");
                const info = document.getElementById("detailInfo");
                const history = document.getElementById("eventHistory");

                panel.hidden = false;
                title.textContent = "Loading property...";
                info.textContent = "";
                history.textContent = "Loading event history...";
                currentEvents = [];

                document.getElementById("eventCount").textContent = "0 events";
                document.getElementById("eventFilter").value = "ALL";

                panel.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

                try {
                    const encodedId = encodeURIComponent(listingId);

                    const [listingResponse, eventsResponse] = await Promise.all([
                        fetch(`/listings/${encodedId}`),
                        fetch(`/listings/${encodedId}/events`)
                    ]);

                    if (!listingResponse.ok || !eventsResponse.ok) {
                        throw new Error("Could not retrieve property details.");
                    }

                    const listing = await listingResponse.json();
                    const events = await eventsResponse.json();

                    title.textContent = listing.title || "Untitled property";

                    info.textContent =
                        `ID: ${listing.id} | ` +
                        `City: ${listing.city || "Unknown"} | ` +
                        `Transaction: ${listing.transaction_type || "Unknown"} | ` +
                        `Price: ${formatPrice(listing.price)}`;

                    currentEvents = Array.isArray(events) ? events : [];

                    // The selected listing supplies reliable title and ID
                    // even if an event response omits those fields.
                    currentEvents = currentEvents.map(event => ({
                        ...event,
                        title: event.title || listing.title,
                        listing_id: event.listing_id || listing.id
                    }));

                    renderEventHistory();
                } catch (error) {
                    title.textContent = "Could not load property";
                    info.textContent = error.message;
                    currentEvents = [];

                    document.getElementById("eventCount").textContent = "0 events";
                    history.textContent = "Check the API and try again.";

                    console.error(error);
                }
            }

            async function loadListings() {
                const message = document.getElementById("message");
                const refreshButton = document.getElementById("refresh");

                refreshButton.disabled = true;
                message.textContent = "Loading listings...";

                try {
                    const response = await fetch("/listings");

                    if (!response.ok) {
                        throw new Error("The API returned an error.");
                    }

                    const data = await response.json();

                    if (!Array.isArray(data)) {
                        throw new Error("Unexpected API response.");
                    }

                    allListings = data;

                    document.getElementById("total").textContent =
                        allListings.length;

                    document.getElementById("priced").textContent =
                        allListings.filter(item =>
                            item.price !== null &&
                            item.price !== undefined &&
                            item.price !== ""
                        ).length;

                    document.getElementById("cities").textContent =
                        new Set(
                            allListings.map(item => item.city).filter(Boolean)
                        ).size;

                    renderListings();
                } catch (error) {
                    message.textContent =
                        "Could not load listings. Check that the API is running.";

                    console.error(error);
                } finally {
                    refreshButton.disabled = false;
                }
            }

            document.getElementById("search")
                .addEventListener("input", renderListings);

            document.getElementById("type")
                .addEventListener("change", renderListings);

            document.getElementById("refresh")
                .addEventListener("click", loadListings);

            document.getElementById("eventFilter")
                .addEventListener("change", renderEventHistory);

            document.getElementById("closeDetails")
                .addEventListener("click", () => {
                    document.getElementById("listingDetails").hidden = true;
                });

            loadListings();
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
