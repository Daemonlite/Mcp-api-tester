import asyncio
import httpx
import json
import logging
from pathlib import Path
from faker import Faker
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP Server and Faker
server = Server("api-test-server")
fake = Faker()

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- Load Config ---
CONFIG_PATH = Path(__file__).parent / "config.json"

if not CONFIG_PATH.exists():
    raise FileNotFoundError("❌ Missing config.json file. Please create it before running.")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

API_BASE_URL = CONFIG.get("api_base_url")
ENDPOINTS = CONFIG.get("endpoints", {})


# --- Dynamic Tool Registration from Config ---
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    tools = []

    if "products" in ENDPOINTS:
        tools.append(
            Tool(
                name="create_test_products",
                description="Creates test products by calling the /products API endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {"count": {"type": "number", "description": "Number of products to create."}},
                    "required": ["count"],
                },
            )
        )

    if "customers" in ENDPOINTS:
        tools.append(
            Tool(
                name="create_test_customers",
                description="Creates test customers by calling the /customers API endpoint.",
                inputSchema={
                    "type": "object",
                    "properties": {"count": {"type": "number", "description": "Number of customers to create."}},
                    "required": ["count"],
                },
            )
        )

    if "reset" in ENDPOINTS:
        tools.append(
            Tool(
                name="clear_test_data",
                description="**DANGER**: Clears all test data via /admin/reset-test-db.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "confirm": {"type": "boolean", "description": "Set to true to confirm data wipe."}
                    },
                    "required": ["confirm"],
                },
            )
        )

    return tools


# --- Helper: Generate Fake Data Based on Config ---
def generate_fake_data(field_map: dict) -> dict:
    data = {}
    for key, faker_method in field_map.items():
        if faker_method == "int":
            data[key] = fake.random_int(min=0, max=1000)
        elif faker_method == "price":
            data[key] = round(fake.random_number(digits=2) + fake.random_number(digits=2) / 100, 2)
        elif faker_method == "sku":
            data[key] = fake.bothify(text="????-####")
        elif hasattr(fake, faker_method):
            value = getattr(fake, faker_method)()
            if isinstance(value, str):
                data[key] = value.replace("\n", ", ")  # flatten addresses
            else:
                data[key] = value
        else:
            data[key] = f"<no faker method: {faker_method}>"
    return data


# --- Helper: API Post with Retry ---
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
    results = []

    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        if name == "create_test_products" and "products" in ENDPOINTS:
            count = arguments.get("count", 1)
            fields = ENDPOINTS["products"]["fields"]
            path = ENDPOINTS["products"]["path"]

            for _ in range(count):
                payload = generate_fake_data(fields)
                result = await api_post_with_retry(client, path, payload)
                results.append(result)

        elif name == "create_test_customers" and "customers" in ENDPOINTS:
            count = arguments.get("count", 1)
            fields = ENDPOINTS["customers"]["fields"]
            path = ENDPOINTS["customers"]["path"]

            for _ in range(count):
                payload = generate_fake_data(fields)
                result = await api_post_with_retry(client, path, payload)
                results.append(result)

            fake.unique.clear()

        elif name == "clear_test_data" and "reset" in ENDPOINTS:
            if not arguments.get("confirm"):
                return [TextContent(type="text", text=json.dumps({"status": "cancelled", "reason": "Confirmation required"}))]

            path = ENDPOINTS["reset"]["path"]
            result = await api_post_with_retry(client, path, {})
            results.append(result)

        else:
            raise ValueError(f"Unknown tool: {name}")

    return [TextContent(type="text", text=json.dumps(results, indent=2))]


# --- Main Entry Point ---
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, initialization_options={})


if __name__ == "__main__":
    asyncio.run(main())
    
