import os
import requests
import json
from typing import Type, Optional
import logging

from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# --- Prerequisites ---
# 1. Run the MCP server: `go run ./app` in the `app` directory.
# 2. Install libraries: `pip install langchain langchain-openai requests`
# 3. Set OpenAI API Key: `export OPENAI_API_KEY="your_openai_api_key"`
# ---------------------

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CategorySearchToolInput(BaseModel):
    """Input for the category search tool."""
    category_group_code: str = Field(description="The category group code to search for (e.g., 'PM9' for pharmacy, 'CE7' for cafe).")
    latitude: float = Field(description="The latitude for the center of the search radius.")
    longitude: float = Field(description="The longitude for the center of the search radius.")
    radius: Optional[int] = Field(description="The search radius in meters (0-20000). Default is 1000m.")


class CategorySearchTool(BaseTool):
    """A tool to find places of a specific category around a coordinate."""
    name: str = "korean_category_search"
    description: str = "Useful for finding places of a specific category (like pharmacy, cafe) around a given coordinate. Category codes are required (e.g., PM9 for pharmacy, CE7 for cafe)."
    args_schema: Type[BaseModel] = CategorySearchToolInput

    def _run(self, category_group_code: str, latitude: float, longitude: float, radius: Optional[int] = 1000) -> str:
        """Use the tool."""
        mcp_server_url = "http://localhost:8080/search/category"
        params = {
            "category_group_code": category_group_code,
            "y": latitude,
            "x": longitude,
            "radius": radius
        }
        logging.info(f"Requesting {mcp_server_url} with params: {params}")

        try:
            response = requests.get(mcp_server_url, params=params)
            logging.info(f"Response Status Code: {response.status_code}")
            response.raise_for_status()

            # 디버깅을 위해 서버로부터 받은 원본 응답 텍스트를 로깅합니다.
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
                results = [f"Place: {doc.get('place_name')}, Address: {doc.get('address_name')}" for doc in data["documents"][:3]]
                return "\n".join(results)
            else:
                logging.warning("No documents found in the response.")
                return "No results found for the given category and location."

        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP Request failed: {e}")
            return f"Error calling the API: {e}"
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from response: {e}. Response text: '{response.text}'")
            return f"Error parsing server response. The response was not valid JSON: {response.text}"


def main():
    """Initializes and runs a LangChain agent with the category search tool."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    tools = [CategorySearchTool()]

    agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

    question = "서울시청 근처에 있는 약국들을 찾아줘. 서울시청 좌표는 위도 37.5665, 경도 126.9780 이고, 카테고리 코드는 PM9 이야."
    result = agent.invoke({"input": question})
    print("\n--- 최종 답변 ---")
    print(result["output"])

if __name__ == "__main__":
    main()