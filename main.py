import asyncio
import httpx
import json
import logging
from faker import Faker
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize the MCP Server and Faker
server = Server("inventory-mcp")
fake = Faker()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define your API's base URL
API_BASE_URL = "http://localhost:8000/"  # Change this to your test API's URL

# --- Tool Schemas ---
CREATE_PRODUCTS_SCHEMA = {
    "type": "object",
    "properties": {
        "count": {"type": "number", "description": "Number of test products to create."},
        "category": {
            "type": "string",
            "description": "Primary category for the products (e.g., 'electronics', 'clothing').",
            "nullable": True
        },
    },
    "required": ["count"],
}

CREATE_CUSTOMERS_SCHEMA = {
    "type": "object",
    "properties": {
        "count": {"type": "number", "description": "Number of test customers to create."}
    },
    "required": ["count"],
}

CLEAR_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "confirm": {
            "type": "boolean",
            "description": "You must set this to true to confirm you want to delete all data."
        }
    },
    "required": ["confirm"],
}


# --- Register Tools ---
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_test_products",
            description="Creates realistic test products by making POST requests to the /products API endpoint.",
            inputSchema=CREATE_PRODUCTS_SCHEMA,
        ),
        Tool(
            name="create_test_customers",
            description="Creates realistic test customer profiles by making POST requests to the /customers API endpoint.",
            inputSchema=CREATE_CUSTOMERS_SCHEMA,
        ),
        Tool(
            name="clear_test_data",
            description="**DANGER**: Deletes all data from the test database. Only use on a test environment!",
            inputSchema=CLEAR_DATA_SCHEMA,
        ),
    ]


# --- Helper: API Request with Retry ---
async def api_post_with_retry(client: httpx.AsyncClient, endpoint: str, payload: dict, retries: int = 3) -> dict:
    for attempt in range(1, retries + 1):
        try:
            response = await client.post(endpoint, json=payload, timeout=30.0)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logging.warning(f"Attempt {attempt} failed for {endpoint}: {e}")
            if attempt == retries:
                return {"status": "error", "error": str(e), "payload": payload}
            await asyncio.sleep(2 ** attempt)  # exponential backoff


# --- Tool Handlers ---
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "create_test_products":
        count = arguments.get("count", 1)
        category = arguments.get("category") or fake.word()

        results = []
        async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
            for _ in range(count):
                product_data = {
                    "name": fake.catch_phrase(),
                    "description": fake.paragraph(),
                    "category": category,
                    "price": round(fake.random_number(digits=2) + fake.random_number(digits=2) / 100, 2),
                    "quantity": fake.random_int(min=0, max=1000),
                }
                result = await api_post_with_retry(client, "/products/products", product_data)
                if result["status"] == "success":
                    result["product"] = product_data
                results.append(result)

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    elif name == "create_test_customers":
        if not arguments.get("count"):
            return [TextContent(type="text", text=json.dumps({"error": "'count' argument is required."}))]

        count = arguments["count"]
        results = []
        async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
            for _ in range(count):
                customer_data = {
                    "firstName": fake.first_name(),
                    "lastName": fake.last_name(),
                    "email": fake.unique.email(),
                    "address": fake.address().replace("\n", ", "),
                    "phoneNumber": fake.phone_number(),
                }

                result = await api_post_with_retry(client, "/customers", customer_data)
                if result["status"] == "success":
                    result["customer"] = customer_data
                results.append(result)

        # Clear Faker unique constraints to avoid collisions later
        fake.unique.clear()

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    elif name == "clear_test_data":
        if not arguments.get("confirm"):
            return [TextContent(type="text", text=json.dumps({"status": "cancelled", "reason": "Confirmation required"}))]

        async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
            result = await api_post_with_retry(client, "/admin/reset-test-db", {})
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


# --- Main Entry Point ---
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream,initialization_options={})


if __name__ == "__main__":
    asyncio.run(main())
