import asyncio
import aiohttp
import json
import logging
from config import config

MODEL_ENDPOINTS = config["model_endpoints"]
MODELS = list(MODEL_ENDPOINTS.keys())


async def stream_inference_request(message, model, session, history):
    logger = logging.getLogger("ALLaM-Chat")
    logger.info(f"Starting inference request for {history.name} using model {model}")
    messages = history.get_messages()

    model_type = MODEL_ENDPOINTS[model]["type"]
    user_content = []

    if model_type == "image" and history.current_image_url:
        image_url = f"{config['image_base_url']}{history.current_image_url}"
        user_content.append({"type": "image_url", "image_url": {"url": image_url}})
        logger.debug(f"[{history.name}] Added image URL to request for image model")

    user_content.append({"type": "text", "text": message})

    final_message = {
        "role": "user",
        "content": user_content if model_type == "image" else message,
    }
    messages.append(final_message)

    payload = {
        "model": "allam",
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.95,
        "stream": True,
    }
    logger.info(payload)
    logger.debug(f"[{history.name}] Sending request to {MODEL_ENDPOINTS[model]['url']}")
    url = MODEL_ENDPOINTS[model]["url"]

    try:
        async with session.post(url, json=payload) as response:
            accumulated_text = ""
            async for line in response.content:
                if line:
                    line_text = line.decode("utf-8").strip()
                    if line_text.startswith("data: "):
                        try:
                            json_line = json.loads(line_text[6:])
                            if "choices" in json_line and json_line["choices"]:
                                delta = json_line["choices"][0].get("delta", {})
                                if "content" in delta:
                                    accumulated_text += delta["content"]
                                    yield accumulated_text
                        except json.JSONDecodeError:
                            logger.warning(
                                f"[{history.name}] Failed to decode JSON line"
                            )
                            continue
    except Exception as e:
        error_msg = f"Error during inference: {str(e)}"
        logger.error(error_msg, exc_info=True)
        yield error_msg


async def direct_function(message, model, history):
    logger = logging.getLogger("ALLaM-Chat")
    logger.info(f"Direct function called for {history.name}")
    async with aiohttp.ClientSession() as session:
        async for response in stream_inference_request(
            message, model, session, history
        ):
            yield response


async def battle_function_async(message, model1, model2, history1, history2):
    logger = logging.getLogger("ALLaM-Chat")
    logger.info("Battle function called")
    async with aiohttp.ClientSession() as session:
        stream1 = stream_inference_request(message, model1, session, history1)
        stream2 = stream_inference_request(message, model2, session, history2)
        response1, response2 = "", ""

        while True:
            done1, done2 = True, True
            try:
                response1 = await anext(stream1)
                done1 = False
            except StopAsyncIteration:
                pass

            try:
                response2 = await anext(stream2)
                done2 = False
            except StopAsyncIteration:
                pass

            if not done1 or not done2:
                yield response1, response2
            else:
                break
