from mcp import ClientSession
from mcp.client.sse import sse_client
import json


async def run():
    async with sse_client(url="http://localhost:8000/sse") as streams:
        async with ClientSession(*streams) as session:

            await session.initialize()

            print("Listing Tools:")
            tools = await session.list_tools()
            print(tools.model_dump_json(indent=4))

            print("\nCalling Add Tool:")
            result = await session.call_tool("add", arguments={"a": 2, "b": 3})
            print(result.model_dump_json(indent=4))

            print("\n Listing Static Resources:")
            resources = await session.list_resources()
            print(resources.model_dump_json(indent=4))
            print("Reading Static Resource:")
            content = await session.read_resource("resource://static_resource")
            print(content.model_dump_json(indent=4))
            print("\n Listing Dynamic Resources:")
            resources = await session.list_resource_templates()
            print(resources.model_dump_json(indent=4))
            print("Reading Dynamic Resource:")
            content = await session.read_resource("greeting://Aria")
            print(content.model_dump_json(indent=4))

            print("\nListing Prompts:")
            prompts = await session.list_prompts()
            print(prompts.model_dump_json(indent=4))
            print("Getting a Prompt:")
            prompt = await session.get_prompt(
                name="greet_user", arguments={"name": "Aria"}
            )
            print(prompt.model_dump_json(indent=4))


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
