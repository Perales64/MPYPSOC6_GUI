import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import os
import re
import webbrowser

class MicroPythonPSoC6GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroPython PSoC6 - Device Setup")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Configure style
        self.setup_styles()
        
        # Variables
        self.action_var = tk.StringVar(value="device-setup")
        self.board_var = tk.StringVar()
        self.version_var = tk.StringVar(value="latest")
        self.serial_var = tk.StringVar()
        self.kitprog_var = tk.BooleanVar()
        self.quiet_var = tk.BooleanVar()
        self.hex_file_var = tk.StringVar()

        # Create interface
        self.create_widgets()

        # Configure resizing behavior
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def setup_styles(self):
        """Configure interface styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       font=('Helvetica', 16, 'bold'),
                       foreground='#4F46E5')
        
        style.configure('Subtitle.TLabel',
                       font=('Helvetica', 10),
                       foreground='#6B7280')
        
        style.configure('Section.TLabel',
                       font=('Helvetica', 11, 'bold'),
                       foreground='#374151')
        
        style.configure('Info.TLabel',
                       font=('Helvetica', 9),
                       foreground='#6B7280')
        
        style.configure('Generate.TButton',
                       font=('Helvetica', 11, 'bold'),
                       padding=10)
        
        style.configure('Link.TLabel',
                       font=('Helvetica', 10, 'underline'),
                       foreground='blue')
        
    def create_widgets(self):
        """Create all interface widgets"""
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Header (spans both columns)
        self.create_header(main_frame)

        # Left frame - LOG
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Right frame - CONFIGURATION
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Create left side content (LOG)
        self.create_output_section(left_frame)

        # Create right side content (CONFIGURATION)
        # Action Selection
        self.create_action_selection(right_frame)

        # Configuration
        self.config_frame = ttk.LabelFrame(right_frame, text="Configuration", padding="15")
        self.config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=10)
        self.config_frame.grid_columnconfigure(0, weight=1)

        # Dynamic frames for options
        self.create_device_setup_options(self.config_frame)
        self.create_device_erase_options(self.config_frame)
        self.create_firmware_deploy_options(self.config_frame)

        # Buttons
        self.create_buttons_section(right_frame)

        self.update_options_visibility()

    def create_header(self, parent):
        """Create the header"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="🔧 MicroPython PSoC6",
                 style='Title.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(header_frame,
                 text="Command generator for terminal",
                 style='Subtitle.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        link_label = ttk.Label(header_frame,
                               text="Hackster.io Tutorial",
                               style='Link.TLabel',
                               cursor="hand2")
        link_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.hackster.io/Infineon_Team/micropython-on-psoc-fcf1d0"))

    def create_action_selection(self, parent):
        action_frame = ttk.LabelFrame(parent, text="Action", padding="15")
        action_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        actions = [
            ("Device Setup", "device-setup"),
            ("Device Erase", "device-erase"),
            ("Firmware Deploy", "firmware-deploy")
        ]

        for i, (text, value) in enumerate(actions):
            ttk.Radiobutton(action_frame, text=text, variable=self.action_var, value=value,
                            command=self.update_options_visibility).grid(row=0, column=i, padx=10, sticky=tk.W)

    def create_device_setup_options(self, parent):
        self.setup_options_frame = ttk.Frame(parent)
        self.setup_options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.setup_options_frame.grid_columnconfigure(0, weight=1)
        self.create_common_options(self.setup_options_frame)

        # Version
        ttk.Label(self.setup_options_frame, text="Firmware Version:",
                    style='Section.TLabel').grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(self.setup_options_frame, textvariable=self.version_var,
                    width=42).grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(self.setup_options_frame,
                    text='Leave as "latest" for the most recent version',
                    style='Info.TLabel').grid(row=8, column=0, sticky=tk.W, pady=(0, 15))
        # Checkboxes
        ttk.Checkbutton(self.setup_options_frame,
                        text="Update Kitprog3 debugger firmware",
                        variable=self.kitprog_var).grid(row=9, column=0, sticky=tk.W, pady=5)

    def create_device_erase_options(self, parent):
        self.erase_options_frame = ttk.Frame(parent)
        self.erase_options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.erase_options_frame.grid_columnconfigure(0, weight=1)
        self.create_common_options(self.erase_options_frame, require_board=True)

    def create_firmware_deploy_options(self, parent):
        self.deploy_options_frame = ttk.Frame(parent)
        self.deploy_options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.deploy_options_frame.grid_columnconfigure(0, weight=1)
        self.create_common_options(self.deploy_options_frame, require_board=True)

        # File selector
        ttk.Label(self.deploy_options_frame, text=".hex File:",
                    style='Section.TLabel').grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        hex_file_frame = ttk.Frame(self.deploy_options_frame)
        hex_file_frame.grid(row=7, column=0, sticky=(tk.W, tk.E))
        hex_file_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Entry(hex_file_frame, textvariable=self.hex_file_var,
                    width=30).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(hex_file_frame, text="Browse...",
                    command=self.browse_hex_file).grid(row=0, column=1, padx=5)

    def create_common_options(self, parent, require_board=False):
        # Configure columns for expansion
        parent.grid_columnconfigure(0, weight=1)
        
        # Board
        ttk.Label(parent, text="PSoC6 Board:",
                    style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        boards = [
            "CY8CPROTO-062-4343W",
            "CY8CPROTO-063-BLE",
            "CY8CKIT-062S2-AI"
        ]
        if not require_board:
            boards.insert(0, "Select at runtime")

        board_combo = ttk.Combobox(parent, textvariable=self.board_var,
                                    values=boards, state='readonly', width=40)
        board_combo.current(0)
        board_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        if not require_board:
            ttk.Label(parent,
                        text="If you do not select a board, the script will ask you to choose during execution",
                        style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 15))

        # Serial number
        ttk.Label(parent, text="Adapter Serial Number (optional):",
                    style='Section.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(parent, textvariable=self.serial_var,
                    width=42).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(parent,
                    text="Only necessary if you have multiple boards connected",
                    style='Info.TLabel').grid(row=5, column=0, sticky=tk.W, pady=(0, 15))
        
        # Silent Mode Checkbox (common to all)
        ttk.Checkbutton(parent,
                       text="Silent mode (no confirmations)",
                       variable=self.quiet_var).grid(row=10, column=0, sticky=tk.W, pady=5)

    def browse_hex_file(self):
        filename = filedialog.askopenfilename(
            title="Select .hex file",
            filetypes=(("Hex files", "*.hex"), ("All files", "*.*"))
        )
        if filename:
            self.hex_file_var.set(filename)

    def update_options_visibility(self):
        action = self.action_var.get()
        
        self.setup_options_frame.grid_remove()
        self.erase_options_frame.grid_remove()
        self.deploy_options_frame.grid_remove()

        if action == "device-setup":
            self.setup_options_frame.grid()
        elif action == "device-erase":
            self.erase_options_frame.grid()
        elif action == "firmware-deploy":
            self.deploy_options_frame.grid()

    def create_buttons_section(self, parent):
        """Create the buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, pady=(15, 0), sticky=(tk.S))
        
        ttk.Button(button_frame, text="Execute Now",
                  command=self.execute_command,
                  style='Generate.TButton').grid(row=0, column=0, padx=5, pady=5)
    
    def create_output_section(self, parent):
        """Create the output section"""
        output_frame = ttk.LabelFrame(parent, text="Execution Log", padding="15")
        output_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        # Text widget for the log
        self.log_text = tk.Text(output_frame, height=15,
                                wrap=tk.WORD, bg='#1F2937', fg='#E5E7EB',
                                font=('Courier', 10), relief=tk.FLAT, padx=10, pady=10)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.config(state=tk.DISABLED)

        # Scrollbar
        scrollbar = ttk.Scrollbar(output_frame, orient='vertical',
                                    command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set

    def update_log(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    # --- Validation Functions ---
    def validate_script_exists(self):
        """Validate that the main script exists"""
        if not os.path.exists('mpy-psoc6.py'):
            messagebox.showerror("File Error", 
                                 "The script 'mpy-psoc6.py' was not found.\n\n"
                                 "Make sure this GUI is running in the same "
                                 "directory as the main script.")
            return False
        return True

    def validate_serial(self, serial):
        """Serial number validation (hexadecimal format)"""
        if serial and not re.match(r'^[A-F0-9]+$', serial.upper()):
            messagebox.showerror("Validation Error",
                                 "The provided serial number is not valid.\n\n"
                                 "It must contain only hexadecimal characters (0-9 and A-F).")
            return False
        return True

    def generate_command(self):
        """Generate the command according to the configuration"""
        action = self.action_var.get()
        cmd = f"python mpy-psoc6.py {action}"

        board = self.board_var.get()
        if board and board != "Select at runtime":
            cmd += f" -b \"{board}\""

        serial = self.serial_var.get().strip()
        if serial:
            if not self.validate_serial(serial):
                return None
            cmd += f" -n {serial}"

        if self.quiet_var.get():
            cmd += " -q"

        if action == "device-setup":
            version = self.version_var.get()
            if version and version != "latest":
                cmd += f" -v {version}"
            if self.kitprog_var.get():
                cmd += " --kitprog-fw-update"
        elif action == "firmware-deploy":
            hex_file = self.hex_file_var.get()
            if not hex_file:
                messagebox.showerror("Error", "Please select a .hex file to deploy.")
                return None
            cmd += f" -f \"{hex_file}\""
        
        return cmd

    def execute_command(self):
        """Execute the command directly"""
        if not self.validate_script_exists():
            return

        cmd = self.generate_command()
        if not cmd:
            return

        self.clear_log()
        self.update_log(f"Executing command:\n\n$ {cmd}\n\n")
        self.update_log("="*60 + "\n\n")

        thread = threading.Thread(target=self.run_subprocess, args=(cmd,))
        thread.daemon = True
        thread.start()

    def run_subprocess(self, cmd):
        """
        Executes the command in a new terminal window to allow
        user interaction (e.g., to enter sudo passwords).
        """
        # Command to keep the terminal open after execution
        prompt_message = "Process finished. Press Enter to close this window."
        full_cmd = f'{cmd}; read -p "{prompt_message}"'
        
        try:
            # Try with gnome-terminal, common on Debian/Ubuntu based systems (like Linux Mint)
            terminal_cmd = ['gnome-terminal', '--', 'bash', '-c', full_cmd]
            subprocess.Popen(terminal_cmd)
            self.update_log("A new terminal window has been opened to execute the command.\n"
                              "Please interact with it to enter the sudo password or any other required information.\n")
        except FileNotFoundError:
            try:
                # Fallback to xterm if gnome-terminal is not available
                escaped_cmd = full_cmd.replace('"', '\\"')
                terminal_cmd = ['xterm', '-e', f'bash -c "{escaped_cmd}"']
                subprocess.Popen(terminal_cmd)
                self.update_log("A new terminal window (xterm) has been opened to execute the command.\n"
                                  "Please interact with it to enter the sudo password or any other required information.\n")
            except FileNotFoundError:
                self.update_log("Error: Could not find a compatible terminal emulator (gnome-terminal, xterm).\n"
                                  "Cannot execute the command interactively.\n\n"
                                  "SUGGESTION: Try checking the 'Silent mode' option and running again if no password is required.\n")
            except Exception as e:
                self.update_log(f"Error trying to open xterm:\n{str(e)}\n")
        except Exception as e:
            self.update_log(f"Error trying to open gnome-terminal:\n{str(e)}\n")


def main():
    root = tk.Tk()
    MicroPythonPSoC6GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
