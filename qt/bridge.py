# qt/bridge.py
from PySide6.QtCore import QObject, Signal, Slot
import json

class Bridge(QObject):
    """Qt WebChannel 通信桥梁（当前保留，后续扩展）"""
    message_sent = Signal(str)
    
    @Slot()
    def ping(self):
        print("Ping received from JavaScript!")
        self.message_sent.emit("Pong from Python!")
    
    @Slot(str)
    def render_mermaid(self, code: str):
        print(f"Received mermaid code: {code[:50]}...")
        self.message_sent.emit(json.dumps({'type': 'mermaid', 'code': code}))