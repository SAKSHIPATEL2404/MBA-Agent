
import math, requests

def calculator(expression: str):
    
    try:
        
        result = eval(expression, {"__builtins__": {}}, {})
        return {"type": "calculator", "result": result}
    except Exception as e:
        return {"error": str(e)}

def web_search(query: str):
    
    return [{"title": "Search Disabled", "snippet": f"Mock search results for: {query}", "url": ""}]
