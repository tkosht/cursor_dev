import os

from langchain_core.messages import AIMessage  # , HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


if __name__ == "__main__":
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    r: AIMessage = model.invoke("Hello, world!")
    print(r.content)
