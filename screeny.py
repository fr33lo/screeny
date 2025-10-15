#!/usr/bin/env python3
"""
Screeny - High-quality full-page screenshot capture tool
Author: AI Assistant
"""

import asyncio
import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright, Browser, Page
except ImportError:
    print("❌ Playwright not installed. Run: pip install playwright")
    print("   Then run: playwright install")
    sys.exit(1)


class ScreenshotConfig:
    """Configuration class for screenshot settings"""
    
    def __init__(self):
        self.viewport_width = 1920
        self.viewport_height = 1080
        self.device_scale_factor = 2.0
        self.full_page = True
        self.wait_timeout = 30000
        self.wait_for_selector = None
        self.wait_for_load_state = "networkidle"
        self.disable_animations = True
        self.block_ads = True
        self.output_format = "png"
        self.output_quality = None  # PNG uses lossless compression
        self.mobile = False
        self.user_agent = None
        

class Screeny:
    """High-quality screenshot capture class"""
    
    def __init__(self, config: ScreenshotConfig):
        self.config = config
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().__aenter__()
        
        # Launch browser with optimal settings for screenshots
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--hide-scrollbars',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--mute-audio',
            ]
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        await self.playwright.__aexit__(exc_type, exc_val, exc_tb)
        
    async def capture_screenshot(self, url: str, output_path: str) -> bool:
        """
        Capture a full-page screenshot of the given URL
        
        Args:
            url: The URL to capture
            output_path: Where to save the screenshot
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create new page with optimal settings
            page = await self.browser.new_page(
                viewport={
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                },
                device_scale_factor=self.config.device_scale_factor,
                user_agent=self.config.user_agent,
                is_mobile=self.config.mobile
            )
            
            # Block ads and tracking if enabled
            if self.config.block_ads:
                await page.route("**/*", self._block_ads_handler)
            
            # Disable animations for consistent screenshots
            if self.config.disable_animations:
                await page.add_init_script("""
                    // Disable CSS animations and transitions
                    const style = document.createElement('style');
                    style.innerHTML = `
                        *, *::before, *::after {
                            animation-duration: 0.01ms !important;
                            animation-delay: -0.01ms !important;
                            animation-iteration-count: 1 !important;
                            background-attachment: initial !important;
                            scroll-behavior: auto !important;
                            transition-duration: 0ms !important;
                            transition-delay: 0ms !important;
                        }
                    `;
                    document.head.appendChild(style);
                """)
            
            print(f"🌐 Loading {url}...")
            
            # Navigate to URL with timeout
            await page.goto(
                url, 
                wait_until=self.config.wait_for_load_state,
                timeout=self.config.wait_timeout
            )
            
            # Wait for specific selector if provided
            if self.config.wait_for_selector:
                await page.wait_for_selector(
                    self.config.wait_for_selector,
                    timeout=self.config.wait_timeout
                )
            
            # Additional wait for lazy-loaded content
            await page.wait_for_timeout(2000)
            
            # Scroll to bottom to trigger lazy loading
            await page.evaluate("""
                const scrollStep = () => {
                    window.scrollBy(0, window.innerHeight);
                    if (window.scrollY + window.innerHeight < document.body.scrollHeight) {
                        setTimeout(scrollStep, 100);
                    }
                };
                scrollStep();
            """)
            
            # Wait for images and fonts to load
            await page.wait_for_load_state("networkidle")
            
            # Scroll back to top
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(500)
            
            print(f"📸 Capturing screenshot...")
            
            # Take screenshot with optimal settings
            screenshot_options = {
                "path": output_path,
                "full_page": self.config.full_page,
                "type": self.config.output_format,
                "omit_background": False,
            }
            
            if self.config.output_format == "jpeg" and self.config.output_quality:
                screenshot_options["quality"] = self.config.output_quality
                
            await page.screenshot(**screenshot_options)
            
            await page.close()
            
            # Get file size for reporting
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Screenshot saved: {output_path} ({file_size:.1f} MB)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error capturing {url}: {str(e)}")
            return False
    
    async def _block_ads_handler(self, route):
        """Block ads, trackers, and unnecessary resources"""
        request = route.request
        resource_type = request.resource_type
        
        # Block ads, tracking, and analytics
        blocked_domains = [
            'googletagmanager.com', 'google-analytics.com', 'doubleclick.net',
            'googlesyndication.com', 'facebook.com/tr', 'hotjar.com',
            'crazyegg.com', 'mouseflow.com', 'clarity.ms'
        ]
        
        if any(domain in request.url for domain in blocked_domains):
            await route.abort()
            return
            
        # Allow essential resources
        if resource_type in ["document", "stylesheet", "image", "font"]:
            await route.continue_()
        else:
            # Block other resource types like scripts from ad networks
            if any(domain in request.url for domain in blocked_domains):
                await route.abort()
            else:
                await route.continue_()
    
    async def batch_capture(self, urls: List[str], output_dir: str, 
                          name_template: str = "{domain}_{timestamp}") -> Dict[str, bool]:
        """
        Capture screenshots for multiple URLs
        
        Args:
            urls: List of URLs to capture
            output_dir: Directory to save screenshots
            name_template: Template for output filenames
            
        Returns:
            Dict mapping URLs to success status
        """
        results = {}
        os.makedirs(output_dir, exist_ok=True)
        
        for i, url in enumerate(urls, 1):
            print(f"\n📊 Processing {i}/{len(urls)}: {url}")
            
            # Generate filename
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '').replace('.', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = name_template.format(
                domain=domain,
                timestamp=timestamp,
                index=i
            )
            
            if not filename.endswith(f'.{self.config.output_format}'):
                filename += f'.{self.config.output_format}'
            
            output_path = os.path.join(output_dir, filename)
            
            # Capture screenshot
            success = await self.capture_screenshot(url, output_path)
            results[url] = success
            
            # Small delay between captures
            if i < len(urls):
                await asyncio.sleep(1)
        
        return results


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a text or CSV file"""
    urls = []
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.suffix.lower() == '.csv':
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():  # Skip empty rows
                    url = row[0].strip()
                    if url.startswith(('http://', 'https://')):
                        urls.append(url)
        else:
            # Treat as text file
            for line in f:
                url = line.strip()
                if url and url.startswith(('http://', 'https://')):
                    urls.append(url)
    
    return urls


