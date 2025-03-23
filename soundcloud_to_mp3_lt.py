import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import tempfile
import shutil
import re

class SoundCloudOpusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SoundCloud Downloader & Opus Converter")
        self.root.geometry("800x600")
        
        # Set up variables
        self.is_downloading = False
        self.is_converting = False
        self.stop_requested = False
        self.process = None
        
        # Create UI elements
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.downloader_tab = ttk.Frame(self.notebook)
        self.converter_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.downloader_tab, text="SoundCloud Downloader")
        self.notebook.add(self.converter_tab, text="Opus Converter")
        
        # Set up each tab
        self.setup_downloader_tab()
        self.setup_converter_tab()
    
    def setup_downloader_tab(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.downloader_tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="SoundCloud Downloader", font=('Helvetica', 16, 'bold')).pack(pady=(0, 20))
        
        # URL input frame
        url_frame = ttk.LabelFrame(main_frame, text="SoundCloud URL")
        url_frame.pack(fill=tk.X, pady=10)
        
        url_inner_frame = ttk.Frame(url_frame, padding=10)
        url_inner_frame.pack(fill=tk.X)
        
        ttk.Label(url_inner_frame, text="URL:").pack(side=tk.LEFT, padx=(0, 10))
        self.url_var = tk.StringVar()
        ttk.Entry(url_inner_frame, textvariable=self.url_var, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Output directory frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Location")
        output_frame.pack(fill=tk.X, pady=10)
        
        output_inner_frame = ttk.Frame(output_frame, padding=10)
        output_inner_frame.pack(fill=tk.X)
        
        ttk.Label(output_inner_frame, text="Save to:").pack(side=tk.LEFT, padx=(0, 10))
        self.download_output_var = tk.StringVar(value=os.path.expanduser("~/Music"))
        self.download_output_entry = ttk.Entry(output_inner_frame, textvariable=self.download_output_var, width=50)
        self.download_output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(output_inner_frame, text="Browse...", command=self.browse_download_directory).pack(side=tk.LEFT)
        
        # Batch download button
        batch_frame = ttk.Frame(main_frame)
        batch_frame.pack(fill=tk.X, pady=10)
        ttk.Button(batch_frame, text="Add Multiple URLs...", command=self.show_batch_dialog).pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        self.download_button = ttk.Button(button_frame, text="Download", command=self.start_download, width=15)
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_download, width=15, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status area
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Use a Text widget with scrollbar for status
        status_scroll = ttk.Scrollbar(status_frame)
        status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.download_status_text = tk.Text(status_frame, height=10, wrap=tk.WORD, yscrollcommand=status_scroll.set)
        self.download_status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        status_scroll.config(command=self.download_status_text.yview)
        
        # Set initial status
        self.update_download_status("Ready. Enter a SoundCloud URL to begin.")
        
        # Progress bar
        self.download_progress_var = tk.DoubleVar(value=0.0)
        self.download_progress_bar = ttk.Progressbar(main_frame, orient="horizontal", variable=self.download_progress_var, mode="determinate")
        self.download_progress_bar.pack(fill=tk.X, pady=10)
    
    def setup_converter_tab(self):
        # Main frame
        main_frame = ttk.Frame(self.converter_tab, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Opus to MP3 Converter", font=("Helvetica", 16)).pack(pady=(0, 15))
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="File Selection")
        file_frame.pack(fill=tk.X, pady=10)
        
        # Opus file
        opus_frame = ttk.Frame(file_frame, padding=5)
        opus_frame.pack(fill=tk.X, pady=5)
        ttk.Label(opus_frame, text="Opus File:").pack(side=tk.LEFT, padx=(0, 10))
        self.opus_var = tk.StringVar()
        ttk.Entry(opus_frame, textvariable=self.opus_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(opus_frame, text="Browse...", command=self.browse_opus).pack(side=tk.LEFT)
        
        # Image file
        img_frame = ttk.Frame(file_frame, padding=5)
        img_frame.pack(fill=tk.X, pady=5)
        ttk.Label(img_frame, text="Image File:").pack(side=tk.LEFT, padx=(0, 10))
        self.img_var = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.img_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(img_frame, text="Browse...", command=self.browse_img).pack(side=tk.LEFT)
        
        # Output directory
        out_frame = ttk.Frame(file_frame, padding=5)
        out_frame.pack(fill=tk.X, pady=5)
        ttk.Label(out_frame, text="Output To:").pack(side=tk.LEFT, padx=(0, 10))
        self.convert_output_var = tk.StringVar(value=os.path.expanduser("~/Music"))
        ttk.Entry(out_frame, textvariable=self.convert_output_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(out_frame, text="Browse...", command=self.browse_convert_output).pack(side=tk.LEFT)
        
        # Metadata
        meta_frame = ttk.LabelFrame(main_frame, text="Metadata")
        meta_frame.pack(fill=tk.X, pady=10)
        
        # Title
        title_frame = ttk.Frame(meta_frame, padding=5)
        title_frame.pack(fill=tk.X)
        ttk.Label(title_frame, text="Title:").pack(side=tk.LEFT, padx=(0, 10))
        self.title_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=self.title_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Artist
        artist_frame = ttk.Frame(meta_frame, padding=5)
        artist_frame.pack(fill=tk.X)
        ttk.Label(artist_frame, text="Artist:").pack(side=tk.LEFT, padx=(0, 10))
        self.artist_var = tk.StringVar()
        ttk.Entry(artist_frame, textvariable=self.artist_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Convert to MP3", command=self.start_conversion)
        self.convert_btn.pack(pady=15)
        
        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrolled text for status
        convert_status_scroll = ttk.Scrollbar(status_frame)
        convert_status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.convert_status_text = tk.Text(status_frame, height=8, wrap=tk.WORD, yscrollcommand=convert_status_scroll.set)
        self.convert_status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        convert_status_scroll.config(command=self.convert_status_text.yview)
        
        # Initial status
        self.update_convert_status("Ready. Select files to begin.")
        
        # Progress bar
        self.convert_progress_var = tk.DoubleVar()
        ttk.Progressbar(main_frame, variable=self.convert_progress_var, maximum=100).pack(fill=tk.X, pady=10)
    
    # === Downloader Methods ===
    def browse_download_directory(self):
        directory = filedialog.askdirectory(initialdir=self.download_output_var.get())
        if directory:
            self.download_output_var.set(directory)
    
    def update_download_status(self, message):
        self.download_status_text.insert(tk.END, message + "\n")
        self.download_status_text.see(tk.END)
        self.root.update_idletasks()
    
    def show_batch_dialog(self):
        batch_window = tk.Toplevel(self.root)
        batch_window.title("Add Multiple URLs")
        batch_window.geometry("600x400")
        
        # Instructions
        ttk.Label(batch_window, text="Enter one SoundCloud URL per line:").pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        # Text area with scrollbar
        text_frame = ttk.Frame(batch_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(text_frame, yscrollcommand=text_scroll.set)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=text_area.yview)
        
        # Buttons
        button_frame = ttk.Frame(batch_window)
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        def process_urls():
            text = text_area.get("1.0", tk.END).strip()
            if text:
                urls = [line.strip() for line in text.split("\n") if line.strip()]
                valid_urls = [url for url in urls if "soundcloud.com/" in url]
                
                if valid_urls:
                    self.process_multiple_urls(valid_urls)
                    batch_window.destroy()
                else:
                    messagebox.showerror("Invalid URLs", "No valid SoundCloud URLs found!")
            else:
                messagebox.showerror("Empty Input", "Please enter at least one URL!")
        
        ttk.Button(button_frame, text="Download All", command=process_urls).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=batch_window.destroy).pack(side=tk.RIGHT)
    
    def process_multiple_urls(self, urls):
        if self.is_downloading:
            messagebox.showerror("Already Downloading", "Please wait for the current download to finish.")
            return
        
        # Update status
        self.update_download_status(f"Added {len(urls)} URLs for batch downloading.")
        
        # Start batch download
        threading.Thread(target=self.batch_download_thread, args=(urls,), daemon=True).start()
    
    def batch_download_thread(self, urls):
        # Update UI state
        self.is_downloading = True
        self.stop_requested = False
        self.download_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Get output directory
        output_dir = self.download_output_var.get()
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
            except:
                self.update_download_status(f"Error: Could not create output directory: {output_dir}")
                self.reset_download_ui()
                return
        
        # Download each URL
        total = len(urls)
        for i, url in enumerate(urls):
            if self.stop_requested:
                self.update_download_status("Batch download stopped by user.")
                break
            
            self.update_download_status(f"Processing URL {i+1} of {total}: {url}")
            
            # Download this URL
            success = self.download_single(url, output_dir)
            
            if not success and not self.stop_requested:
                answer = messagebox.askyesno("Download Error", 
                                          f"Failed to download: {url}\n\nContinue with the next URL?")
                if not answer:
                    self.update_download_status("Batch download stopped.")
                    break
        
        # Reset UI when done
        self.reset_download_ui()
        self.update_download_status("Batch download completed.")
    
    def download_single(self, url, output_dir):
        """Download a single track with just yt-dlp"""
        # First ensure yt-dlp is installed and up to date
        try:
            self.update_download_status("Checking yt-dlp installation...")
            try:
                # Check if yt-dlp exists
                subprocess.run(["yt-dlp", "--version"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             check=True)
                
                # Update yt-dlp
                self.update_download_status("Updating yt-dlp...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
            except FileNotFoundError:
                # Install yt-dlp if not found
                self.update_download_status("Installing yt-dlp...")
                subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              check=True)
        except Exception as e:
            self.update_download_status(f"Warning: yt-dlp check/install failed: {str(e)}")
            # Continue anyway as it might already be installed
        try:
            # Update progress bar for this individual download
            self.download_progress_var.set(0)
            
            # Create the yt-dlp command
            cmd = [
                "yt-dlp",
                "--no-check-certificate",  # Skip SSL verification
                "--no-playlist",           # Don't download playlists
                "--extract-audio",         # Extract audio
                "--audio-format", "mp3",   # Convert to mp3 directly
                "--write-thumbnail",       # Save thumbnail
                "--embed-thumbnail",       # Embed thumbnail
                "--add-metadata",          # Add metadata
                "--output", os.path.join(output_dir, "%(title)s.%(ext)s"),
                "--verbose",               # Show verbose output
                url
            ]
            
            # Run the command
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            track_info = {}
            last_line = ""
            
            # Parse output
            for line in self.process.stdout:
                if self.stop_requested:
                    self.process.terminate()
                    return False
                
                # Update status with selected output (to avoid too much noise)
                if any(x in line for x in ['download', 'extract', 'Writing', 'Destination', 'Converting', '[info]', '[debug]', 'ERROR', 'Warning']):
                    self.update_download_status(line.strip())
                    last_line = line.strip()
                
                # Try to parse progress
                try:
                    if '[download]' in line and '%' in line:
                        percent_str = re.search(r'(\d+\.?\d*)%', line)
                        if percent_str:
                            percent = float(percent_str.group(1))
                            self.download_progress_var.set(percent)
                except:
                    pass
            
            # Wait for completion
            self.process.wait()
            
            return_code = self.process.returncode
            
            if return_code == 0 and not self.stop_requested:
                # Find MP3 file
                latest_mp3_file = self.find_latest_mp3_file(output_dir)
                if latest_mp3_file:
                    self.update_download_status(f"Successfully downloaded: {os.path.basename(latest_mp3_file)}")
                else:
                    self.update_download_status("Download completed, but couldn't find the MP3 file.")
                
                self.download_progress_var.set(100)
                return True
            else:
                # Print any output to help diagnose issue
                error_message = f"Download failed with code {return_code}"
                if "ffprobe" in last_line or "ffmpeg" in last_line:
                    error_message += "\n\nFFmpeg issue detected. Let's try downloading without conversion."
                    # Try without conversion
                    return self.download_without_conversion(url, output_dir)
                    
                self.update_download_status(error_message)
                return False
                
        except Exception as e:
            self.update_download_status(f"Error: {str(e)}")
            return False
    
    def download_without_conversion(self, url, output_dir):
        """Fallback method: download without requiring conversion"""
        try:
            self.update_download_status("Trying fallback method (no conversion)...")
            
            # Create the yt-dlp command - simpler without conversion
            cmd = [
                "yt-dlp",
                "--no-check-certificate",
                "--no-playlist",
                "--output", os.path.join(output_dir, "%(title)s.%(ext)s"),
                url
            ]
            
            # Run the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Parse output
            for line in process.stdout:
                if self.stop_requested:
                    process.terminate()
                    return False
                
                # Update status
                if any(x in line for x in ['download', 'Destination', '[info]', 'ERROR', 'Warning']):
                    self.update_download_status(line.strip())
                
                # Try to parse progress
                try:
                    if '[download]' in line and '%' in line:
                        percent_str = re.search(r'(\d+\.?\d*)%', line)
                        if percent_str:
                            percent = float(percent_str.group(1))
                            self.download_progress_var.set(percent)
                except:
                    pass
            
            # Wait for completion
            process.wait()
            
            if process.returncode == 0 and not self.stop_requested:
                self.update_download_status("Download completed successfully!")
                self.download_progress_var.set(100)
                return True
            else:
                self.update_download_status(f"Fallback download failed with error code: {process.returncode}")
                return False
                
        except Exception as e:
            self.update_download_status(f"Fallback error: {str(e)}")
            return False
    
    def find_latest_mp3_file(self, directory):
        """Find the latest MP3 file in the directory"""
        try:
            mp3_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                         if f.lower().endswith('.mp3')]
            
            if not mp3_files:
                return None
                
            return max(mp3_files, key=os.path.getmtime)
        except:
            return None
    
    def find_latest_opus_file(self, directory):
        """Find the latest Opus file in the directory"""
        try:
            opus_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                          if f.lower().endswith('.opus')]
            
            if not opus_files:
                return None
                
            return max(opus_files, key=os.path.getmtime)
        except:
            return None
    
    def find_latest_jpg_file(self, directory):
        """Find the latest JPG file in the directory"""
        try:
            jpg_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if not jpg_files:
                return None
                
            return max(jpg_files, key=os.path.getmtime)
        except:
            return None
    
    def start_download(self):
        # Get URL
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a SoundCloud URL")
            return
            
        if "soundcloud.com/" not in url:
            messagebox.showerror("Error", "Please enter a valid SoundCloud URL")
            return
        
        # Check if already downloading
        if self.is_downloading:
            messagebox.showinfo("Already Downloading", "A download is already in progress.")
            return
        
        # Get output directory
        output_dir = self.download_output_var.get()
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
            except:
                messagebox.showerror("Error", f"Could not create output directory: {output_dir}")
                return
        
        # Check if yt-dlp is installed
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, check=True)
        except FileNotFoundError:
            if messagebox.askyesno("Install yt-dlp", 
                               "yt-dlp is not installed but is required for downloading.\n\n"
                               "Would you like to install it now? (requires pip)"):
                try:
                    self.update_download_status("Installing yt-dlp...")
                    subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
                    self.update_download_status("yt-dlp installed successfully!")
                except Exception as e:
                    messagebox.showerror("Installation Error", f"Failed to install yt-dlp: {str(e)}")
                    return
            else:
                return
        
        # Update UI state
        self.is_downloading = True
        self.stop_requested = False
        self.download_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.download_progress_var.set(0)
        
        # Start download in separate thread
        download_thread = threading.Thread(target=self.download_thread, args=(url, output_dir))
        download_thread.daemon = True
        download_thread.start()
    
    def stop_download(self):
        if self.is_downloading:
            self.stop_requested = True
            self.update_download_status("Stopping download...")
            
            # Try to terminate the process if it exists
            if self.process:
                try:
                    self.process.terminate()
                except:
                    pass
    
    def reset_download_ui(self):
        self.is_downloading = False
        self.download_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def download_thread(self, url, output_dir):
        try:
            self.update_download_status(f"Starting download from: {url}")
            
            success = self.download_single(url, output_dir)
            
            if success:
                self.update_download_status("Download completed successfully!")
                
                # Ask if user wants to also convert any opus files
                # if messagebox.askyesno("Download Complete", 
                #                     "Download completed successfully!\n\nWould you like to check for and convert any Opus files?"):
                #     # Switch to converter tab
                #     self.notebook.select(1)
                    
                #     # Look for opus and jpg files
                #     opus_file = self.find_latest_opus_file(output_dir)
                #     jpg_file = self.find_latest_jpg_file(output_dir)
                    
                #     if opus_file:
                #         self.opus_var.set(opus_file)
                #         # Try to extract artist/title from filename
                #         filename = os.path.basename(opus_file)
                #         name_part = os.path.splitext(filename)[0]
                #         if " - " in name_part:
                #             parts = name_part.split(" - ")
                #             if len(parts) >= 2:
                #                 self.artist_var.set(parts[0])
                #                 self.title_var.set(parts[1])
                    
                #     if jpg_file:
                #         self.img_var.set(jpg_file)
                    
                #     self.convert_output_var.set(output_dir)
            else:
                self.update_download_status("Download failed or was stopped.")
            
        except Exception as e:
            self.update_download_status(f"Error: {str(e)}")
        finally:
            self.reset_download_ui()
    
    # === Converter Methods ===
    def browse_opus(self):
        file_path = filedialog.askopenfilename(
            title="Select Opus File",
            filetypes=[("Opus files", "*.opus"), ("All files", "*.*")]
        )
        if file_path:
            self.opus_var.set(file_path)
            # Try to extract artist/title from filename
            filename = os.path.basename(file_path)
            name_part = os.path.splitext(filename)[0]
            if " - " in name_part:
                parts = name_part.split(" - ")
                if len(parts) >= 2:
                    self.artist_var.set(parts[0])
                    self.title_var.set(parts[1])
    
    def browse_img(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if file_path:
            self.img_var.set(file_path)
    
    def browse_convert_output(self):
        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.convert_output_var.get()
        )
        if dir_path:
            self.convert_output_var.set(dir_path)
    
    def update_convert_status(self, message):
        self.convert_status_text.insert(tk.END, message + "\n")
        self.convert_status_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_conversion(self):
        # Check files
        opus_file = self.opus_var.get()
        if not opus_file or not os.path.exists(opus_file):
            messagebox.showerror("Error", "Please select a valid Opus file")
            return
        
        img_file = self.img_var.get()
        if img_file and not os.path.exists(img_file):
            messagebox.showerror("Error", "Image file not found")
            return
        
        # Check output directory
        out_dir = self.convert_output_var.get()
        if not os.path.isdir(out_dir):
            try:
                os.makedirs(out_dir)
            except:
                messagebox.showerror("Error", "Cannot create output directory")
                return
        
        # Prevent multiple conversions
        if self.is_converting:
            return
            
        # Get output filename
        if self.artist_var.get() and self.title_var.get():
            safe_name = f"{self.artist_var.get()} - {self.title_var.get()}"
            safe_name = "".join(c if c.isalnum() or c in " -_." else "_" for c in safe_name)
        else:
            base_name = os.path.basename(opus_file)
            safe_name = os.path.splitext(base_name)[0]
            
        output_file = os.path.join(out_dir, safe_name + ".mp3")
        
        # Start conversion in thread
        self.is_converting = True
        self.convert_btn.config(state=tk.DISABLED)
        self.convert_progress_var.set(0)
        
        thread = threading.Thread(target=self.convert_file, args=(opus_file, img_file, output_file))
        thread.daemon = True
        thread.start()
    
    def convert_file(self, opus_file, img_file, output_file):
        try:
            self.update_convert_status(f"Converting {os.path.basename(opus_file)}...")
            
            # Method 1: yt-dlp direct conversion
            try:
                self.update_convert_status("Trying conversion with yt-dlp...")
                self.convert_progress_var.set(10)
                
                # Modified command for yt-dlp with --enable-file-urls flag
                opus_path = f"file://{os.path.abspath(opus_file)}"
                cmd = [
                    "yt-dlp",
                    "--enable-file-urls",  # Enable file:// URLs
                    "--no-simulate",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--audio-quality", "0",  # best quality
                    "--output", output_file,
                    "--force-overwrites",
                    opus_path
                ]
                
                # Run command
                result = subprocess.run(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
                
                self.convert_progress_var.set(60)
                
                if result.returncode == 0:
                    self.update_convert_status("Conversion successful!")
                else:
                    self.update_convert_status(f"yt-dlp failed: {result.stderr}")
                    raise Exception("yt-dlp conversion failed")
            except Exception as e:
                self.update_convert_status(f"yt-dlp method failed: {str(e)}")
                
                # Method 2: Try direct ffmpeg conversion - use absolute paths and fix slashes
                try:
                    self.update_convert_status("Trying direct ffmpeg conversion...")
                    
                    # Fix paths for Windows
                    abs_opus_file = os.path.abspath(opus_file).replace('/', '\\')
                    abs_output_file = os.path.abspath(output_file).replace('/', '\\')
                    
                    # Check if FFmpeg exists
                    ffmpeg_found = False
                    for path in ["ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe", os.path.expanduser("~/ffmpeg/bin/ffmpeg")]:
                        try:
                            subprocess.run([path, "-version"], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          check=True)
                            ffmpeg_found = True
                            ffmpeg_cmd = path
                            self.update_convert_status(f"Found ffmpeg at: {path}")
                            break
                        except:
                            continue
                    
                    if not ffmpeg_found:
                        self.update_convert_status("FFmpeg not found in PATH. Attempting to download...")
                        
                        # For simplicity in this app, direct the user to install FFmpeg
                        if messagebox.askyesno("FFmpeg Not Found", 
                                            "FFmpeg is required but not found. Would you like to open the download page?"):
                            import webbrowser
                            webbrowser.open("https://ffmpeg.org/download.html")
                            
                        self.update_convert_status("Continuing with other conversion methods...")
                        raise Exception("FFmpeg not found")
                    
                    # Try direct ffmpeg conversion
                    cmd = [ffmpeg_cmd, "-i", abs_opus_file, "-y", "-acodec", "libmp3lame", "-q:a", "2", abs_output_file]
                    self.update_convert_status(f"Running command: {' '.join(cmd)}")
                    
                    result = subprocess.run(cmd, 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          text=True)
                    
                    if result.returncode == 0:
                        self.update_convert_status("FFmpeg conversion successful!")
                    else:
                        self.update_convert_status(f"FFmpeg error: {result.stderr}")
                        raise Exception("FFmpeg conversion failed")
                    
                    if result.returncode == 0:
                        self.update_convert_status("ffmpeg conversion successful!")
                    else:
                        self.update_convert_status(f"ffmpeg error: {result.stderr}")
                        raise Exception("ffmpeg conversion failed")
                        
                except Exception as e:
                    self.update_convert_status(f"Direct FFmpeg conversion failed: {str(e)}")
                    
                    # Method 3: Try fallback with a simpler direct conversion approach
                    try:
                        self.update_convert_status("Trying simpler conversion approach...")
                        
                        # Try a simple file copy approach if the file is actually an MP3 with wrong extension
                        if os.path.exists(opus_file):
                            # Create a temporary copy of the file
                            temp_file = os.path.join(tempfile.gettempdir(), "temp_audio_file.mp3")
                            shutil.copy2(opus_file, temp_file)
                            
                            self.update_convert_status(f"Copied file to {temp_file}")
                            
                            # Check if it can be opened as an MP3
                            try:
                                subprocess.run([sys_module.executable, "-m", "pip", "install", "mutagen"], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE,
                                              check=True)
                                
                                from mutagen.mp3 import MP3
                                try:
                                    audio = MP3(temp_file)
                                    # If no exception, it's a valid MP3
                                    self.update_convert_status("File is actually an MP3 with wrong extension")
                                    shutil.copy2(opus_file, output_file)
                                    self.update_convert_status("Simple copy successful!")
                                    os.unlink(temp_file)
                                    return  # Success - exit the method
                                except:
                                    self.update_convert_status("Not a valid MP3 file")
                            except:
                                self.update_convert_status("Couldn't verify file format")
                                
                        # Alternative approach - use a manual conversion with ffmpeg libraries
                        self.update_convert_status("Trying to install required packages...")
                        
                        # Install pydub as a final approach
                        subprocess.run([sys_module.executable, "-m", "pip", "install", "pydub", "simpleaudio"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
                                      
                        import importlib
                        if 'pydub' in sys_module.modules:
                            importlib.reload(sys_module.modules['pydub'])
                        else:
                            importlib.import_module('pydub')
                        
                        from pydub import AudioSegment
                        
                        self.update_convert_status(f"Converting with pydub...")
                        
                        # Try different formats
                        formats_to_try = ["opus", "ogg", "mp3", "wav"]
                        success = False
                        
                        for fmt in formats_to_try:
                            try:
                                self.update_convert_status(f"Trying to load as {fmt} format...")
                                sound = AudioSegment.from_file(opus_file, format=fmt)
                                sound.export(output_file, format="mp3")
                                self.update_convert_status(f"Conversion successful using {fmt} format!")
                                success = True
                                break
                            except Exception as e:
                                self.update_convert_status(f"Failed with {fmt} format: {str(e)}")
                        
                        if not success:
                            self.update_convert_status("Could not convert with any format")
                            raise Exception("All format attempts failed")
                    except Exception as e:
                        self.update_convert_status(f"moviepy conversion failed: {str(e)}")
                    
                    except Exception as e:
                        self.update_convert_status(f"All conversion methods failed: {str(e)}")
                        
                        # Final fallback - just suggest manual installation of ffmpeg
                        message = ("All conversion methods failed. The simplest solution is to:\n\n"
                                  "1. Install FFmpeg from https://ffmpeg.org/download.html\n"
                                  "2. Add it to your system PATH\n"
                                  "3. Try the conversion again\n\n"
                                  "Would you like to open the FFmpeg download page?")
                        
                        if messagebox.askyesno("Conversion Failed", message):
                            import webbrowser
                            webbrowser.open("https://ffmpeg.org/download.html")
                        
                        raise Exception("All conversion methods failed")
                    except Exception as e:
                        self.update_convert_status(f"All conversion methods failed: {str(e)}")
                        messagebox.showerror("Conversion Failed", 
                                          "All conversion methods failed. Please install FFmpeg manually.")
                        self.is_converting = False
                        self.convert_btn.config(state=tk.NORMAL)
                        return
            
            # Add metadata and album art
            self.convert_progress_var.set(80)
            self.update_convert_status("Adding metadata...")
            
            # Check if output file was created
            if not os.path.exists(output_file):
                self.update_convert_status("Error: Output file was not created.")
                self.is_converting = False
                self.convert_btn.config(state=tk.NORMAL)
                return
            
            # Try different methods for adding metadata
            try:
                # Method 1: eyed3
                try:
                    self.update_convert_status("Installing eyed3 for metadata...")
                    subprocess.run([sys.executable, "-m", "pip", "install", "eyed3"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  check=True)
                    
                    self.update_convert_status("Adding metadata with eyed3...")
                    import eyed3
                    
                    audiofile = eyed3.load(output_file)
                    if audiofile.tag is None:
                        audiofile.initTag()
                    
                    if self.title_var.get():
                        audiofile.tag.title = self.title_var.get()
                    if self.artist_var.get():
                        audiofile.tag.artist = self.artist_var.get()
                    
                    # Add image if available
                    if img_file and os.path.exists(img_file):
                        with open(img_file, "rb") as img_data:
                            audiofile.tag.images.set(3, img_data.read(), "image/jpeg")
                    
                    audiofile.tag.save()
                    self.update_convert_status("Added metadata with eyed3!")
                except Exception as e:
                    self.update_convert_status(f"eyed3 failed: {str(e)}")
                    
                    # Method 2: mutagen
                    try:
                        self.update_convert_status("Installing mutagen for metadata...")
                        subprocess.run([sys.executable, "-m", "pip", "install", "mutagen"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      check=True)
                        
                        self.update_convert_status("Adding metadata with mutagen...")
                        from mutagen.id3 import ID3, TIT2, TPE1, APIC
                        from mutagen.mp3 import MP3
                        
                        # Add ID3 header if it doesn't exist
                        try:
                            audio = MP3(output_file, ID3=ID3)
                            audio.add_tags()
                        except:
                            audio = MP3(output_file)
                        
                        # Add basic tags
                        if self.title_var.get():
                            audio.tags.add(TIT2(encoding=3, text=self.title_var.get()))
                        if self.artist_var.get():
                            audio.tags.add(TPE1(encoding=3, text=self.artist_var.get()))
                        
                        # Add image if available
                        if img_file and os.path.exists(img_file):
                            with open(img_file, "rb") as img_data:
                                audio.tags.add(
                                    APIC(
                                        encoding=3,
                                        mime='image/jpeg',
                                        type=3,
                                        desc='Cover',
                                        data=img_data.read()
                                    )
                                )
                        
                        audio.save()
                        self.update_convert_status("Added metadata with mutagen!")
                    except Exception as e:
                        self.update_convert_status(f"mutagen failed: {str(e)}")
                        self.update_convert_status("Could not add metadata, but MP3 was created.")
            except:
                self.update_convert_status("Could not add metadata, but MP3 was created.")
            
            # Finish
            self.convert_progress_var.set(100)
            self.update_convert_status(f"Conversion completed! Saved to: {output_file}")
            messagebox.showinfo("Success", f"Conversion completed!\nSaved to: {output_file}")
        except Exception as e:
            self.update_convert_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.is_converting = False
            self.convert_btn.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = SoundCloudOpusApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()