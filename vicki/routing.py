from channels.routing import route, include
from vicki.consumers import ws_message, ws_connect, ws_disconnect

ws_routing = [
    route("websocket.receive", ws_message),
    route("websocket.connect", ws_connect),
    # route("websocket.disconnect", ws_disconnect),
]

channel_routing = [
    include(ws_routing, path=r"^/chat"),
]
