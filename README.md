

# 🛠️ MCP API Integration Tool

This project is a **Model Context Protocol (MCP) server** that enables you to integrate with any REST API.
Instead of hardcoding endpoints and request payloads, it uses a `config.json` file where you can define:

* The **API base URL**
* A list of **endpoints** with their paths and fields
* Example payloads to guide requests

This makes it flexible for connecting to different APIs without modifying the code.

---

## 📂 Project Structure

```
py-mcp/
│── main.py         # MCP server implementation
│── config.json     # Stores base URL, endpoints, and payload field definitions
│── README.md       # Project documentation
```

---

## ⚙️ Configuration (`config.json`)

The `config.json` file controls how the MCP server connects to your API.

Example:

```json
{
  "api_base_url": "http://localhost:8000/api",
  "endpoints": {
    "products": {
      "path": "/products",
      "method": "POST",
      "fields": {
        "name": "string",
        "price": "float",
        "stockQuantity": "integer"
      }
    },
    "customers": {
      "path": "/customers",
      "method": "POST",
      "fields": {
        "firstName": "string",
        "lastName": "string",
        "email": "string"
      }
    }
  }
}
```

* `api_base_url` → The root URL of your API
* `endpoints` → A dictionary of available endpoints

  * Each endpoint has:

    * `path`: the URL path (e.g., `/products`)
    * `method`: HTTP method (`POST`, `GET`, `PUT`, `DELETE`)
    * `fields`: expected request body fields

---

## 🚀 Running the MCP Server

1. Install dependencies:

```bash
pip install mcp httpx anyio
```

2. Ensure your `config.json` is set up correctly.

3. Run the MCP server:

```bash
py main.py
```

---

## 🧩 Example Usage

* With the `config.json` above, you can call:

```json
{
  "endpoint": "products",
  "payload": {
    "name": "Laptop",
    "price": 1200,
    "stockQuantity": 50
  }
}
```

The server will send this request to:

```
POST http://localhost:8000/api/products
```

And return the API’s response.

---

## 🌟 Features

* ✅ MCP-compatible server
* ✅ Loads endpoints dynamically from `config.json`
* ✅ Supports multiple APIs without code changes
* ✅ Validates required payload fields
* ✅ Flexible for REST API integrations

---

