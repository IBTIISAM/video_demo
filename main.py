import gradio as gr
import logging
from logger import setup_logger
from message_history import MessageHistory
from upload import handle_file_upload
from inference import MODELS, direct_function, battle_function_async

logger = setup_logger()

with gr.Blocks() as demo:
    with gr.Tabs():
        # Direct Tab
        with gr.Tab("Direct"):
            direct_history = MessageHistory(name="direct")
            gr.Markdown("# Direct Tab")
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    choices=MODELS, value=MODELS[0], label="Select Model"
                )
                file_upload_direct = gr.File(label="Upload File (Optional)")

            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(label="Message", placeholder="Type your message here...")
            clear = gr.Button("Clear")

            async def user_message(message, chatbot_history, model):
                logger.info(f"Processing user message for model {model}")
                chatbot_history = chatbot_history + [(message, "")]
                async for response in direct_function(message, model, direct_history):
                    chatbot_history[-1] = (message, response)
                    yield "", chatbot_history
                direct_history.add_message(message, response)

            file_upload_direct.upload(
                lambda file: handle_file_upload(file, direct_history),
                inputs=[file_upload_direct],
            )
            file_upload_direct.clear(
                lambda: handle_file_upload(None, direct_history), None
            )

            msg.submit(
                user_message,
                inputs=[msg, chatbot, model_dropdown],
                outputs=[msg, chatbot],
            )

            def clear_direct():
                logger.info("Clearing direct tab")
                direct_history.clear()
                return [], None

            clear.click(clear_direct, None, [chatbot, file_upload_direct], queue=False)
            model_dropdown.change(
                clear_direct, None, [chatbot, file_upload_direct], queue=False
            )

        # Battle Tab
        with gr.Tab("Battle"):
            battle_history1 = MessageHistory(name="battle1")
            battle_history2 = MessageHistory(name="battle2")
            gr.Markdown("# Battle Tab")

            file_upload_battle = gr.File(label="Upload File (Optional)")

            with gr.Row():
                with gr.Column():
                    model1_dropdown = gr.Dropdown(
                        choices=MODELS, value=MODELS[0], label="Model 1"
                    )
                    chatbot1 = gr.Chatbot(height=400, label="Model 1 Chat")
                with gr.Column():
                    model2_dropdown = gr.Dropdown(
                        choices=MODELS, value=MODELS[1], label="Model 2"
                    )
                    chatbot2 = gr.Chatbot(height=400, label="Model 2 Chat")

            msg_battle = gr.Textbox(
                label="Message", placeholder="Type your message here..."
            )
            clear_battle = gr.Button("Clear")

            async def battle_message(
                message, chatbot1_history, chatbot2_history, model1, model2
            ):
                logger.info(
                    f"Processing battle message for models {model1} and {model2}"
                )
                chatbot1_history = chatbot1_history + [(message, "")]
                chatbot2_history = chatbot2_history + [(message, "")]
                async for response1, response2 in battle_function_async(
                    message, model1, model2, battle_history1, battle_history2
                ):
                    chatbot1_history[-1] = (message, response1)
                    chatbot2_history[-1] = (message, response2)
                    yield "", chatbot1_history, chatbot2_history
                battle_history1.add_message(message, response1)
                battle_history2.add_message(message, response2)

            file_upload_battle.upload(
                lambda file: handle_file_upload(file, battle_history1, battle_history2),
                inputs=[file_upload_battle],
            )
            file_upload_battle.clear(
                lambda: handle_file_upload(None, battle_history1, battle_history2), None
            )

            msg_battle.submit(
                battle_message,
                inputs=[
                    msg_battle,
                    chatbot1,
                    chatbot2,
                    model1_dropdown,
                    model2_dropdown,
                ],
                outputs=[msg_battle, chatbot1, chatbot2],
            )

            def clear_battle_history():
                logger.info("Clearing battle tab")
                battle_history1.clear()
                battle_history2.clear()
                return [], [], None

            clear_battle.click(
                clear_battle_history,
                None,
                [chatbot1, chatbot2, file_upload_battle],
                queue=False,
            )

            model1_dropdown.change(
                clear_battle_history,
                None,
                [chatbot1, chatbot2, file_upload_battle],
                queue=False,
            )

            model2_dropdown.change(
                clear_battle_history,
                None,
                [chatbot1, chatbot2, file_upload_battle],
                queue=False,
            )

if __name__ == "__main__":
    logger.info("Starting ALLaM Chat application")
    demo.launch(share=True)
