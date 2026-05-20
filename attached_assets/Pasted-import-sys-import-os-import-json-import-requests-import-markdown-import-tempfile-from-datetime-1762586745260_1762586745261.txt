import sys
import os
import json
import requests
import markdown
import tempfile
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QPushButton, QWidget, QLabel, 
                             QScrollArea, QFrame, QFileDialog, QMessageBox, 
                             QSplitter, QComboBox, QProgressBar, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QTextCursor, QPixmap, QIcon, QTextCharFormat, QPalette
from PyQt5.QtWebEngineWidgets import QWebEngineView


class ChatMessageWidget(QWidget):
    def __init__(self, message, is_user=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Timestamp
        time_label = QLabel(self.timestamp.strftime("%H:%M:%S"))
        time_label.setStyleSheet("color: gray; font-size: 10px;")
        time_label.setAlignment(Qt.AlignRight if self.is_user else Qt.AlignLeft)
        layout.addWidget(time_label)
        
        # Message bubble
        message_frame = QFrame()
        message_frame.setFrameStyle(QFrame.Box)
        message_frame.setLineWidth(1)
        
        if self.is_user:
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #007bff;
                    border-radius: 15px;
                    border: 1px solid #0056b3;
                    padding: 10px;
                    color: white;
                }
            """)
        else:
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 15px;
                    border: 1px solid #dee2e6;
                    padding: 10px;
                    color: #212529;
                }
            """)
        
        message_layout = QVBoxLayout(message_frame)
        
        # Use QWebEngineView to render formatted content
        self.web_view = QWebEngineView()
        self.web_view.setFixedHeight(1)  # Will be adjusted later
        self.web_view.setHtml(self.format_message(self.message))
        
        message_layout.addWidget(self.web_view)
        layout.addWidget(message_frame)
        
        self.setLayout(layout)
        
        # Adjust height after content loads
        self.web_view.loadFinished.connect(self.adjust_height)
        
    def format_message(self, message):
        # Convert markdown to HTML
        html_content = markdown.markdown(message, extensions=['fenced_code', 'tables'])
        
        # Basic styling
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: transparent;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                code {{
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    margin: 10px 0;
                    padding-left: 15px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        return html
        
    def adjust_height(self):
        # Adjust the height based on content
        self.web_view.page().runJavaScript("document.body.scrollHeight", self.set_height)
        
    def set_height(self, height):
        self.web_view.setFixedHeight(min(height + 20, 500))  # Limit max height


class ChatWorker(QThread):
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, api_key, model, message, conversation_history=None):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.message = message
        self.conversation_history = conversation_history or []
        
    def run(self):
        try:
            url = "https://api.perplexity.ai/chat/completions"
            
            # Prepare messages with conversation history
            messages = self.conversation_history.copy()
            messages.append({"role": "user", "content": self.message})
            
            payload = {
                "model": self.model,
                "messages": messages
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Simulate progress for long-running requests
            for i in range(5):
                self.progress_updated.emit(i * 20)
                self.msleep(200)
                
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    self.response_received.emit(content)
                else:
                    self.error_occurred.emit("No response content received")
            else:
                self.error_occurred.emit(f"API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.error_occurred.emit(f"Request failed: {str(e)}")


class ResponsiveTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
    def sizeHint(self):
        # Return a size hint that's appropriate for the content
        doc_height = self.document().size().height()
        return QSize(super().sizeHint().width(), min(int(doc_height) + 10, 120))


class ChatBotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = None
        self.conversation_history = []
        self.uploaded_files = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Perplexity AI Chatbot")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for settings and file management
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel for chat
        right_panel = self.create_chat_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        
        # Apply styles
        self.apply_styles()
        
    def create_left_panel(self):
        panel = QWidget()
        panel.setMinimumWidth(250)
        panel.setMaximumWidth(400)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # API Key section
        api_group = QFrame()
        api_group.setFrameStyle(QFrame.Box)
        api_layout = QVBoxLayout(api_group)
        
        api_layout.addWidget(QLabel("API Configuration"))
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Perplexity API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_key_input)
        
        self.save_api_btn = QPushButton("Save API Key")
        self.save_api_btn.clicked.connect(self.save_api_key)
        api_layout.addWidget(self.save_api_btn)
        
        layout.addWidget(api_group)
        
        # Model selection
        model_group = QFrame()
        model_group.setFrameStyle(QFrame.Box)
        model_layout = QVBoxLayout(model_group)
        
        model_layout.addWidget(QLabel("Model Selection"))
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["sonar-pro", "sonar-deep-research"])
        model_layout.addWidget(self.model_combo)
        
        layout.addWidget(model_group)
        
        # File upload section
        file_group = QFrame()
        file_group.setFrameStyle(QFrame.Box)
        file_layout = QVBoxLayout(file_group)
        
        file_layout.addWidget(QLabel("Document Management"))
        
        self.upload_btn = QPushButton("Upload Document")
        self.upload_btn.clicked.connect(self.upload_document)
        file_layout.addWidget(self.upload_btn)
        
        self.file_list_label = QLabel("Uploaded Files:")
        file_layout.addWidget(self.file_list_label)
        
        self.file_list = QTextEdit()
        self.file_list.setMaximumHeight(150)
        self.file_list.setReadOnly(True)
        file_layout.addWidget(self.file_list)
        
        layout.addWidget(file_group)
        
        # Conversation management
        conv_group = QFrame()
        conv_group.setFrameStyle(QFrame.Box)
        conv_layout = QVBoxLayout(conv_group)
        
        self.save_conv_btn = QPushButton("Save Conversation")
        self.save_conv_btn.clicked.connect(self.save_conversation)
        conv_layout.addWidget(self.save_conv_btn)
        
        self.load_conv_btn = QPushButton("Load Conversation")
        self.load_conv_btn.clicked.connect(self.load_conversation)
        conv_layout.addWidget(self.load_conv_btn)
        
        self.clear_conv_btn = QPushButton("Clear Conversation")
        self.clear_conv_btn.clicked.connect(self.clear_conversation)
        conv_layout.addWidget(self.clear_conv_btn)
        
        layout.addWidget(conv_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        return panel
        
    def create_chat_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Chat display area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_container)
        layout.addWidget(self.chat_scroll)
        
        # Input area - Now with message input and send button on same line
        input_group = QFrame()
        input_group.setFrameStyle(QFrame.Box)
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(5, 5, 5, 5)
        
        # Main input row - message input and send button side by side
        input_row_layout = QHBoxLayout()
        
        # Message input (expands to fill available space)
        self.message_input = ResponsiveTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMaximumHeight(120)  # Limit maximum height
        input_row_layout.addWidget(self.message_input)
        
        # Send button (fixed size)
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedSize(80, 60)  # Fixed size for send button
        self.send_btn.clicked.connect(self.send_message)
        input_row_layout.addWidget(self.send_btn)
        
        input_layout.addLayout(input_row_layout)
        
        # Additional buttons row
        button_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("Record Message")
        self.record_btn.clicked.connect(self.record_message)
        button_layout.addWidget(self.record_btn)
        
        # Add some stretch to push buttons to the left
        button_layout.addStretch()
        
        input_layout.addLayout(button_layout)
        
        layout.addWidget(input_group)
        
        return panel
        
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 3px;
            }
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
    def save_api_key(self):
        self.api_key = self.api_key_input.text().strip()
        if self.api_key:
            QMessageBox.information(self, "Success", "API key saved successfully!")
        else:
            QMessageBox.warning(self, "Warning", "Please enter a valid API key")
            
    def upload_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Document", "", 
            "All Files (*);;Text Files (*.txt);;PDF Files (*.pdf);;Word Documents (*.docx)"
        )
        
        if file_path:
            # Store file info
            file_name = os.path.basename(file_path)
            self.uploaded_files.append({
                'name': file_name,
                'path': file_path,
                'upload_time': datetime.now()
            })
            
            # Update file list display
            self.update_file_list()
            
            QMessageBox.information(self, "Success", f"File '{file_name}' uploaded successfully!")
            
    def update_file_list(self):
        file_text = ""
        for file in self.uploaded_files:
            file_text += f"• {file['name']} ({file['upload_time'].strftime('%H:%M:%S')})\n"
        self.file_list.setPlainText(file_text)
        
    def send_message(self):
        if not self.api_key:
            QMessageBox.warning(self, "Warning", "Please set your API key first")
            return
            
        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Warning", "Please enter a message")
            return
            
        # Add context from uploaded files if any
        if self.uploaded_files:
            file_context = "\n\nUploaded documents:\n"
            for file in self.uploaded_files:
                file_context += f"- {file['name']}\n"
            message += file_context
            
        # Add user message to chat
        self.add_message_to_chat(message, is_user=True)
        
        # Clear input
        self.message_input.clear()
        
        # Disable send button during request
        self.send_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # Start API request in separate thread
        self.chat_worker = ChatWorker(
            self.api_key, 
            self.model_combo.currentText(),
            message,
            self.conversation_history
        )
        self.chat_worker.response_received.connect(self.handle_response)
        self.chat_worker.error_occurred.connect(self.handle_error)
        self.chat_worker.progress_updated.connect(self.progress_bar.setValue)
        self.chat_worker.start()
        
    def record_message(self):
        # This would integrate with a recording system
        # For now, just show a message
        QMessageBox.information(self, "Record", "Recording functionality would be implemented here")
        
    def handle_response(self, response):
        # Add AI response to chat
        self.add_message_to_chat(response, is_user=False)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": self.get_last_user_message()})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Re-enable send button
        self.send_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def handle_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.send_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def add_message_to_chat(self, message, is_user=True):
        message_widget = ChatMessageWidget(message, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_widget)
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
        
    def scroll_to_bottom(self):
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def get_last_user_message(self):
        # Get the last user message from chat
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if isinstance(widget, ChatMessageWidget) and widget.is_user:
                return widget.message
        return ""
        
    def save_conversation(self):
        if not self.conversation_history:
            QMessageBox.warning(self, "Warning", "No conversation to save")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Conversation", f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump({
                        'conversation_history': self.conversation_history,
                        'timestamp': datetime.now().isoformat(),
                        'model': self.model_combo.currentText()
                    }, f, indent=2)
                QMessageBox.information(self, "Success", "Conversation saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save conversation: {str(e)}")
                
    def load_conversation(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Conversation", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                self.conversation_history = data.get('conversation_history', [])
                
                # Clear current chat
                self.clear_chat_display()
                
                # Reload messages
                for msg in self.conversation_history:
                    is_user = msg['role'] == 'user'
                    self.add_message_to_chat(msg['content'], is_user)
                    
                QMessageBox.information(self, "Success", "Conversation loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load conversation: {str(e)}")
                
    def clear_conversation(self):
        reply = QMessageBox.question(
            self, "Confirm Clear", 
            "Are you sure you want to clear the conversation?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.conversation_history.clear()
            self.clear_chat_display()
            
    def clear_chat_display(self):
        # Remove all message widgets
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if isinstance(widget, ChatMessageWidget):
                widget.setParent(None)
                widget.deleteLater()


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Perplexity AI Chatbot")
    app.setApplicationVersion("1.0")
    
    window = ChatBotWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()