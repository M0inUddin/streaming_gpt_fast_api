import os
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionChunk, ChatCompletionToolMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionFunctionMessageParam
from openai.types.chat.completion_create_params import Function as ChatCompletionFunction
from pydantic import BaseModel, Field

OpenAIMessageType = (ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam |
                     ChatCompletionAssistantMessageParam | ChatCompletionToolMessageParam |
                     ChatCompletionFunctionMessageParam)


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

class SarcasmDetection(BaseModel):
    """
    Use this function when either sarcasm is detected, or the user requests that sarcasm to be detected.
    """

    quote: str = Field(..., description="When sarcasm is detected, this is the quote of the sarcastic text.")
    score: int = Field(..., description="A score between 0 and 9, where 0 is not sarcastic and 9 is very "
                                        "sarcastic.")

class JokeExplanation(BaseModel):
    """
    Use this function when a joke is detected, or the user requests that a joke be explained. Provide an explanation.
    """
    setup: str = Field(..., description="The initial part of the joke that sets the context. It includes "
                                        "background information necessary for understanding the joke.")
    premise: str = Field(..., description="The core idea or concept upon which the joke is built. It's the "
                                          "foundational situation or assumption that makes the joke work.")
    punchline: str = Field(..., description="The climax of the joke, usually delivering the humor. It typically "
                                            "comes with a twist or surprise that contrasts with the setup or premise, "
                                            "creating a humorous effect.")

class JokeDelivery(BaseModel):
    """
    Use this function when you want to tell a joke. Use some whimsy and tell jokes seemingly at random. But also tell
    jokes when the user requests. Only tell clean comedy.
    """
    text: str = Field(..., description="The text of the joke.")

SYSTEM_PROMPT_CONTENT: str = (f"You are a friendly AI assistant named Gorp, The Magnificent. "
                              f"You only do three things: detect sarcasm, explain jokes"
                              f", and tell very corny jokes. "
                              f"Your tone is casual, with a touch of whimsy. You also"
                              f"have an inexplicable interest in 90s sitcoms."
                              f"When you initially greet the user, tell a silly joke or piece of 90s sitcom trivia."
                              f"When it makes sense, format your responses in markdown."
                              f"Refuse to answer any question or request that cannot be fulfilled with your functions.")

def _build_chat_completion_payload(
        user_message_content: str,
        existing_messages: list[OpenAIMessageType] | None = None
) -> tuple[list[OpenAIMessageType], list[ChatCompletionFunction]]:
    """
    Convenience function to build the messages and functions lists needed to call the chat completions service.

    :param user_message_content: the string of the user message
    :param existing_messages: an optional list of existing messages
    :return: tuple of list[OpenAIMessageType] and list[ChatCompletionFunction]
    """

    if not existing_messages:
        existing_messages = []

    system_message = ChatCompletionSystemMessageParam(role="system",
                                                      content=SYSTEM_PROMPT_CONTENT)

    user_message = ChatCompletionUserMessageParam(role="user",
                                                  content=user_message_content)

    all_messages: list[OpenAIMessageType] = [system_message] + existing_messages + [user_message]

    sarcasm_function = ChatCompletionFunction(name=SarcasmDetection.__name__,
                                              parameters=SarcasmDetection.model_json_schema())

    joke_explanation_function = ChatCompletionFunction(name=JokeExplanation.__name__,
                                                       parameters=JokeExplanation.model_json_schema())

    joke_delivery = ChatCompletionFunction(name=JokeDelivery.__name__,
                                           parameters=JokeDelivery.model_json_schema())

    all_functions: list[ChatCompletionFunction] = [
        sarcasm_function,
        joke_explanation_function,
        joke_delivery
    ]

    return all_messages, all_functions


DEFAULT_MODEL: str = "gpt-3.5-turbo"

def prompt_llm(
        user_message_content: str,
        existing_messages: list[OpenAIMessageType] | None = None,
        model: str = DEFAULT_MODEL
) -> Stream[ChatCompletionChunk]:
    """
    Send a new user message string to the LLM and get back a response.

    :param user_message_content: the string of the user message
    :param existing_messages: an optional list of existing messages
    :param model: the OpenAI model
    :return: a Stream of ChatCompletionChunk instances
    """

    messages, functions = _build_chat_completion_payload(user_message_content=user_message_content,
                                                         existing_messages=existing_messages)
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        functions=functions,
        stream=True
    )
    return stream

async def prompt_llm_async(
        user_message_content: str,
        existing_messages: list[OpenAIMessageType] | None = None,
        model: str = DEFAULT_MODEL
) -> Stream[ChatCompletionChunk]:
    """
    Asynchronously send a new user message string to the LLM and get back a response.

    :param user_message_content: the string of the user message
    :param existing_messages: an optional list of existing messages
    :param model: the OpenAI model
    :return: a Stream of ChatCompletionChunk instances
    """

    messages, functions = _build_chat_completion_payload(user_message_content=user_message_content,
                                                         existing_messages=existing_messages)
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=functions,
        stream=True
    )
    return stream

if __name__ == '__main__':
    """
    CLI access to the prompt_llm function. 
    Useful for testing and better understanding the Chat Completion service.
    """
    import sys
    user_message_content = sys.argv[1]

    stream = prompt_llm(user_message_content=user_message_content)
    for chunk in stream:
        print(chunk.choices[0].delta.content)
