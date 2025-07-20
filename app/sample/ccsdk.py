import anyio
from claude_code_sdk import ClaudeCodeOptions, Message, query
from claude_code_sdk.types import ResultMessage


async def main():
    messages: list[Message] = []

    options = ClaudeCodeOptions(
        max_turns=3,
    )

    async for message in query(
        prompt="foo.pyについての俳句を書いて",
        options=options
    ):
        messages.append(message)

    assert isinstance(messages[-1], ResultMessage)
    r = messages[-1]
    print(r.result)


if __name__ == "__main__":
    anyio.run(main)
