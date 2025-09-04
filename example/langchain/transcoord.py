import os
import requests
import json
from typing import Type
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

class TransCoordToolInput(BaseModel):
    """Input for the coordinate transformation tool."""
    longitude: float = Field(description="The x-coordinate to transform.")
    latitude: float = Field(description="The y-coordinate to transform.")
    input_coord: str = Field(description="The input coordinate system. e.g., WTM, WGS84.")
    output_coord: str = Field(description="The target coordinate system. e.g., WGS84, WTM.")


class TransCoordTool(BaseTool):
    """A tool to convert coordinates from one system to another."""
    name: str = "korean_coordinate_transformer"
    description: str = "Useful for converting coordinates between different systems like WGS84 and WTM."
    args_schema: Type[BaseModel] = TransCoordToolInput

    def _run(self, latitude: float, longitude: float, input_coord: str, output_coord: str) -> str:
        """Use the tool."""
        mcp_server_url = "http://localhost:8080/geo/transcoord"
        params = {
            "y": latitude,
            "x": longitude,
            "input_coord": input_coord,
            "output_coord": output_coord
        }
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
                first_doc = data["documents"][0]
                return f"Converted Coordinates -> Latitude: {first_doc.get('y')}, Longitude: {first_doc.get('x')}"
            else:
                logging.warning("No documents found in the response.")
                return "Could not transform the coordinates."

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
    """Initializes and runs a LangChain agent with the transcoord tool."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    tools = [TransCoordTool()]

    agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

    question = "WTM 좌표계의 x: 160710.3, y: -4388.8을 WGS84 좌표계로 변환해줘."
    result = agent.invoke({"input": question})
    print("\n--- 최종 답변 ---")
    print(result["output"])

if __name__ == "__main__":
    main()