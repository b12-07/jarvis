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

        cpu, ram = self.actions.get_system_metrics()
        assert cpu == 45.0
        assert ram == 60.0

    @patch('subprocess.Popen')
    def test_launch_app_mac_linux(self, mock_popen):
        # Override OS to test logic branch
        self.actions.os_name = "darwin"
        result = self.actions.launch_app("testapp")
        assert result is True
        mock_popen.assert_called_with(["open", "-a", "test_executable"])

class TestJarvisBrain:
    def setup_method(self):
        self.brain = JarvisBrain()
        # Mock the chat session to avoid actual API calls
        self.brain.chat = MagicMock()

    @patch('actions.system.SystemActions.get_system_metrics')
    def test_process_input_system_stats(self, mock_metrics):
        mock_metrics.return_value = (30.0, 50.0)
        response = self.brain.process_input("What are my system stats?")
        assert "30.0" in response
        assert "50.0" in response

    @patch('actions.system.SystemActions.launch_app')
    def test_process_input_launch_app(self, mock_launch):
        mock_launch.return_value = True
        response = self.brain.process_input("Open chrome")
        assert "chrome" in response
        mock_launch.assert_called_with("chrome")

    @patch('actions.system.SystemActions.adjust_volume')
    def test_process_input_volume(self, mock_volume):
        mock_volume.return_value = True
        response = self.brain.process_input("Set volume to 75 percent")
        assert "75" in response
        mock_volume.assert_called_with(75)

    def test_process_input_llm_fallback(self):
        mock_response = MagicMock()
        mock_response.text = "I am processing that, sir."
        self.brain.chat.send_message.return_value = mock_response

        response = self.brain.process_input("Who is Iron Man?")
        assert response == "I am processing that, sir."
        self.brain.chat.send_message.assert_called_with("Who is Iron Man?")
