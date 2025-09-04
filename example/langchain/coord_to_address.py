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

class CoordToAddressToolInput(BaseModel):
    """Input for the coordinate to address conversion tool."""
    latitude: float = Field(description="The latitude coordinate.")
    longitude: float = Field(description="The longitude coordinate.")


class CoordToAddressTool(BaseTool):
    """A tool to convert geographic coordinates into a Korean address."""
    name: str = "korean_coord_to_address"
    description: str = "Useful for converting geographic coordinates (latitude, longitude) into a Korean street address or lot number address."
    args_schema: Type[BaseModel] = CoordToAddressToolInput

    def _run(self, latitude: float, longitude: float) -> str:
        """Use the tool."""
        mcp_server_url = "http://localhost:8080/geo/coord2address"
        params = {"y": latitude, "x": longitude}
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

            logging.info(f"Parsed JSON data: {data}")

            if data and data.get("documents"):
                first_doc = data["documents"][0]
                # road_address 또는 address가 None일 수 있는 경우를 안전하게 처리
                road_address_obj = first_doc.get('road_address')
                road_address = road_address_obj.get('address_name', 'N/A') if road_address_obj else 'N/A'
                
                address_obj = first_doc.get('address')
                lot_address = address_obj.get('address_name', 'N/A') if address_obj else 'N/A'

                return f"Road Address: {road_address}, Lot Address: {lot_address}"
            else:
                logging.warning("No documents found in the response.")
                return "Could not find an address for the given coordinates."

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
    """Initializes and runs a LangChain agent with the coord-to-address tool."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    tools = [CoordToAddressTool()]

    agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

    question = "위도 37.5143, 경도 127.0628는 어디 주소야?"
    result = agent.invoke({"input": question})
    print("\n--- 최종 답변 ---")
    print(result["output"])

if __name__ == "__main__":
    main()