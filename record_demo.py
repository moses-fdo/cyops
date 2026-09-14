"""Script to record a complete ~5.5-minute 1080p demo video of CyberLens 2.0 using Playwright.
Strictly aligned with CyberLens_2.0_Demo_Script.md timestamp breakdowns (Sections 0 to 7).
Saves output as demoSIH.mp4.
"""

import os
import time
import subprocess
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

def run():
    video_dir = os.path.abspath("demo_recordings")
    os.makedirs(video_dir, exist_ok=True)
    
    with sync_playwright() as p:
        print("Launching Chromium browser in 1080p resolution (1920x1080)...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=video_dir,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        # =====================================================================
        # Section 0 & 1: On-Screen Title Card & The Problem (0:00 - 0:45) ~ 45s
        # =====================================================================
        print("Section 0 & 1 (0:00 - 0:45): Title Card & Problem Statement...")
        page.goto("http://localhost:8501")
        page.wait_for_timeout(10000)
        
        # Click Access CyberLens Platform 2.0 Button
        access_btn = page.locator("button:visible:has-text('Access CyberLens Platform')").first
        if access_btn.count() > 0:
            print("Accessing platform landing page...")
            access_btn.click()
            page.wait_for_timeout(10000)
            
        print("Showcasing baseline portfolio financial exposure (Expected Annual Loss in INR Rupees)...")
        page.wait_for_timeout(25000)  # Total ~45s
        
        # =====================================================================
        # Section 2 & 3: The Novelty & Architecture Overview (0:45 - 2:30) ~ 1m 45s (105s)
        # =====================================================================
        print("Section 2 & 3 (0:45 - 2:30): 4 Pillars, Architecture & Supervisory Audit Console...")
        # Smooth scroll through Executive View telemetry
        for _ in range(4):
            page.mouse.wheel(0, 180)
            page.wait_for_timeout(5000)
            
        # Open Supervisory Audit Console
        expander_hdr = page.locator("summary:has-text('Supervisory Audit')").first
        if expander_hdr.count() > 0:
            print("Expanding Supervisory Audit & Breach Simulation Console...")
            expander_hdr.click()
            page.wait_for_timeout(8000)
            
            # Click Compliance Audit Package
            audit_btn = page.locator("button:visible:has-text('Generate Compliance Audit Package')").first
            if audit_btn.count() > 0:
                print("Generating Regulatory Compliance Audit Package (RBI / SEBI / NPCI)...")
                audit_btn.click()
                page.wait_for_timeout(20000)
                
            # Click Breach Simulation
            breach_btn = page.locator("button:visible:has-text('Run Before/After Breach Simulation')").first
            if breach_btn.count() > 0:
                print("Executing Systemic Breach Simulation on Payment Infrastructure...")
                breach_btn.click()
                page.wait_for_timeout(25000)
                
            expander_hdr.click()
            page.wait_for_timeout(6000)
            
        page.mouse.wheel(0, -720)
        page.wait_for_timeout(26000)  # Total ~105s
        
        # =====================================================================
        # Section 4: Live Demo - Executive View & ROSI Knapsack Optimizer (2:30 - 3:45) ~ 1m 15s (75s)
        # =====================================================================
        print("Section 4 (2:30 - 3:45): Live Demo Executive View & ROSI Optimizer...")
        upi_btn = page.locator("button:visible:has-text('UPI Demo'), button:visible:has-text('UPI Switch Demo')").first
        if upi_btn.count() > 0:
            print("Activating UPI Switch Demo Scenario...")
            upi_btn.click()
            page.wait_for_timeout(15000)
            
        print("Inspecting updated UPI Risk Exposure & CR-I score...")
        page.wait_for_timeout(15000)
        
        print("Scrolling down to ROSI Knapsack Budget Optimizer...")
        page.mouse.wheel(0, 550)
        page.wait_for_timeout(10000)
        
        alloc_btn = page.locator("button:visible:has-text('Generate Allocation Schedule'), button:visible:has-text('Show Optimal')").first
        if alloc_btn.count() > 0:
            print("Executing ROSI Knapsack Optimizer for 1 Crore INR security budget...")
            alloc_btn.click()
            page.wait_for_timeout(20000)
            
        page.mouse.wheel(0, 350)
        page.wait_for_timeout(15000)
        
        page.mouse.wheel(0, -900)
        page.wait_for_timeout(0)  # Total ~75s
        
        # =====================================================================
        # Section 5: Live Demo - Technical View & AI Remediation (3:45 - 4:45) ~ 1m (60s)
        # =====================================================================
        print("Section 5 (3:45 - 4:45): Live Demo Technical View...")
        tech_btn = page.locator("button:visible:has-text('Technical View')").first
        if tech_btn.count() > 0:
            print("Switching to Technical View for security analysts...")
            tech_btn.click()
            page.wait_for_timeout(12000)
            
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(10000)
        
        # Tab 2: Regulatory Mapping
        rbi_tab = page.locator("[data-baseweb='tab']:has-text('RBI / SEBI / NPCI'), [data-baseweb='tab']:has-text('Regulatory')").first
        if rbi_tab.count() > 0:
            print("Inspecting RBI / SEBI / NPCI Regulatory Clause Mapping...")
            rbi_tab.click()
            page.wait_for_timeout(10000)
            
        # Tab 3: Remediation Guidance (English & Hindi)
        remed_tab = page.locator("[data-baseweb='tab']:has-text('Remediation')").first
        if remed_tab.count() > 0:
            print("Viewing Remediation Guidance (English)...")
            remed_tab.click()
            page.wait_for_timeout(8000)
            
            hindi_opt = page.locator("label:has-text('Hindi'), label:has-text('hindi')").or_(page.locator("label").filter(has_text="हिंदी")).first
            if hindi_opt.count() > 0:
                print("Toggling Plain Hindi Remediation for branch staff...")
                hindi_opt.click()
                page.wait_for_timeout(10000)
                
        # Tab 4: What-If Simulation
        whatif_tab = page.locator("[data-baseweb='tab']:has-text('What-If Simulation'), [data-baseweb='tab']:has-text('What-If')").first
        if whatif_tab.count() > 0:
            print("Testing Interactive What-If Simulation...")
            whatif_tab.click()
            page.wait_for_timeout(5000)
            
            checkbox = page.locator("input[type='checkbox']").first
            if checkbox.count() > 0:
                print("Toggling control on/off to recalculate CR-I and EAL in real time...")
                checkbox.click()
                page.wait_for_timeout(5000)
                
        page.mouse.wheel(0, -400)
        page.wait_for_timeout(0)  # Total ~60s
        
        # =====================================================================
        # Section 6: SIH-Specific Feature (4:45 - 5:10) ~ 25s
        # =====================================================================
        print("Section 6 (4:45 - 5:10): SIH Summary Export...")
        sih_btn = page.locator("button:visible:has-text('SIH Export'), button:visible:has-text('Generate SIH')").first
        if sih_btn.count() > 0:
            print("Clicking 'Generate SIH Summary' button...")
            sih_btn.click()
            page.wait_for_timeout(25000)  # Total ~25s
            
        # =====================================================================
        # Section 7: Closing & Future Scope (5:10 - 5:45) ~ 35s
        # =====================================================================
        print("Section 7 (5:10 - 5:45): Closing & Future Scope...")
        exec_nav = page.locator("button:visible:has-text('Executive View')").first
        if exec_nav.count() > 0:
            exec_nav.click()
            page.wait_for_timeout(10000)
            
        page.mouse.wheel(0, -600)
        page.wait_for_timeout(25000)  # Total ~35s
        
        print("Demo walkthrough complete. Finalizing ~5-6 minute 1080p recording...")
        video = page.video
        video_path = video.path() if video else None
        
        context.close()
        browser.close()
        
        import shutil
        if video_path and os.path.exists(video_path):
            print(f"Recorded video file saved at: {video_path}")
            final_webm = os.path.abspath("demoSIH.webm")
            final_mp4 = os.path.abspath("demoSIH.mp4")
            
            shutil.copy(video_path, final_webm)
            print(f"Saved 1080p WebM video to: {final_webm}")
            
            try:
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                print(f"Converting 1080p video to {final_mp4} using {ffmpeg_exe}...")
                subprocess.run([
                    ffmpeg_exe, "-y", "-i", video_path,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "fast", "-crf", "20",
                    final_mp4
                ], check=True)
                print(f"SUCCESS! 1080p MP4 video available at: {final_mp4}")
            except Exception as e:
                print(f"ffmpeg conversion error: {e}")

if __name__ == "__main__":
    run()
