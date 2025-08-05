from mcp import ClientSession
from mcp.client.sse import sse_client
import json


async def run():
    try:
        async with sse_client(url="http://localhost:8000/sse") as streams:
            async with ClientSession(*streams) as session:

                await session.initialize()

                print("Listing Tools:")
                tools = await session.list_tools()
                print(tools.model_dump_json(indent=4))

                print("\nCalling Calculator Tool:")
                result = await session.call_tool("calculator", arguments={"expression": "2 + 3 * 4"})
                print(result.model_dump_json(indent=4))

                print("\nCalling File Writer Tool:")
                result = await session.call_tool("file_writer", arguments={"file_path": "test.txt", "content": "This is test text."})
                print(result.model_dump_json(indent=4))

                print("\nCalling File Reader Tool:")
                result = await session.call_tool("file_reader", arguments={"file_path": "test.txt"})
                print(result.model_dump_json(indent=4))

                print("\nCalling List Files Tool:")
                result = await session.call_tool("list_files", arguments={"directory": "."})
                print(result.model_dump_json(indent=4))

                print("\nCalling System Time Tool:")
                result = await session.call_tool("system_time", arguments={})
                print(result.model_dump_json(indent=4))
    except Exception as e:
        print(f"Failed to establish connection: {str(e)}")

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
