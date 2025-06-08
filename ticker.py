from typing import Any, Union
import pandas as pd
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP service
mcp = FastMCP("nse-ticker")
tickers_df = pd.read_csv('configs/NSE.csv')

def get_instrument_key(symbol:str):
    exchange_nse = "NSE_EQ"
    filtered_df = tickers_df[(tickers_df['exchange'] == exchange_nse) & (tickers_df['tradingsymbol'] == symbol)]
    instrument_key = filtered_df['instrument_key'].values[0] if not filtered_df.empty else None
    return instrument_key


async def fetch_upstox_data(
    instrument_key: str,
    from_date: str,
    to_date: str,
    interval: str = "day"
) -> Union[list[dict[str, Any]], dict[str, str]]:
    """Fetch historical data from Upstox API."""
    if not instrument_key:
        return {"error": "Invalid instrument_key"}

    url = f"https://api.upstox.com/v2/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"
    headers = {
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()  # Remove await here

            # Check if data structure exists
            if 'data' not in data or 'candles' not in data['data']:
                return {"error": "Invalid response structure from API"}
            
            candle_data = data['data']['candles']
            
            # Handle empty candle data
            if not candle_data:
                return {"error": "No candle data found for the given parameters"}
            
            df = pd.DataFrame(
                candle_data,
                columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'OI']  
            )
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            df = df.to_json(orient="records", date_format="iso")
            return df
            
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"error": f"Request error: {str(e)}"}
        except KeyError as e:
            return {"error": f"Missing key in response: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool(
    name="get_historical_candle",
    description="""Get historical stock prices for NSE stocks through Upstox API. Returns OHLCV data in tabular format.
Args:
    symbol: str
        The NSE stock symbol, e.g. "HDFCBANK"
    from_date: str
        Start date in YYYY-MM-DD format
    to_date: str
        End date in YYYY-MM-DD format
    interval: str
        Valid intervals: minute, 30minute, day, week, month
        Default is "day"
""",
)
async def get_historical_candle(
    symbol: str,
    from_date: str,
    to_date: str,
    interval: str = "day"
) -> str:
    """Get historical stock data from Upstox.

    Args:
        symbol: str
            The NSE stock symbol, e.g. "HDFCBANK"
        from_date: str
            Start date in YYYY-MM-DD format
        to_date: str
            End date in YYYY-MM-DD format
        interval: str
            Valid intervals: minute, 30minute, day, week, month
            Default is "day"
    """
    instrument_key = get_instrument_key(symbol)
    if not instrument_key:
        return f"Error: Invalid symbol {symbol} or instrument key not found"

    try:
        result = await fetch_upstox_data(instrument_key, from_date, to_date, interval)
        
        if isinstance(result, dict) and "error" in result:
            return f"Error: {result['error']}"

        # Convert JSON string back to DataFrame
        df = pd.read_json(result)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df = df.round(2)
        return df.to_dict(orient="records")

    except Exception as e:
        return f"Error: Failed to fetch data for {symbol}: {str(e)}"

if __name__ == "__main__":
    print("Starting Upstox Ticker MCP service...")
    mcp.run(transport="stdio")