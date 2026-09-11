"""Script to record a complete end-to-end demo video of CyberLens 2.0 using Playwright.
"""

import os
import time
import subprocess
from playwright.sync_api import sync_playwright

def run():
    video_dir = os.path.abspath("demo_recordings")
    os.makedirs(video_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/home/mosesfdo/.local/bin/google-chrome"
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 720}
        )
        page = context.new_page()
        
        print("1. Navigating to CyberLens 2.0 at http://localhost:8501...")
        page.goto("http://localhost:8501")
        page.wait_for_timeout(3000)
        
        # Authentication
        auth_input = page.locator("input[type='password'], input[aria-label*='Key'], input[type='text']")
        if auth_input.count() > 0:
            print("2. Entering demo access key 'cyberlens-demo-2024'...")
            auth_input.first.fill("cyberlens-demo-2024")
            page.wait_for_timeout(500)
            auth_btn = page.locator("button:visible:has-text('Authenticate')")
            if auth_btn.count() > 0:
                auth_btn.first.click()
            else:
                page.keyboard.press("Enter")
            page.wait_for_timeout(3500)
            
        print("3. Executive View loaded. Showcasing baseline metrics and KPIs...")
        page.wait_for_timeout(3000)
        
        # Smooth scroll through Executive View
        for _ in range(3):
            page.mouse.wheel(0, 250)
            page.wait_for_timeout(1200)
            
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, -750)
        page.wait_for_timeout(1500)
        
        # Click UPI Switch Demo Scenario from top header
        upi_btn = page.locator("button:visible:has-text('UPI Switch Demo')")
        if upi_btn.count() > 0:
            print("4. Activating 'UPI Switch Demo Scenario'...")
            upi_btn.first.click()
            page.wait_for_timeout(3500)
            
        print("5. Inspecting updated risk metrics and scrolling to Knapsack Budget Allocator...")
        page.mouse.wheel(0, 450)
        page.wait_for_timeout(2500)
        
        # Run Knapsack Optimizer / Generate Allocation Schedule
        alloc_btn = page.locator("button:visible:has-text('Generate Allocation Schedule')")
        if alloc_btn.count() > 0:
            print("6. Executing ROSI Knapsack Optimizer (Allocation Schedule)...")
            alloc_btn.first.click()
            page.wait_for_timeout(3000)
            
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(3500)
        
        # Scroll back to top
        page.mouse.wheel(0, -1000)
        page.wait_for_timeout(1500)
        
        # Switch to Technical View
        tech_btn = page.locator("button:visible:has-text('Technical View')")
        if tech_btn.count() > 0:
            print("7. Switching to 'Technical View'...")
            tech_btn.first.click()
            page.wait_for_timeout(3500)
            
        print("8. Browsing Technical View asset ledger & vulnerability details...")
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2500)
        
        # Tab 2: RBI / SEBI / NPCI mapping
        rbi_tab = page.locator("[data-baseweb='tab']:has-text('RBI / SEBI / NPCI')")
        if rbi_tab.count() > 0:
            print("9. Viewing RBI / SEBI / NPCI Regulatory Clause Mapping...")
            rbi_tab.first.click()
            page.wait_for_timeout(2500)
            
        # Tab 3: Remediation with Hindi toggle
        remed_tab = page.locator("[data-baseweb='tab']:has-text('Remediation')")
        if remed_tab.count() > 0:
            print("10. Viewing AI Remediation Guidance (English)...")
            remed_tab.first.click()
            page.wait_for_timeout(2500)
            
            # Switch to Hindi
            hindi_opt = page.locator("label:has-text('हिंदी')")
            if hindi_opt.count() > 0:
                print("11. Toggling Hindi Language Remediation...")
                hindi_opt.first.click()
                page.wait_for_timeout(2500)
                
        # Tab 4: What-If Simulation
        whatif_tab = page.locator("[data-baseweb='tab']:has-text('What-If Simulation')")
        if whatif_tab.count() > 0:
            print("12. Testing Interactive What-If Simulation...")
            whatif_tab.first.click()
            page.wait_for_timeout(2500)
            
            checkbox = page.locator("input[type='checkbox']").first
            if checkbox.count() > 0:
                print("13. Toggling security control to simulate risk reduction...")
                checkbox.click()
                page.wait_for_timeout(3000)
                
        # Tab 5: Transaction Flow
        flow_tab = page.locator("[data-baseweb='tab']:has-text('Transaction Flow')")
        if flow_tab.count() > 0:
            print("14. Inspecting Transaction Flow Diagram...")
            flow_tab.first.click()
            page.wait_for_timeout(3000)
            
        # Scroll up and click Generate SIH Summary
        page.mouse.wheel(0, -600)
        page.wait_for_timeout(1000)
        
        sih_btn = page.locator("button:visible:has-text('Generate SIH')")
        if sih_btn.count() > 0:
            print("15. Clicking 'Generate SIH Summary' button...")
            sih_btn.first.click()
            page.wait_for_timeout(3000)
            
        print("16. Demo walkthrough complete. Finalizing recording...")
        page.wait_for_timeout(2000)
        
        # Finish recording
        video = page.video
        video_path = video.path() if video else None
        
        context.close()
        browser.close()
        
        if video_path and os.path.exists(video_path):
            print(f"Recorded video saved at: {video_path}")
            final_webm = os.path.abspath("cyberlens_demo.webm")
            final_mp4 = os.path.abspath("cyberlens_demo.mp4")
            
            subprocess.run(["cp", video_path, final_webm], check=True)
            print("Converting video to MP4 using ffmpeg...")
            subprocess.run([
                "ffmpeg", "-y", "-i", video_path,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-preset", "fast", "-crf", "22",
                final_mp4
            ], check=True)
            
            # Copy to Downloads
            downloads_mp4 = "/home/mosesfdo/Downloads/cyberlens_demo.mp4"
            downloads_webm = "/home/mosesfdo/Downloads/cyberlens_demo.webm"
            subprocess.run(["cp", final_mp4, downloads_mp4], check=True)
            subprocess.run(["cp", final_webm, downloads_webm], check=True)
            print(f"SUCCESS! MP4 video available at:\n- {final_mp4}\n- {downloads_mp4}")

if __name__ == "__main__":
    run()
