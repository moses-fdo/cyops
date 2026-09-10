import os
import unittest
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamlit_app.py")

class TestTopNavE2E(unittest.TestCase):

    def test_e2e_user_journey(self):
        at = AppTest.from_file(APP_PATH)
        at.run()
        self.assertEqual(len(at.exception), 0)

        # 1. Authenticate
        at.text_input[0].input("cyberlens-demo-2024")
        at.button[0].click()
        at.run()
        self.assertEqual(len(at.exception), 0)

        # Verify top navigation bar rendered
        self.assertEqual(at.session_state["current_view"], "Executive View")

        # 2. Switch to Technical View via top nav button
        tech_btn = [b for b in at.button if b.key == "nav_top_tech"][0]
        tech_btn.click()
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.session_state["current_view"], "Technical View")

        # 3. Switch back to Executive View via top nav button
        exec_btn = [b for b in at.button if b.key == "nav_top_exec"][0]
        exec_btn.click()
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.session_state["current_view"], "Executive View")

        # 4. Trigger Load UPI Switch Demo
        demo_btn = [b for b in at.button if b.key == "top_upi_demo"][0]
        demo_btn.click()
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertLessEqual(len(at.session_state["assets"]), 5)

        # 5. Click View Details on Top Risk
        view_details_btns = [b for b in at.button if b.key and b.key.startswith("tr_")]
        self.assertGreater(len(view_details_btns), 0)
        view_details_btns[0].click()
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.session_state["current_view"], "Technical View")

        # 6. Reset Full Portfolio
        reset_btn = [b for b in at.button if b.key == "top_reset_portfolio"][0]
        reset_btn.click()
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.session_state["assets"]), 10)

        # 7. Generate SIH Summary
        sih_btn = [b for b in at.button if b.key == "top_sih_summary"][0]
        sih_btn.click()
        at.run()
        self.assertEqual(len(at.exception), 0)

        print("E2E User Journey Test PASSED successfully!")

if __name__ == "__main__":
    unittest.main()
