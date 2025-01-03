from poe_bot_but_better import poe_bot_but_better

IMAGE_URL = (
    "https://images.pexels.com/photos/46254/leopard-wildcat-big-cat-botswana-46254.jpeg"
)

@poe_bot_but_better
class SampleImageResponseBot:
    def get_response(self):
        return "This is a test image. ![leopard]({IMAGE_URL})"