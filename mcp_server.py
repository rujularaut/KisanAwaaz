"""
mcp_server.py — MCP Tool Definitions for KisanAwaaz

Tools available:
1. get_mandi_price — fetches live price for a commodity at a specific market
2. get_best_mandi  — finds the mandi offering the HIGHEST price for a commodity
                     (farmers are sellers — they want maximum price)
"""

from tools.mandi_tool import get_mandi_price as _get_mandi_price
from tools.mandi_tool import _translate_commodity, STATE_MAP
import requests
import os


# ── Tool Definitions (described to LLM in the prompt) ────────────────────────
TOOLS_DESCRIPTION = """
You have access to these tools. Respond with ONLY a JSON object to call a tool.

TOOL 1: get_mandi_price
Use when farmer asks price at a specific market.
Response format:
{"tool": "get_mandi_price", "commodity": "<Hindi name>", "market": "<Hindi name>", "state": "<Hindi or empty>"}

TOOL 2: get_best_mandi
Use when farmer asks where they can get the best/highest price for their crop.
Response format:
{"tool": "get_best_mandi", "commodity": "<Hindi name>", "state": "<Hindi or empty>"}

Examples:
Query: "बड़वानी मंडी में टमाटर का भाव क्या है?"
Response: {"tool": "get_mandi_price", "commodity": "टमाटर", "market": "बड़वानी", "state": ""}

Query: "टमाटर का सबसे अच्छा भाव कहाँ मिलेगा?"
Response: {"tool": "get_best_mandi", "commodity": "टमाटर", "state": ""}

Query: "राजस्थान में आलू सबसे महंगा कहाँ बिकता है?"
Response: {"tool": "get_best_mandi", "commodity": "आलू", "state": "राजस्थान"}

Query: "जयपुर मंडी में प्याज का दाम बताओ"
Response: {"tool": "get_mandi_price", "commodity": "प्याज", "market": "जयपुर", "state": "राजस्थान"}
"""


def execute_tool(tool_name: str, tool_args: dict) -> dict:
    """
    Execute the tool requested by the LLM and return the result.
    This is the MCP server's core — bridges LLM decisions to real actions.
    """
    print(f"   MCP executing tool : {tool_name}")
    print(f"    Arguments          : {tool_args}")

    # ── Tool 1: get_mandi_price ──────────────────────────────────────────
    if tool_name == "get_mandi_price":
        result = _get_mandi_price(
            tool_args.get("commodity", ""),
            tool_args.get("market", ""),
            tool_args.get("state", "")
        )
        print(f"    Result             : {result}")
        return result

    # ── Tool 2: get_best_mandi ───────────────────────────────────────────
    elif tool_name == "get_best_mandi":
        commodity    = tool_args.get("commodity", "")
        state        = tool_args.get("state", "")
        commodity_en = _translate_commodity(commodity)
        state_en     = STATE_MAP.get(state.strip(), "") if state else ""

        params = {
            "api-key":            os.getenv("DATA_GOV_API_KEY"),
            "format":             "json",
            "filters[commodity]": commodity_en,
            "limit":              100,
        }
        if state_en:
            params["filters[state]"] = state_en

        try:
            resp    = requests.get(
                "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
                params=params, timeout=30
            )
            records = resp.json().get("records", [])
        except Exception as e:
            return {"error": str(e)}

        if not records:
            return {"error": "No data found", "commodity": commodity_en}

        # Farmers are SELLERS — find mandi with HIGHEST modal price
        best   = max(records, key=lambda r: float(r.get("modal_price", 0) or 0))
        result = {
            "commodity":   best.get("commodity"),
            "market":      best.get("market"),
            "state":       best.get("state"),
            "min_price":   best.get("min_price"),
            "max_price":   best.get("max_price"),
            "modal_price": best.get("modal_price"),
            "date":        best.get("arrival_date", "unknown"),
        }
        print(f"    Best mandi result  : {result}")
        return result

    else:
        return {"error": f"Unknown tool: {tool_name}"}