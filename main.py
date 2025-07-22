#!/usr/bin/env python3
"""
AI Screen Assistant - GUI application that captures screen and gets AI assistance
"""

import os
import json
import base64
import threading
import argparse
import datetime
import subprocess
import webbrowser
import requests
from io import BytesIO
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, simpledialog
from PIL import ImageTk, Image

# Import token authentication client
from token_auth import BedrockTokenClient
# Import region selector
from region_selector import RegionSelector

# Import boto3 conditionally to allow mock mode without AWS credentials
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# Parse command line arguments
parser = argparse.ArgumentParser(description='AI Screen Assistant')
parser.add_argument('--mock', action='store_true', help='Run in mock mode without AWS credentials')
args = parser.parse_args()

# Thumbnail configuration constants
THUMBNAIL_CONFIG = {
    'max_width': 200,
    'max_height': 150,
    'quality': 'high',
    'format': 'PNG'
}

class CredentialsDialog(tk.Toplevel):
    """Dialog for entering AWS credentials"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("AWS Credentials Setup")
        self.geometry("500x400")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self.access_key = tk.StringVar(value=os.environ.get('AWS_ACCESS_KEY_ID', ''))
        self.secret_key = tk.StringVar(value=os.environ.get('AWS_SECRET_ACCESS_KEY', ''))
        self.region = tk.StringVar(value=os.environ.get('AWS_REGION', 'us-east-1'))
        
        self.result = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="AWS Credentials Setup", 
            font=("Helvetica", 16)
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="To use Amazon Bedrock, you need to provide your AWS credentials.\n"
                 "You can find these in your AWS Management Console.",
            wraplength=450,
            justify=tk.LEFT
        )
        instructions.pack(fill=tk.X, pady=(0, 20))
        
        # AWS Console link
        link_frame = ttk.Frame(main_frame)
        link_frame.pack(fill=tk.X, pady=(0, 20))
        
        link_label = ttk.Label(
            link_frame,
            text="Need help finding your credentials?",
        )
        link_label.pack(side=tk.LEFT)
        
        link_button = ttk.Button(
            link_frame,
            text="Open AWS Console",
            command=self.open_aws_console
        )
        link_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Access Key
        ttk.Label(form_frame, text="AWS Access Key ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.access_key, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Secret Key
        ttk.Label(form_frame, text="AWS Secret Access Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        secret_entry = ttk.Entry(form_frame, textvariable=self.secret_key, width=40, show="*")
        secret_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Region
        ttk.Label(form_frame, text="AWS Region:").grid(row=2, column=0, sticky=tk.W, pady=5)
        regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2']
        region_combo = ttk.Combobox(form_frame, textvariable=self.region, values=regions, width=37)
        region_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Test Connection", command=self.test_connection).pack(side=tk.RIGHT, padx=5)
        
    def open_aws_console(self):
        """Open AWS Console in browser"""
        webbrowser.open("https://console.aws.amazon.com/iam/home?#/security_credentials")
        
    def test_connection(self):
        """Test AWS credentials"""
        if not self.access_key.get() or not self.secret_key.get():
            messagebox.showerror("Error", "Please enter both Access Key and Secret Key")
            return
            
        try:
            # Create a temporary session with the provided credentials
            session = boto3.Session(
                aws_access_key_id=self.access_key.get(),
                aws_secret_access_key=self.secret_key.get(),
                region_name=self.region.get()
            )
            
            # Test STS connection
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            
            # Test Bedrock access
            bedrock = session.client('bedrock-runtime')
            
            messagebox.showinfo(
                "Success", 
                f"Connection successful!\nAccount: {identity['Account']}\nUser: {identity['UserId']}"
            )
        except ClientError as e:
            messagebox.showerror("Error", f"AWS Error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
            
    def save(self):
        """Save credentials and close dialog"""
        if not self.access_key.get() or not self.secret_key.get():
            messagebox.showerror("Error", "Please enter both Access Key and Secret Key")
            return
            
        self.result = {
            'access_key': self.access_key.get(),
            'secret_key': self.secret_key.get(),
            'region': self.region.get()
        }
        self.destroy()
        
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.destroy()

class ScreenAssistantApp:
    def __init__(self, root, mock_mode=False):
        self.root = root
        self.root.title("AI Screen Assistant")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Set mock mode
        self.mock_mode = mock_mode
        
        # Initialize AWS Bedrock client if not in mock mode
        self.bedrock = None
        if not self.mock_mode and BOTO3_AVAILABLE:
            self.setup_aws_client()
        
        # Screenshot storage and thumbnail management
        self.current_screenshot = None
        
        # Set up the UI
        self.setup_ui()
        
        # Flag for tracking if analysis is in progress
        self.analyzing = False
        
        # Flag for tracking if viewer window is open
        self.viewer_window = None
    
    def setup_aws_client(self):
        """Set up AWS Bedrock client"""
        # Check for Bedrock API token first
        bearer_token = os.environ.get('AWS_BEARER_TOKEN_BEDROCK')
        if bearer_token:
            print("Using Bedrock API token for authentication")
            region = os.environ.get('AWS_REGION', 'us-east-1')
            
            # For token-based auth, we need to use a different approach
            # Store the token for later use
            self.bedrock_token = bearer_token
            self.using_bearer_token = True
            
            # Create a standard client for now
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name=region
            )
            return
            
        # Try to use existing credentials
        try:
            self.using_bearer_token = False
            region = os.environ.get('AWS_REGION', 'us-east-1')
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name=region
            )
            # Test the credentials
            boto3.client('sts').get_caller_identity()
        except (ClientError, NoCredentialsError, Exception) as e:
            print(f"AWS client error: {e}")
            # If credentials are invalid, show setup dialog
            self.show_credentials_dialog()
    
    def show_credentials_dialog(self):
        """Show credentials dialog and set up client with new credentials"""
        dialog = CredentialsDialog(self.root)
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Set environment variables
            os.environ['AWS_ACCESS_KEY_ID'] = dialog.result['access_key']
            os.environ['AWS_SECRET_ACCESS_KEY'] = dialog.result['secret_key']
            os.environ['AWS_REGION'] = dialog.result['region']
            
            # Create new client
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name=dialog.result['region']
            )
            
            # Ask if user wants to save credentials permanently
            if messagebox.askyesno(
                "Save Credentials", 
                "Do you want to save these credentials to your AWS CLI configuration?"
            ):
                self.save_aws_config(
                    dialog.result['access_key'],
                    dialog.result['secret_key'],
                    dialog.result['region']
                )
        else:
            # If user cancels, switch to mock mode
            self.mock_mode = True
            messagebox.showinfo(
                "Mock Mode", 
                "Running in mock mode. The application will simulate AI responses."
            )
    
    def save_aws_config(self, access_key, secret_key, region):
        """Save AWS credentials to config file"""
        try:
            # Use AWS CLI to save credentials
            subprocess.run([
                'aws', 'configure', 'set', 'aws_access_key_id', access_key
            ])
            subprocess.run([
                'aws', 'configure', 'set', 'aws_secret_access_key', secret_key
            ])
            subprocess.run([
                'aws', 'configure', 'set', 'region', region
            ])
            subprocess.run([
                'aws', 'configure', 'set', 'output', 'json'
            ])
            messagebox.showinfo("Success", "Credentials saved to AWS CLI configuration")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {str(e)}")
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_text = "AI Screen Assistant" + (" (MOCK MODE)" if self.mock_mode else "")
        title_label = ttk.Label(
            main_frame, 
            text=title_text, 
            font=("Helvetica", 16)
        )
        title_label.pack(pady=10)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="How to Use", padding="10")
        instructions_frame.pack(fill=tk.X, pady=(0, 10))
        
        instructions_text = (
            "📋 Before clicking 'Analyze Screen':\n\n"
            "1. Open the application, document, or webpage you need help with\n"
            "2. Make sure the content is visible and in focus\n"
            "3. Position any windows or dialogs you want the AI to see\n"
            "4. Then click the button below to capture and analyze your screen\n\n"
            "💡 The AI can help with code, documents, error messages, UI design, and more!"
        )
        
        instructions_label = ttk.Label(
            instructions_frame,
            text=instructions_text,
            wraplength=550,
            justify=tk.LEFT,
            font=("Arial", 10)
        )
        instructions_label.pack()
        
        # Analyze button
        self.analyze_button = ttk.Button(
            main_frame,
            text="Analyze Screen",
            command=self.on_analyze_clicked,
            style="Accent.TButton"
        )
        self.analyze_button.pack(pady=20)
        
        # Progress indicator
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress.pack(pady=10)
        self.progress.pack_forget()  # Hide initially
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
        
        # Thumbnail display area
        self.thumbnail_frame = ttk.LabelFrame(main_frame, text="Last Screenshot")
        self.thumbnail_frame.pack(fill=tk.X, pady=(10, 5))
        self.thumbnail_frame.pack_forget()  # Hide initially when no screenshot
        
        self.thumbnail_label = ttk.Label(
            self.thumbnail_frame,
            text="Click to view full size",
            cursor="hand2"
        )
        self.thumbnail_label.pack(pady=5)
        self.thumbnail_label.bind("<Button-1>", self.on_thumbnail_click)
        
        # Results text area
        results_frame = ttk.LabelFrame(main_frame, text="AI Suggestions")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=70,
            height=15
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_text.config(state=tk.DISABLED)
        
        # Configure style for accent button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Helvetica", 12))
        
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="AWS Credentials", command=self.show_credentials_dialog)
        settings_menu.add_command(label="Toggle Mock Mode", command=self.toggle_mock_mode)
    
    def toggle_mock_mode(self):
        """Toggle between mock mode and real mode"""
        self.mock_mode = not self.mock_mode
        
        # Update title
        title_text = "AI Screen Assistant" + (" (MOCK MODE)" if self.mock_mode else "")
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and child.cget("font") == "Helvetica 16":
                        child.config(text=title_text)
                        break
        
        # If switching to real mode, set up AWS client
        if not self.mock_mode and BOTO3_AVAILABLE:
            self.setup_aws_client()
    
    def store_screenshot(self, image):
        """Store the current screenshot for thumbnail generation and display"""
        self.current_screenshot = image.copy() if image else None
    
    def generate_thumbnail(self, image, max_size=None):
        """Generate a thumbnail with aspect ratio preservation and size constraints
        
        Args:
            image: PIL Image object to create thumbnail from
            max_size: Tuple of (max_width, max_height), defaults to THUMBNAIL_CONFIG values
            
        Returns:
            PIL Image object containing the thumbnail
        """
        if image is None:
            return None
            
        # Use default thumbnail config if no max_size provided
        if max_size is None:
            max_size = (THUMBNAIL_CONFIG['max_width'], THUMBNAIL_CONFIG['max_height'])
        
        max_width, max_height = max_size
        
        # Get original dimensions
        original_width, original_height = image.size
        
        # Calculate scaling ratio while preserving aspect ratio
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        scale_ratio = min(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = int(original_width * scale_ratio)
        new_height = int(original_height * scale_ratio)
        
        # Use high-quality resampling
        try:
            resample_filter = Image.LANCZOS
        except AttributeError:
            # Fallback for older PIL versions
            resample_filter = Image.ANTIALIAS
        
        # Create and return the thumbnail
        thumbnail = image.resize((new_width, new_height), resample=resample_filter)
        return thumbnail
    
    def get_current_screenshot(self):
        """Get the currently stored screenshot
        
        Returns:
            PIL Image object or None if no screenshot is stored
        """
        return self.current_screenshot
    
    def update_thumbnail(self, image):
        """Update the thumbnail display with a new image"""
        if image is None:
            self.clear_thumbnail()
            return
        
        try:
            # Generate thumbnail
            thumbnail = self.generate_thumbnail(image)
            if thumbnail is None:
                self.clear_thumbnail()
                return
            
            # Convert to Tkinter PhotoImage
            tk_thumbnail = ImageTk.PhotoImage(thumbnail)
            
            # Update the label
            self.thumbnail_label.config(image=tk_thumbnail, text="")
            self.thumbnail_label.image = tk_thumbnail  # Keep reference to prevent garbage collection
            
            # Show the thumbnail frame
            self.thumbnail_frame.pack(fill=tk.X, pady=(10, 5))
            
        except Exception as e:
            print(f"Error updating thumbnail: {e}")
            self.clear_thumbnail()
    
    def clear_thumbnail(self):
        """Clear the thumbnail display and hide the frame"""
        self.thumbnail_label.config(image="", text="Click to view full size")
        self.thumbnail_label.image = None
        self.thumbnail_frame.pack_forget()
    
    def on_thumbnail_click(self, event):
        """Handle thumbnail click to open full-size viewer"""
        if self.current_screenshot is not None and self.viewer_window is None:
            self.viewer_window = ScreenshotViewer(self.root, self.current_screenshot)
            # Clear the reference when window is closed
            self.viewer_window.protocol("WM_DELETE_WINDOW", self.on_viewer_closed)
    
    def on_viewer_closed(self):
        """Handle viewer window being closed"""
        if self.viewer_window:
            self.viewer_window.destroy()
            self.viewer_window = None
    
    def on_analyze_clicked(self):
        """Handle analyze button click"""
        if self.analyzing:
            return
        
        # Start analysis in a separate thread
        self.analyzing = True
        self.analyze_button.config(state=tk.DISABLED)
        self.status_var.set("Capturing screen...")
        self.progress.pack(pady=10)
        self.progress.start()
        
        threading.Thread(target=self.analyze_screen_thread, daemon=True).start()
    
    def analyze_screen_thread(self):
        """Analyze screen in a separate thread"""
        try:
            # Step 1: Prepare for capture (10%)
            self.root.after(0, lambda: self.update_progress(10, "Preparing to capture screen..."))
            
            # Hide our window completely (not just minimize)
            self.root.after(0, self.root.withdraw)
            
            # Give time for window to hide and desktop to settle
            import time
            time.sleep(2)
            
            # Step 2: Capturing screen (30%)
            self.root.after(0, lambda: self.update_progress(30, "Capturing screen..."))
            
            # Capture the full screen
            screen = RegionSelector.capture_full_screen()
            
            # Small delay before showing window again
            time.sleep(0.5)
            
            # Restore our window
            self.root.after(0, self.root.deiconify)
            self.root.after(0, lambda: self.root.lift())  # Bring to front
            self.root.after(0, lambda: self.root.focus_force())  # Give it focus
            
            # If screenshot failed
            if screen is None:
                self.root.after(0, lambda: self.status_var.set("Screenshot failed"))
                self.root.after(0, self.reset_ui)
                return
            
            # Step 3: Screenshot captured (50%)
            self.root.after(0, lambda: self.update_progress(50, "Screenshot captured! Review below..."))
            
            # Show the captured screenshot for approval
            self.root.after(0, lambda: self.show_screenshot_for_approval(screen))
            
        except Exception as e:
            # Make sure window is restored even if there's an error
            self.root.after(0, self.root.deiconify)
            self.root.after(0, lambda: self.root.lift())
            
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: self.update_results(f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def show_screenshot_for_approval(self, screen):
        """Show the captured screenshot for user approval"""
        # Create a new top-level window
        approval_window = tk.Toplevel(self.root)
        approval_window.title("Approve Screenshot")
        approval_window.geometry("800x600")
        
        # Create a frame for the screenshot
        frame = ttk.Frame(approval_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add instructions
        ttk.Label(
            frame,
            text="Review the captured screenshot. Click 'Analyze' to proceed or 'Retake' to capture again.",
            wraplength=780
        ).pack(pady=(0, 10))
        
        # Resize the screenshot to fit in the window
        max_width = 760
        max_height = 450
        width, height = screen.size
        
        # Calculate new dimensions while maintaining aspect ratio
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Use LANCZOS if available, otherwise fall back to ANTIALIAS
            try:
                resample_filter = Image.LANCZOS
            except AttributeError:
                resample_filter = Image.ANTIALIAS
                
            resized_screen = screen.resize((new_width, new_height), resample=resample_filter)
        else:
            resized_screen = screen
        
        # Convert PIL Image to Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(resized_screen)
        
        # Create a label to display the image
        image_label = ttk.Label(frame, image=tk_image)
        image_label.image = tk_image  # Keep a reference to prevent garbage collection
        image_label.pack(pady=10)
        
        # Create buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text="Retake Screenshot",
            command=lambda: self.retake_screenshot(approval_window)
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="Analyze with AI",
            command=lambda: self.proceed_with_analysis(screen, approval_window),
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=10)
        
        # Center the window on screen
        approval_window.update_idletasks()
        width = approval_window.winfo_width()
        height = approval_window.winfo_height()
        x = (approval_window.winfo_screenwidth() // 2) - (width // 2)
        y = (approval_window.winfo_screenheight() // 2) - (height // 2)
        approval_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Make the window modal
        approval_window.transient(self.root)
        approval_window.grab_set()
    
    def retake_screenshot(self, approval_window):
        """Close the approval window and retake the screenshot"""
        approval_window.destroy()
        
        # Reset progress and start retake process
        self.root.after(0, lambda: self.update_progress(10, "Preparing to retake screenshot..."))
        
        # Small delay before retaking
        self.root.after(500, lambda: self.analyze_screen_thread())
    
    def proceed_with_analysis(self, screen, approval_window):
        """Proceed with AI analysis using the approved screenshot"""
        # Close the approval window
        approval_window.destroy()
        
        # Store the screenshot and update thumbnail
        self.store_screenshot(screen)
        self.update_thumbnail(screen)
        
        # Start analysis in a separate thread to avoid blocking UI
        threading.Thread(target=self.ai_analysis_thread, args=(screen,), daemon=True).start()
    
    def ai_analysis_thread(self, screen):
        """Perform AI analysis in a separate thread with progress updates"""
        try:
            # Step 4: Processing image (60%)
            self.root.after(0, lambda: self.update_progress(60, "Processing image..."))
            
            # Step 5: Compressing image (70%)
            self.root.after(0, lambda: self.update_progress(70, "Compressing image..."))
            
            # Step 6: Uploading to AI (80%)
            self.root.after(0, lambda: self.update_progress(80, "Sending to AI..."))
            
            # Step 7: Waiting for AI response (90%)
            self.root.after(0, lambda: self.update_progress(90, "AI is analyzing your screen..."))
            
            # Perform the actual analysis
            suggestion = self.analyze_screen(screen)
            
            # Step 8: Complete (100%)
            self.root.after(0, lambda: self.update_progress(100, "Analysis complete!"))
            
            # Update UI with results
            self.root.after(0, lambda: self.update_results(suggestion))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: self.update_results(f"An error occurred: {str(e)}"))
        finally:
            # Reset UI state after a short delay to show completion
            self.root.after(1000, self.reset_ui)
    
    def update_progress(self, value, status_text):
        """Update progress bar and status text"""
        self.progress.config(mode='determinate')
        self.progress_var.set(value)
        self.status_var.set(status_text)
    
    def reset_ui(self):
        """Reset UI after analysis"""
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_button.config(state=tk.NORMAL)
        self.status_var.set("Ready")
        self.analyzing = False
    
    def update_results(self, text):
        """Update results text area"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)
    
    def compress_image(self, image):
        """Compress the image to reduce size"""
        # Create a buffer for the compressed image
        buffer = BytesIO()
        
        # Save with maximum compression
        image.save(
            buffer, 
            format='PNG', 
            optimize=True, 
            quality=85,  # Lower quality for JPEG, doesn't affect PNG
            compress_level=9  # Maximum compression for PNG (0-9)
        )
        
        # Get the compressed size
        compressed_size = buffer.tell() / 1024  # Size in KB
        print(f"Compressed image size: {compressed_size:.2f} KB")
        
        # If still too large, resize the image
        if compressed_size > 1000:  # If larger than ~1MB
            # Calculate new dimensions (reduce by 25%)
            width, height = image.size
            new_width = int(width * 0.75)
            new_height = int(height * 0.75)
            
            # Resize and compress again
            # Use LANCZOS if available, otherwise fall back to ANTIALIAS
            try:
                resample_filter = Image.LANCZOS
            except AttributeError:
                resample_filter = Image.ANTIALIAS
                
            resized_image = image.resize((new_width, new_height), resample=resample_filter)
            buffer = BytesIO()
            resized_image.save(
                buffer, 
                format='PNG', 
                optimize=True, 
                compress_level=9
            )
            
            print(f"Resized and compressed image size: {buffer.tell() / 1024:.2f} KB")
        
        # Reset buffer position
        buffer.seek(0)
        return buffer
    
    def image_to_base64(self, image):
        """Convert PIL Image to base64 string with compression"""
        # Compress the image
        buffer = self.compress_image(image)
        
        # Convert to base64
        return base64.b64encode(buffer.getvalue()).decode()
    
    def generate_mock_response(self, image):
        """Generate a mock AI response for testing"""
        # Get image dimensions
        width, height = image.size
        now = datetime.datetime.now()
        
        mock_response = f"""
I can see your screen capture (resolution: {width}x{height}).

Based on what I see, here's how I can help:

1. You appear to be working on a Python project with a GUI application.
2. I could help you optimize your code structure or suggest UI improvements.
3. Consider adding error handling for edge cases and improving the user feedback when operations are in progress.

The current time is {now.strftime('%H:%M:%S')} and I notice you're testing an AI screen assistant application.
        """
        return mock_response.strip()
    
    def analyze_screen(self, image):
        """Send screen to AI for analysis or use mock response"""
        try:
            # If in mock mode, return a mock response
            if self.mock_mode:
                # Simulate network delay
                import time
                time.sleep(2)
                return self.generate_mock_response(image)
            
            base64_image = self.image_to_base64(image)
            
            # Prepare the request for Claude 3 Sonnet
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "I'm showing you my current computer screen. Based on what you see, please:\n\n1. Briefly describe what you see on the screen\n2. Suggest ONE specific way you could help me with what I'm working on\n3. Provide a specific, actionable tip or solution\n\nBe concise but helpful. Focus on providing practical assistance related to what I'm doing."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Check if we're using bearer token authentication
            if hasattr(self, 'using_bearer_token') and self.using_bearer_token:
                # Use the token client for authentication
                token_client = BedrockTokenClient(
                    token=self.bedrock_token,
                    region=os.environ.get('AWS_REGION', 'us-east-1')
                )
                response = token_client.invoke_model(
                    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                    body=json.dumps(request_body)
                )
            else:
                # Use standard AWS authentication through boto3
                response = self.bedrock.invoke_model(
                    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                    body=json.dumps(request_body)
                )
            
            response_body = json.loads(response.body.read())
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return f"Error analyzing screen: {str(e)}"

