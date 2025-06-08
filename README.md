# NSE Ticker MCP Server

A Model Context Protocol (MCP) server that provides access to National Stock Exchange (NSE) data through Upstox API.

## Tools

The server exposes the following tools through the Model Context Protocol:

### Historical Data
| Tool | Description |
|------|-------------|
| `get_historical_candle` | Get historical OHLCV (Open, High, Low, Close, Volume) data for NSE stocks |

## Features

- Real-time NSE stock data access
- Multiple time intervals support (minute, 30minute, day, week, month)
- Error handling and data validation
- Historical price data with customizable date ranges

## Requirements

- Python 3.11 or higher
- Dependencies (specified in pyproject.toml):
  - mcp
  - pandas
  - httpx
  - pydantic

## Setup

1. Clone this repository:
```sh
git clone https://github.com/sougatabh/nse-ticker-mcp.git
cd nse-ticker-mcp
```

2. Create and activate a virtual environment:
```sh
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```sh
pip install -e .
```

## Usage

### Development Mode

Test the server with MCP Inspector:

```sh
python ticker.py
```

### Integration with Claude for Desktop

1. Install Claude for Desktop

2. Edit Claude's config file:

**MacOS**:
```sh
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Add the following configuration:
```json
{
  "mcpServers": {
    "nse-ticker": {
      "command": "python",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/nse-ticker-mcp",
        "ticker.py"
      ]
    }
  }
}
```

### Example Usage

```python
# Get historical data for HDFC Bank
response = await get_historical_candle(
    symbol="HDFCBANK",
    from_date="2024-01-01",
    to_date="2024-03-31",
    interval="day"
)
```

## Available Intervals

- `minute` - 1-minute candles
- `30minute` - 30-minute candles
- `day` - Daily candles
- `week` - Weekly candles
- `month` - Monthly candles

## Error Handling

The server provides detailed error messages for:
- Invalid symbols
- Connection issues
- API errors
- Data validation failures
- Date format issues

## Configuration

Stock symbols and instrument keys are configured in:
- `configs/NSE.csv`

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request