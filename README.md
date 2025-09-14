
```markdown
# API Test MCP Server

This project implements a **Minimal Compute Protocol (MCP) server** that provides tools for quickly generating and managing **test data** against a REST API. It’s designed for developers who want to **seed their test environments** with realistic products, customers, and reset data — all through the MCP standard.

---

## ✨ Features

- **Create Test Products**
  - Generates realistic product records with:
    - Name (catchphrase)
    - Description
    - Category (custom or random)
    - Price
    - Stock quantity
    - SKU
  - Sends data to `/products` endpoint.

- **Create Test Customers**
  - Generates realistic customer records with:
    - First/last name
    - Email
    - Address
    - Phone number
  - Sends data to `/customers` endpoint.

- **Clear Test Data**
  - Calls a special endpoint (`/admin/reset-test-db`) to wipe all test data.
  - **Dangerous: only use on test environments.**

- **Faker Integration**
  - Uses [Faker](https://faker.readthedocs.io/) to generate believable random data.

- **Error Handling & Retries**
  - Retries failed API calls with exponential backoff.
  - Returns structured JSON results for easier parsing.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- [asyncio](https://docs.python.org/3/library/asyncio.html) – async event loop
- [httpx](https://www.python-httpx.org/) – async HTTP client
- [Faker](https://faker.readthedocs.io/) – fake data generation
- [mcp](https://pypi.org/project/mcp/) – Minimal Compute Protocol server library
- [anyio](https://anyio.readthedocs.io/) – async backend

---

## 📂 Project Structure

```

.
├── main.py        # MCP server implementation
├── requirements.txt  # Dependencies
└── README.md      # Project documentation

````

---

## 🚀 Usage

1. **Clone the repo** and set up a virtual environment:

   ```bash
   git clone https://github.com/yourusername/py-mcp.git
   cd py-mcp
   python -m venv env
   source env/bin/activate   # (or env\Scripts\activate on Windows)
````

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**

   ```bash
   python main.py
   ```

4. The server starts in **stdio mode**, ready to accept MCP client connections.

---

## 🔧 Configuration

By default, the server connects to:

```
http://localhost:8000/api
```

If you want to target another API, update the `API_BASE_URL` in `main.py`, or pass it via initialization options (future enhancement).

---

## ⚠️ Warnings

* **Do not use in production.**
  The `clear_test_data` tool will wipe your database.
* Always ensure you’re pointing at a **test environment**.

---

## 📜 License

MIT License – feel free to use, modify, and share.


