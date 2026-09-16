import pytest
from unittest.mock import patch, MagicMock

from actions.system import SystemActions
from brain.llm import JarvisBrain

class TestSystemActions:
    def setup_method(self):
        self.aliases = {"testapp": "test_executable"}
        self.actions = SystemActions(self.aliases)

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_get_system_metrics(self, mock_vm, mock_cpu):
        mock_cpu.return_value = 45.0
        mock_vm_instance = MagicMock()
        mock_vm_instance.percent = 60.0
        mock_vm.return_value = mock_vm_instance

        result = self.actions.get_system_metrics()
        assert "45.0" in result
        assert "60.0" in result

    @patch('subprocess.Popen')
    def test_launch_app_mac_linux(self, mock_popen):
        # Override OS to test logic branch
        self.actions.os_name = "darwin"
        result = self.actions.launch_app("testapp")
        assert "Successfully launched test_executable" in result
        mock_popen.assert_called_with(["open", "-a", "test_executable"])

class TestJarvisBrain:
    def setup_method(self):
        self.brain = JarvisBrain()
        # Mock the chat session to avoid actual API calls
        self.brain.chat = MagicMock()

    def test_process_input_llm_fallback(self):
        mock_response = MagicMock()
        mock_response.text = "I am processing that, sir."
        self.brain.chat.send_message.return_value = mock_response

        response = self.brain.process_input("Who is Iron Man?")
        assert response == "I am processing that, sir."
        self.brain.chat.send_message.assert_called_with("Who is Iron Man?")

    def test_process_input_empty_response(self):
        # When Gemini returns an empty text (due to function call completion being handled automatically)
        mock_response = MagicMock()
        mock_response.text = ""
        self.brain.chat.send_message.return_value = mock_response

        response = self.brain.process_input("Check CPU")
        assert "Araç çalıştırıldı" in response