async def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(
        description="Screeny - High-quality full-page screenshot capture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  screeny.py -u https://example.com
  screeny.py -f urls.txt -o screenshots/
  screeny.py -u https://example.com --mobile --width 375 --height 812
  screeny.py -u https://example.com --scale 3.0 --wait-selector ".main-content"
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-u', '--url', help='Single URL to capture')
    input_group.add_argument('-f', '--file', help='File containing URLs (txt or csv)')
    
    # Output options
    parser.add_argument('-o', '--output', default='./screenshots', 
                       help='Output directory (default: ./screenshots)')
    parser.add_argument('--format', choices=['png', 'jpeg'], default='png',
                       help='Output format (default: png)')
    parser.add_argument('--quality', type=int, default=90,
                       help='JPEG quality 1-100 (default: 90)')
    
    # Viewport options
    parser.add_argument('--width', type=int, default=1920,
                       help='Viewport width (default: 1920)')
    parser.add_argument('--height', type=int, default=1080,
                       help='Viewport height (default: 1080)')
    parser.add_argument('--scale', type=float, default=2.0,
                       help='Device pixel ratio (default: 2.0)')
    parser.add_argument('--mobile', action='store_true',
                       help='Use mobile viewport')
    
    # Wait options
    parser.add_argument('--wait-timeout', type=int, default=30000,
                       help='Wait timeout in ms (default: 30000)')
    parser.add_argument('--wait-selector', 
                       help='Wait for CSS selector before screenshot')
    parser.add_argument('--wait-state', 
                       choices=['load', 'domcontentloaded', 'networkidle'],
                       default='networkidle',
                       help='Wait for load state (default: networkidle)')
    
    # Quality options
    parser.add_argument('--no-animations', action='store_true', default=True,
                       help='Disable animations (default: True)')
    parser.add_argument('--no-ads', action='store_true', default=True,
                       help='Block ads and trackers (default: True)')
    
    args = parser.parse_args()
    
    # Create configuration
    config = ScreenshotConfig()
    config.viewport_width = args.width
    config.viewport_height = args.height
    config.device_scale_factor = args.scale
    config.mobile = args.mobile
    config.wait_timeout = args.wait_timeout
    config.wait_for_selector = args.wait_selector
    config.wait_for_load_state = args.wait_state
    config.disable_animations = args.no_animations
    config.block_ads = args.no_ads
    config.output_format = args.format
    if args.format == 'jpeg':
        config.output_quality = args.quality
    
    # Load URLs
    if args.url:
        urls = [args.url]
    else:
        try:
            urls = load_urls_from_file(args.file)
            print(f"📄 Loaded {len(urls)} URLs from {args.file}")
        except Exception as e:
            print(f"❌ Error loading URLs: {e}")
            return 1
    
    if not urls:
        print("❌ No valid URLs found")
        return 1
    
    # Capture screenshots
    start_time = time.time()
    
    async with Screeny(config) as screeny:
        if len(urls) == 1:
            # Single URL
            url = urls[0]
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '').replace('.', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"{domain}_{timestamp}.{config.output_format}"
            output_path = os.path.join(args.output, filename)
            
            os.makedirs(args.output, exist_ok=True)
            success = await screeny.capture_screenshot(url, output_path)
            
            if success:
                print(f"\n✅ Screenshot completed successfully!")
            else:
                print(f"\n❌ Screenshot failed!")
                return 1
        else:
            # Batch processing
            results = await screeny.batch_capture(urls, args.output)
            
            successful = sum(results.values())
            total = len(results)
            
            print(f"\n📊 Batch Results:")
            print(f"   ✅ Successful: {successful}/{total}")
            print(f"   ❌ Failed: {total - successful}/{total}")
            
            if successful < total:
                print(f"\n❌ Failed URLs:")
                for url, success in results.items():
                    if not success:
                        print(f"   • {url}")
    
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed_time:.1f} seconds")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))