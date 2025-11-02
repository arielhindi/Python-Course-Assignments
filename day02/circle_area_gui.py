import tkinter as tk
from tkinter import ttk, messagebox

from circle_area import circle_area


class CircleAreaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Circle Area Calculator")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Circle Area Calculator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Radius input
        ttk.Label(main_frame, text="Radius:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.radius_entry = ttk.Entry(main_frame, font=("Arial", 12), width=15)
        self.radius_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
    
        
        # Calculate button
        self.calculate_btn = ttk.Button(main_frame, text="Calculate Area", 
                                       command=self.calculate_area)
        self.calculate_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Result display
        ttk.Label(main_frame, text="Result:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 12), 
                                     foreground="blue", background="lightgray", 
                                     relief="sunken", padding=5)
        self.result_label.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Clear button
        self.clear_btn = ttk.Button(main_frame, text="Clear", command=self.clear_fields)
        self.clear_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Bind Enter key to calculate
        root.bind('<Return>', lambda event: self.calculate_area())
        
        # Focus on base entry
        self.radius_entry.focus()
    
    def calculate_area(self):
        """Calculate and display the circle area"""
        try:
            # Get values from entries
            radius_str = self.radius_entry.get().strip()

            # Check if fields are empty
            if not radius_str:
                messagebox.showerror("Error", "Please enter a radius value.")
                return
            
            # Convert to float
            radius = float(radius_str)
        
            
            # Check for negative values
            if radius <= 0:
                messagebox.showerror("Error", "Radius must be a positive number.")
                return
            
            # Calculate area
            area = circle_area(radius)
            
            # Display result
            self.result_label.config(text=f"{area:.2f}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for radius.")
    
    def clear_fields(self):
        """Clear all input fields and result"""
        self.radius_entry.delete(0, tk.END)
        self.result_label.config(text="")


def main():
    # Create the main window
    root = tk.Tk()
    
    # Create the application
    app = CircleAreaGUI(root)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()