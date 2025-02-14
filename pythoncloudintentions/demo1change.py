import tkinter as tk
from tkinter import Canvas
import time

# Dictionary of Objects with their receiving and reflecting intentions
objects = {
    "cloud": {
        "receives": "change_cloud_color",
        "reflects": "cloud_color_changed",
        "image": "☁️"  # Using emoji for simplicity
    },
    "mood": {
        "receives": "express_mood",
        "reflects": "mood_expressed",
        "image": "😊"
    }
}

# Dictionary of Design Nodes (functions) with their intentions
design_nodes = {
    "color_processor": {
        "receives": "cloud_color_changed",
        "emits": "express_mood",
        "function": lambda color: "happy" if color == "blue" else "neutral"
    },
    "mood_processor": {
        "receives": "mood_expressed",
        "emits": "change_cloud_color",
        "function": lambda mood: "blue" if mood == "happy" else "gray"
    }
}

class IntentionFlowDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Intention Flow Demo")
        self.root.geometry("400x400")
        
        # Create canvas for cloud
        self.canvas = Canvas(self.root, width=400, height=300)
        self.canvas.pack(pady=20)
        
        # Create cloud shape
        self.cloud = self.canvas.create_oval(150, 100, 250, 180, fill="gray")
        
        # Create labels for tracking intentions
        self.intention_label = tk.Label(self.root, text="Current Intention: None")
        self.intention_label.pack()
        
        self.object_label = tk.Label(self.root, text="Current Object: None")
        self.object_label.pack()
        
        # Initialize state
        self.current_color = "gray"
        self.current_mood = "neutral"
        
        # Start the interaction loop
        self.root.after(1000, self.simulate_intention_flow)

    def update_labels(self, intention, object_name):
        self.intention_label.config(text=f"Current Intention: {intention}")
        self.object_label.config(text=f"Current Object: {object_name}")

    def simulate_intention_flow(self):
        # Simulate human initiating intention
        self.emit_intention("change_cloud_color", "blue")
        self.root.after(2000, self.continue_flow)

    def emit_intention(self, intention, value):
        # Find object that receives this intention
        for obj_name, obj in objects.items():
            if obj["receives"] == intention:
                self.update_labels(intention, obj_name)
                
                # Simulate object reflecting intention
                if obj_name == "cloud":
                    self.canvas.itemconfig(self.cloud, fill=value)
                    self.current_color = value
                    
                # Find design node that receives reflected intention
                reflected_intention = obj["reflects"]
                self.process_design_node(reflected_intention, value)

    def process_design_node(self, intention, value):
        # Find design node that handles this intention
        for node_name, node in design_nodes.items():
            if node["receives"] == intention:
                # Process the value through the design node
                result = node["function"](value)
                # Emit new intention
                self.root.after(1000, lambda: self.emit_intention(node["emits"], result))

    def continue_flow(self):
        # Toggle cloud color
        new_color = "gray" if self.current_color == "blue" else "blue"
        self.emit_intention("change_cloud_color", new_color)
        self.root.after(2000, self.continue_flow)

    def run(self):
        self.root.mainloop()

# Create and run the demo
demo = IntentionFlowDemo()
demo.run()