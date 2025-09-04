import os
import requests
import json
import logging as log
from typing import Type, Optional
from pydantic import Field
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# --- Prerequisites ---
# 1. Run the MCP server: `go run ./app` in the `app` directory.
# 2. Install libraries: `pip install langchain langchain-openai requests`
# 3. Set OpenAI API Key: `export OPENAI_API_KEY="your_openai_api_key"`
# ---------------------


class AddressSearchToolInput(BaseModel):
    """Input for the address search tool."""
    query: str = Field(description="The Korean address to search for coordinates.")


class AddressSearchTool(BaseTool):
    """A tool to find coordinates for a given Korean address."""
    name: str = "korean_address_search"
    description: str = "Useful for when you need to find the coordinates (latitude and longitude) of a Korean address."
    args_schema: Type[BaseModel] = AddressSearchToolInput

    def _run(self, query: str) -> str:
        """Use the tool."""
        mcp_server_url = "http://localhost:8080/search/address"
        params = {"query": query}

        try:
            response = requests.get(mcp_server_url, params=params)
            response.raise_for_status()
            data = response.json()

            # 결과에서 필요한 정보만 추출하여 반환
            if data and data.get("documents"):
                # 첫 번째 결과만 사용
                first_doc = data["documents"][0]
                address_name = first_doc.get('address_name', 'N/A')
                x = first_doc.get('x', 'N/A') # 경도(longitude)
                y = first_doc.get('y', 'N/A') # 위도(latitude)
                return f"Address: {address_name}, Latitude: {y}, Longitude: {x}"
            else:
                return "No results found for the given address."

        except requests.exceptions.RequestException as e:
            return f"Error calling the API: {e}"
        except (KeyError, IndexError):
            return "Could not parse the API response."


def main():
    """
    Initializes a LangChain agent with the address search tool and runs it.
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    # LLM과 Tool 준비
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    tools = [AddressSearchTool()]

    # Agent 초기화
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

    # Agent 실행
    question = "서울시 강남구 삼성동 159-1번지 코엑스의 좌표를 찾아줘."
    result = agent.invoke({"input": question})
    print("\n--- 최종 답변 ---")
    print(result["output"])

if __name__ == "__main__":
    main()
