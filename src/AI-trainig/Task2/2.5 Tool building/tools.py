import httpx


def currency_exchange_tool(
    from_currency: str,
    to_currency: str,
    amount: float
):
    url = "https://api.frankfurter.dev/v1/latest"

    params = {
        "base": from_currency,
        "symbols": to_currency
    }

    response = httpx.get(
        url,
        params=params
    )

    response.raise_for_status()

    data = response.json()

    print("API Response:", data)

    exchange_rate = data["rates"][to_currency]

    result = amount * exchange_rate

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": amount,
        "exchange_rate": exchange_rate,
        "result": result
    }

def calculate_tool(expression: str):
    try:
        result = eval(expression)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "currency_exchange_tool",
            "description": (
                "Convert an amount from one currency to another using "
                "the current exchange rate."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": (
                            "The currency code to convert from. "
                            "For example, USD for US Dollar."
                        )
                    },
                    "to_currency": {
                        "type": "string",
                        "description": (
                            "The currency code to convert to. "
                            "For example, INR for Indian Rupee."
                        )
                    },
                    "amount": {
                        "type": "number",
                        "description": "The amount of money to convert."
                    }
                },
                "required": [
                    "from_currency",
                    "to_currency",
                    "amount"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_tool",
            "description": "Calculate a mathematical expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "The mathematical expression to calculate. "
                            "For example, 2 + 2 * 3."
                        )
                    }
                },
                "required": ["expression"]
            }
        }
    }
]