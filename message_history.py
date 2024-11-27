import logging


class MessageHistory:
    def __init__(self, max_turns=5, name="default"):
        self.history = []
        self.max_turns = max_turns
        self.current_image_url = None
        self.name = name
        self.logger = logging.getLogger("ALLaM-Chat")
        self.logger.info(f"Initialized MessageHistory for {name}")

    def add_message(self, user_msg, assistant_msg):
        if len(self.history) >= self.max_turns * 2:
            self.history = self.history[2:]
            self.logger.debug(f"[{self.name}] Trimmed history to maintain max turns")
        if not self.history:
            self.history = [{"role": "user", "content": user_msg}]
        else:
            self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        self.logger.debug(f"[{self.name}] Added new message pair to history")

    def get_messages(self):
        return self.history.copy()

    def set_image_url(self, url):
        self.current_image_url = url
        self.logger.info(f"[{self.name}] Set image URL: {url}")

    def clear(self):
        self.history = []
        self.current_image_url = None
        self.logger.info(f"[{self.name}] Cleared history and image URL")
