import os
import requests
import json
from typing import Type, Optional
import logging

from langchain.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# --- Prerequisites ---
# 1. Run the MCP server: `go run ./app` in the `app` directory.
# 2. Install libraries: `pip install langchain langchain-openai requests`
# 3. Set OpenAI API Key: `export OPENAI_API_KEY="your_openai_api_key"`
# ---------------------

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KeywordSearchToolInput(BaseModel):
    """Input for the keyword search tool."""
    query: str = Field(description="The keyword to search for, such as a place name or category.")
    latitude: Optional[float] = Field(description="The latitude for the center of the search radius.")
    longitude: Optional[float] = Field(description="The longitude for the center of the search radius.")
    radius: Optional[int] = Field(description="The search radius in meters (0-20000).")


class KeywordSearchTool(BaseTool):
    """A tool to find places based on a keyword."""
    name: str = "korean_keyword_search"
    description: str = "Useful for when you need to find places in Korea based on a keyword (e.g., 'Kakao Friends', '맛집'). You can optionally provide coordinates and a radius to search a specific area."
    args_schema: Type[BaseModel] = KeywordSearchToolInput

    def _run(self, query: str, latitude: Optional[float] = None, longitude: Optional[float] = None, radius: Optional[int] = None) -> str:
        """Use the tool."""
        mcp_server_url = "http://localhost:8080/search/keyword"
        params = {"query": query}
        if latitude is not None:
            params["y"] = latitude
        if longitude is not None:
            params["x"] = longitude
        if radius is not None:
            params["radius"] = radius
        logging.info(f"Requesting {mcp_server_url} with params: {params}")

        try:
            response = requests.get(mcp_server_url, params=params)
            logging.info(f"Response Status Code: {response.status_code}")
            response.raise_for_status()

            raw_response_text = response.text
            logging.info(f"Raw Response Text: {raw_response_text}")

            # 서버가 SSE 형식("data: ...")으로 응답하는 경우를 처리합니다.
            if raw_response_text.strip().startswith('data:'):
                # "data: " 접두사를 제거하고 JSON으로 파싱합니다.
                json_data = raw_response_text.strip()[len('data:'):].strip()
                data = json.loads(json_data)
            else:
                # 일반 JSON 형식으로 파싱합니다.
                data = response.json()

            if data and data.get("documents"):
                # Return up to 3 results for brevity
                results = [f"Place: {doc.get('place_name')}, Address: {doc.get('address_name')}" for doc in data["documents"][:3]]
                return "\n".join(results)
            else:
                logging.warning("No documents found in the response.")
                return "No results found for the given keyword."

        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP Request failed: {e}")
            return f"Error calling the API: {e}"
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from response: {e}. Response text: '{response.text}'")
            return f"Error parsing server response. The response was not valid JSON: {response.text}"
        except (KeyError, IndexError, AttributeError) as e:
            logging.error(f"Error parsing response structure: {e}")
            return "Could not parse the API response."


def main():
    """Initializes and runs a LangChain agent with the keyword search tool."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    tools = [KeywordSearchTool()]

    agent = initialize_agent(
        tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True
    )

    question = "강남역 근처에 있는 카카오프렌즈 매장을 찾아줘."
    result = agent.invoke({"input": question})
    print("\n--- 최종 답변 ---")
    print(result["output"])

if __name__ == "__main__":
    main()