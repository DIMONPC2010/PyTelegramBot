import openai
import enum
import os


openai.api_key = os.getenv('OPENAI_API_KEY')
message_pool = {}
chat_message_pool = {}
tmp_len = 0

class QuestionType(enum.Enum):
    private_session = 0
    public_session = 1


def chat_gpt_request(message, session_id, session_type):
    messages = {}
    if session_type == QuestionType.private_session:
        messages = message_pool
    else:
        messages = chat_message_pool

    if message:
        message_body = messages.get(session_id, [{"role": "system", "content": "You are a intelligent assistant."}])
        message_body.append({"role": "user", "content": message})
        messages.update({session_id : message_body})

        try:
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages[session_id]
            )
        except openai.error.InvalidRequestError:
            token_counter = 0
            print("openai.error.InvalidRequestError")
            while token_counter < 1000:
                if len(messages[session_id]) > 1:
                    token_counter += len(messages[session_id][1].get("content"))
                    messages[session_id].pop(1)
                else:
                    break
            try:
                chat = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=messages[session_id]
                )
            except openai.error.RateLimitError:
                return "Rate limit reached for default-gpt-3.5-turbo on requests per min. Limit: 3 / min. Please try again in 20s."
        except openai.error.RateLimitError:
            return "Rate limit reached for default-gpt-3.5-turbo on requests per min. Limit: 3 / min. Please try again in 20s."

    reply = chat.choices[0].message.content
    message_body.append({"role": "assistant", "content": reply})
    messages.update({session_id : message_body})

    if session_type == QuestionType.private_session:
        if len(message_pool[session_id]) > 1000:
            del message_pool[session_id]
    else:
        if len(chat_message_pool[session_id]) > 1000:
            del chat_message_pool[session_id]

    return reply

def reset_private_message_cach(session_id):
    tmp_value = message_pool.get(session_id)
    if tmp_value:
        del message_pool[session_id]

def reset_public_message_cach(session_id):
    tmp_value = chat_message_pool.get(session_id)
    if tmp_value:
        del chat_message_pool[session_id]