class ScreenshotViewer(tk.Toplevel):
    """Window for displaying full-size screenshots"""
    
    def __init__(self, parent, image):
        super().__init__(parent)
        self.parent = parent
        self.image = image
        
        self.title("Screenshot Viewer")
        self.transient(parent)
        self.grab_set()
        
        # Set up the UI
        self.setup_ui()
        
        # Center the window on screen
        self.center_window()
        
        # Bind escape key to close
        self.bind('<Escape>', self.on_escape_key)
        self.focus_set()
    
    def setup_ui(self):
        """Set up the viewer UI"""
        # Create main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Calculate display size (up to 1080p)
        max_width = 1920
        max_height = 1080
        
        original_width, original_height = self.image.size
        
        # Calculate scaling to fit within max dimensions
        if original_width > max_width or original_height > max_height:
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            scale_ratio = min(width_ratio, height_ratio)
            
            display_width = int(original_width * scale_ratio)
            display_height = int(original_height * scale_ratio)
            
            # Use high-quality resampling
            try:
                resample_filter = Image.LANCZOS
            except AttributeError:
                resample_filter = Image.ANTIALIAS
                
            display_image = self.image.resize((display_width, display_height), resample=resample_filter)
        else:
            display_image = self.image
        
        # Convert to Tkinter PhotoImage
        self.tk_image = ImageTk.PhotoImage(display_image)
        
        # Create image label
        image_label = ttk.Label(main_frame, image=self.tk_image)
        image_label.pack(pady=(0, 10))
        
        # Create close button
        close_button = ttk.Button(
            main_frame,
            text="Close",
            command=self.close_window,
            style="Accent.TButton"
        )
        close_button.pack(pady=5)
        
        # Set window size based on content
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        self.geometry(f"{width}x{height}")
    
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def close_window(self):
        """Close the viewer window"""
        self.destroy()
    
    def on_escape_key(self, event):
        """Handle Escape key press"""
        self.close_window()

def main():
    """Main entry point"""
    # Check if running in mock mode
    if args.mock:
        print("Running in MOCK MODE - No AWS credentials required")
        root = tk.Tk()
        app = ScreenAssistantApp(root, mock_mode=True)
        root.mainloop()
        return
    
    # Check boto3 availability
    if not BOTO3_AVAILABLE:
        print("Error: boto3 library not available. Please install it with 'pip install boto3'")
        return
    
    # Start application
    root = tk.Tk()
    app = ScreenAssistantApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()