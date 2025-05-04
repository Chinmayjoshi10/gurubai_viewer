#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, font, messagebox
import banidb
import sys
import signal
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gurbani-viewer.log'),
        logging.StreamHandler()
    ]
)

class GurbaniViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Gurbani Viewer")
        
        # Make window fullscreen
        self.root.attributes('-fullscreen', True)
        
        # Set window background color to black
        self.root.configure(bg='#000000')
        
        # Bind ESC key to exit
        self.root.bind('<Escape>', lambda e: self.cleanup())
        
        # Initialize state
        self.current_ang = 1
        self.total_angs = 1430
        self.is_paused = False
        self.auto_switch_timer = None
        self.current_verse_index = 0
        self.current_ang_verses = []
        
        # Test banidb connection first
        try:
            test_data = banidb.angs(1)
            if not test_data or 'page' not in test_data:
                raise Exception("Invalid response from banidb")
            logging.info("Successfully connected to banidb")
        except Exception as e:
            logging.error(f"Failed to connect to banidb: {str(e)}")
            messagebox.showerror("Error", f"Failed to connect to banidb: {str(e)}")
            self.cleanup()
            return
            
        # Define Bani categories and their ang ranges according to traditional Nitnem structure
        self.bani_categories = {
            "Morning Nitnem": {
                "Japji Sahib": (1, 8),
                "Jaap Sahib": (9, 10),
                "Tav Prasad Savaiye": (11, 12),
                "Chaupai Sahib": (13, 15),
                "Anand Sahib": (16, 17)
            },
            "Evening Nitnem": {
                "Rehras Sahib": (18, 20),
                "Kirtan Sohila": (21, 22)
            },
            "Special Banis": {
                "Sukhmani Sahib": (23, 25),
                "Dukh Bhanjani Sahib": (26, 28),
                "Asa Di Vaar": (29, 31),
                "Shabad Hazare": (32, 34),
                "Barah Maha": (35, 37),
                "Aarti": (38, 40),
                "Basant Ki Vaar": (41, 43),
                "Salok Mahalla 9": (44, 46),
                "Laavan": (47, 49),
                "Raag Mala": (50, 52)
            },
            "Daily Hukamnama": {
                "Hukamnama": (1, 1430)  # Full range for daily Hukamnama
            }
        }
        
        try:
            # Configure styles
            self.configure_styles()
            
            # Create main frame with padding
            self.main_frame = ttk.Frame(root, style='Main.TFrame')
            self.main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
            
            # Create menu
            self.create_menu()
            
            # Create header
            self.create_header()
            
            # Create text areas
            self.create_text_areas()
            
            # Create controls
            self.create_controls()
            
            # Create footer
            self.create_footer()
            
            # Load initial content
            self.load_ang()
            
            # Start auto-switch
            self.start_auto_switch()
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        except Exception as e:
            logging.error(f"Error initializing GurbaniViewer: {str(e)}")
            messagebox.showerror("Error", f"Failed to initialize: {str(e)}")
            self.cleanup()

    def create_menu(self):
        # Create menu frame with a distinct background
        menu_frame = ttk.Frame(self.main_frame, style='Menu.TFrame')
        menu_frame.pack(fill=tk.X, pady=(0, 30), padx=20)
        
        # Create a label for the menu
        menu_label = tk.Label(
            menu_frame,
            text="Select Nitnem Bani",
            font=('Arial', 18, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50',
            pady=10
        )
        menu_label.pack(side=tk.LEFT, padx=10)
        
        # Create a frame for category buttons
        category_frame = ttk.Frame(menu_frame, style='Menu.TFrame')
        category_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=20)
        
        # Create menu buttons for each category
        for category, banis in self.bani_categories.items():
            # Create category button
            category_btn = tk.Button(
                category_frame,
                text=category,
                font=('Arial', 14, 'bold'),
                bg='#3498db',
                fg='white',
                activebackground='#2980b9',
                activeforeground='white',
                relief='flat',
                bd=0,
                padx=25,
                pady=12,
                cursor='hand2',
                command=lambda c=category: self.show_category_menu(c)
            )
            category_btn.pack(side=tk.LEFT, padx=10, pady=5)
            
    def show_category_menu(self, category):
        # Create popup menu
        popup = tk.Toplevel(self.root)
        popup.title(category)
        popup.geometry("600x700")
        popup.configure(bg='#f8f9fa')
        
        # Make popup modal
        popup.transient(self.root)
        popup.grab_set()
        
        # Create frame for banis
        bani_frame = ttk.Frame(popup, style='Menu.TFrame')
        bani_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
        
        # Add category title
        title_label = tk.Label(
            bani_frame,
            text=category,
            font=('Arial', 24, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50',
            pady=20
        )
        title_label.pack()
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(bani_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(bani_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Menu.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add banis as buttons
        for bani_name, (start_ang, end_ang) in self.bani_categories[category].items():
            # Create a frame for each bani button
            bani_btn_frame = tk.Frame(scrollable_frame, bg='#f8f9fa')
            bani_btn_frame.pack(fill=tk.X, pady=8, padx=10)
            
            # Bani button
            bani_btn = tk.Button(
                bani_btn_frame,
                text=bani_name,
                font=('Arial', 14),
                bg='#2980b9',
                fg='white',
                activebackground='#3498db',
                activeforeground='white',
                relief='flat',
                bd=0,
                padx=25,
                pady=12,
                cursor='hand2',
                command=lambda b=bani_name: self.load_bani(b)
            )
            bani_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
            # Ang range label
            ang_label = tk.Label(
                bani_btn_frame,
                text=f"Ang {start_ang}-{end_ang}",
                font=('Arial', 12),
                bg='#f8f9fa',
                fg='#2c3e50',
                padx=15
            )
            ang_label.pack(side=tk.RIGHT)
            
        # Add close button
        close_btn = tk.Button(
            bani_frame,
            text="Close",
            font=('Arial', 14),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=12,
            cursor='hand2',
            command=popup.destroy
        )
        close_btn.pack(pady=(30, 0))
        
    def load_bani(self, bani_name):
        try:
            # Find the bani's ang range
            for category, banis in self.bani_categories.items():
                if bani_name in banis:
                    start_ang, end_ang = banis[bani_name]
                    self.current_ang = start_ang
                    self.load_ang()
                    messagebox.showinfo("Info", f"Loaded {bani_name} (Ang {start_ang}-{end_ang})")
                    return
            
            messagebox.showerror("Error", f"Could not find ang range for {bani_name}")
            
        except Exception as e:
            logging.error(f"Error loading bani {bani_name}: {str(e)}")
            messagebox.showerror("Error", f"Failed to load {bani_name}: {str(e)}")
            
    def create_header(self):
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Ang number display
        self.ang_label = ttk.Label(
            header_frame,
            text=f"Ang {self.current_ang}",
            style='Header.TLabel'
        )
        self.ang_label.pack(side=tk.LEFT, padx=20)
        
        # Verse counter
        self.verse_counter = ttk.Label(
            header_frame,
            text="",
            style='Header.TLabel'
        )
        self.verse_counter.pack(side=tk.RIGHT, padx=20)
        
    def create_footer(self):
        footer_frame = ttk.Frame(self.main_frame, style='Footer.TFrame')
        footer_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            footer_frame,
            variable=self.progress_var,
            maximum=100,
            style='Progress.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, pady=10, padx=20)
        
    def configure_styles(self):
        try:
            style = ttk.Style()
            
            # Configure colors and fonts
            style.configure('Main.TFrame', background='#000000')
            style.configure('Header.TFrame', background='#000000')
            style.configure('Footer.TFrame', background='#000000')
            style.configure('Menu.TFrame', background='#000000')
            
            # Header style
            style.configure('Header.TLabel',
                          font=('Arial', 16, 'bold'),
                          background='#000000',
                          foreground='#ffffff',
                          padding=5)
            
            # Gurmukhi style
            style.configure('Gurmukhi.TLabel',
                          font=('Raavi', 32, 'bold'),
                          background='#000000',
                          foreground='#ffffff',
                          padding=10)
            
            # Transliteration style
            style.configure('Transliteration.TLabel',
                          font=('Arial', 28, 'bold'),
                          background='#000000',
                          foreground='#ffffff',
                          padding=10)
            
            # Translation style
            style.configure('Translation.TLabel',
                          font=('Arial', 24, 'bold'),
                          background='#000000',
                          foreground='#ffffff',
                          padding=10)
            
            # Progress bar style
            style.configure('Progress.Horizontal.TProgressbar',
                          background='#ffffff',
                          troughcolor='#333333',
                          thickness=6)
            
        except Exception as e:
            logging.error(f"Error configuring styles: {str(e)}")
            raise
        
    def create_text_areas(self):
        try:
            # Create a centered frame for the verse
            self.verse_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
            self.verse_frame.pack(expand=True, fill=tk.BOTH, pady=10)
            
            # Create a container frame for better centering
            container_frame = ttk.Frame(self.verse_frame, style='Main.TFrame')
            container_frame.pack(expand=True, fill=tk.BOTH, padx=20)
            
            # Gurmukhi
            self.gurmukhi_label = ttk.Label(
                container_frame,
                text="",
                style='Gurmukhi.TLabel',
                wraplength=1000,
                justify=tk.CENTER,
                anchor=tk.CENTER
            )
            self.gurmukhi_label.pack(pady=10, fill=tk.X, anchor=tk.CENTER)
            
            # Transliteration
            self.transliteration_label = ttk.Label(
                container_frame,
                text="",
                style='Transliteration.TLabel',
                wraplength=1000,
                justify=tk.CENTER,
                anchor=tk.CENTER
            )
            self.transliteration_label.pack(pady=10, fill=tk.X, anchor=tk.CENTER)
            
            # Translation
            self.translation_label = ttk.Label(
                container_frame,
                text="",
                style='Translation.TLabel',
                wraplength=1000,
                justify=tk.CENTER,
                anchor=tk.CENTER
            )
            self.translation_label.pack(pady=10, fill=tk.X, anchor=tk.CENTER)
            
        except Exception as e:
            logging.error(f"Error creating text areas: {str(e)}")
            raise
            
    def create_controls(self):
        try:
            # Create control frame
            control_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
            control_frame.pack(fill=tk.X, pady=10)
            
            # Create buttons frame
            button_frame = ttk.Frame(control_frame, style='Main.TFrame')
            button_frame.pack(expand=True, anchor=tk.CENTER)
            
            # Previous button
            self.prev_button = tk.Button(
                button_frame,
                text="⏮️ Previous",
                font=('Arial', 20, 'bold'),
                bg='#ffffff',
                fg='#000000',
                activebackground='#cccccc',
                activeforeground='#000000',
                relief='flat',
                bd=0,
                padx=30,
                pady=15,
                cursor='hand2',
                command=self.previous_verse
            )
            self.prev_button.pack(side=tk.LEFT, padx=20)
            
            # Pause/Resume button
            self.pause_button = tk.Button(
                button_frame,
                text="⏸️ Pause",
                font=('Arial', 20, 'bold'),
                bg='#ffffff',
                fg='#000000',
                activebackground='#cccccc',
                activeforeground='#000000',
                relief='flat',
                bd=0,
                padx=30,
                pady=15,
                cursor='hand2',
                command=self.toggle_pause
            )
            self.pause_button.pack(side=tk.LEFT, padx=20)
            
            # Next button
            self.next_button = tk.Button(
                button_frame,
                text="⏭️ Next",
                font=('Arial', 20, 'bold'),
                bg='#ffffff',
                fg='#000000',
                activebackground='#cccccc',
                activeforeground='#000000',
                relief='flat',
                bd=0,
                padx=30,
                pady=15,
                cursor='hand2',
                command=self.next_verse
            )
            self.next_button.pack(side=tk.LEFT, padx=20)
            
        except Exception as e:
            logging.error(f"Error creating controls: {str(e)}")
            raise
        
    def load_ang(self):
        try:
            logging.info(f"Loading ang {self.current_ang}")
            ang_data = banidb.angs(self.current_ang)
            
            if not ang_data or 'page' not in ang_data:
                raise Exception(f"No data found for ang {self.current_ang}")
            
            # Update header
            self.ang_label.config(text=f"Ang {self.current_ang}")
            
            # Clear current verses
            self.current_ang_verses = []
            
            # Process each verse
            for verse in ang_data['page']:
                try:
                    if 'shabad_id' not in verse:
                        logging.warning(f"Missing shabad_id in verse: {verse}")
                        continue
                        
                    # Get the shabad data for translation
                    shabad_data = banidb.shabad(verse['shabad_id'])
                    
                    if not shabad_data:
                        logging.warning(f"No shabad data found for shabad_id: {verse['shabad_id']}")
                        continue
                    
                    # Get the transliteration and translation for each line
                    if 'verses' in shabad_data:
                        for verse_data in shabad_data['verses']:
                            # Get Gurmukhi text
                            gurmukhi = str(verse_data.get('verse', '')).strip()
                            
                            # Get English transliteration
                            transliteration = ""
                            if 'transliteration' in verse_data:
                                if isinstance(verse_data['transliteration'], dict):
                                    transliteration = str(verse_data['transliteration'].get('en', '')).strip()
                                else:
                                    transliteration = str(verse_data['transliteration']).strip()
                            
                            # Get English translation
                            translation = ""
                            if 'steek' in verse_data and 'en' in verse_data['steek']:
                                translation = str(verse_data['steek']['en'].get('bdb', '')).strip()
                            
                            if gurmukhi and transliteration and translation:
                                self.current_ang_verses.append({
                                    'gurmukhi': gurmukhi,
                                    'transliteration': transliteration,
                                    'translation': translation
                                })
                except Exception as e:
                    logging.error(f"Error processing verse: {str(e)}")
                    continue
            
            if not self.current_ang_verses:
                raise Exception(f"No valid verses found in ang {self.current_ang}")
            
            # Reset verse index and display first verse
            self.current_verse_index = 0
            self.display_current_verse()
            
        except Exception as e:
            logging.error(f"Error loading ang {self.current_ang}: {str(e)}")
            messagebox.showerror("Error", f"Failed to load ang {self.current_ang}: {str(e)}")
            
    def display_current_verse(self):
        try:
            if self.current_verse_index < len(self.current_ang_verses):
                verse = self.current_ang_verses[self.current_verse_index]
                
                # Update Gurmukhi
                gurmukhi_text = verse.get('gurmukhi', '')
                self.gurmukhi_label.config(text=str(gurmukhi_text).strip())
                
                # Update transliteration
                transliteration_text = verse.get('transliteration', '')
                self.transliteration_label.config(text=str(transliteration_text).strip())
                
                # Update translation
                translation_text = verse.get('translation', '')
                self.translation_label.config(text=str(translation_text).strip())
                
                # Update line counter
                self.verse_counter.config(
                    text=f"Line {self.current_verse_index + 1} of {len(self.current_ang_verses)}"
                )
                
                # Update progress bar
                progress = (self.current_verse_index + 1) / len(self.current_ang_verses) * 100
                self.progress_var.set(progress)
                
                # Schedule next verse display if not paused
                if not self.is_paused:
                    if self.auto_switch_timer:
                        self.root.after_cancel(self.auto_switch_timer)
                    self.auto_switch_timer = self.root.after(5000, self.next_verse)
                
        except Exception as e:
            logging.error(f"Error displaying verse: {str(e)}")
            messagebox.showerror("Error", f"Failed to display verse: {str(e)}")
            
    def start_auto_switch(self):
        if not self.is_paused:
            self.auto_switch_timer = self.root.after(5000, self.next_verse)
            
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="▶️ Resume")
            if self.auto_switch_timer:
                self.root.after_cancel(self.auto_switch_timer)
                self.auto_switch_timer = None
        else:
            self.pause_button.config(text="⏸️ Pause")
            self.display_current_verse()
        
    def previous_verse(self):
        if self.current_verse_index > 0:
            self.current_verse_index -= 1
            self.display_current_verse()
        elif self.current_ang > 1:
            self.current_ang -= 1
            self.load_ang()
            self.current_verse_index = len(self.current_ang_verses) - 1
            self.display_current_verse()
            
    def next_verse(self):
        try:
            if self.current_verse_index < len(self.current_ang_verses) - 1:
                self.current_verse_index += 1
                self.display_current_verse()
            elif self.current_ang < self.total_angs:
                self.current_ang += 1
                self.load_ang()
            else:
                self.current_ang = 1
                self.load_ang()
        except Exception as e:
            logging.error(f"Error in next_verse: {str(e)}")
            messagebox.showerror("Error", f"Failed to move to next verse: {str(e)}")
            
    def cleanup(self):
        try:
            if self.auto_switch_timer:
                self.root.after_cancel(self.auto_switch_timer)
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
            sys.exit(1)

def main():
    try:
        root = tk.Tk()
        app = GurbaniViewer(root)
        
        # Handle keyboard interrupt
        def signal_handler(signum, frame):
            try:
                app.cleanup()
            except Exception as e:
                logging.error(f"Error in signal handler: {str(e)}")
                sys.exit(1)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        root.mainloop()
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        messagebox.showerror("Error", f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        try:
            if 'root' in locals():
                root.destroy()
        except Exception as e:
            logging.error(f"Error in final cleanup: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main() 