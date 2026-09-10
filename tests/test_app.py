import os
import unittest
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "streamlit_app.py")


class TestStreamlitApp(unittest.TestCase):

    def test_full_app_flow(self):
        at = AppTest.from_file(APP_PATH)
        at.run()
        self.assertEqual(len(at.exception), 0, f"Exceptions on initial load: {at.exception}")

        # Authenticate
        self.assertGreater(len(at.text_input), 0)
        at.text_input[0].input("cyberlens-demo-2024")
        at.button[0].click()
        at.run()
        self.assertEqual(len(at.exception), 0, f"Exceptions after authentication: {at.exception}")

        # Executive View: change slider
        self.assertGreater(len(at.slider), 0)
        at.slider[0].set_value(2.0)
        at.run()
        self.assertEqual(len(at.exception), 0, f"Exceptions after slider update: {at.exception}")

        # Switch to Technical View
        self.assertGreater(len(at.sidebar.radio), 0)
        at.sidebar.radio[0].set_value("Technical View")
        at.run()
        self.assertEqual(len(at.exception), 0, f"Exceptions on Technical View: {at.exception}")

        # Sidebar button 0: Load Demo Scenario
        at.sidebar.button[0].click()
        at.run()
        self.assertEqual(len(at.exception), 0, f"Exceptions after Load Demo Scenario: {at.exception}")

        # Sidebar button 1: Reset Full Portfolio
        at.sidebar.button[1].click()
        at.run()
        self.assertEqual(len(at.exception), 0, f"Exceptions after Reset Full Portfolio: {at.exception}")

        # Sidebar button 2: Generate SIH Summary
        at.sidebar.button[2].click()
        at.run()
        self.assertEqual(len(at.exception), 0, f"Exceptions after Generate SIH Summary: {at.exception}")


if __name__ == "__main__":
    unittest.main()
