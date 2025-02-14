import tkinter as tk
from tkinter import Canvas
import time

# PnR sets for each design node
pnr_sets = {
    "color_processor": {
        "flowin": {
            "mycolor": ["none"],
        },
        "flowout": {
            "mymood": ["neutral"]
        }
    },
    "mood_processor": {
        "flowin": {
            "mymood": ["neutral"]
        },
        "flowout": {
            "mycolor": ["gray"]
        }
    }
}

# Dictionary of Objects with their receiving and reflecting intentions + PnR mapping
objects = {
    "cloud": {
        "receives": "change_cloud_color",
        "reflects": "cloud_color_changed",
        "image": "☁️",
        "pnr_mapping": {
            "mycolor": "mycolor"  # Keep the same key for cloud color
        }
    },
    "mood": {
        "receives": "express_mood",
        "reflects": "mood_expressed",
        "image": "😊",
        "pnr_mapping": {
            "mymood": "mymood"  # Keep the same key for mood
        }
    }
}

# Dictionary of Design Nodes with their intentions and PnR processing
design_nodes = {
    "color_processor": {
        "receives": "cloud_color_changed",
        "emits": "express_mood",
        "function": lambda color: "happy" if color == "blue" else "neutral",
        "process_pnr": lambda pnr: {
            "mymood": ["happy"] if pnr.get("mycolor", ["gray"])[0] == "blue" else ["neutral"]
        }
    },
    "mood_processor": {
        "receives": "mood_expressed",
        "emits": "change_cloud_color",
        "function": lambda mood: "blue" if mood == "happy" else "gray",
        "process_pnr": lambda pnr: {
            "mycolor": ["blue"] if pnr.get("mymood", ["neutral"])[0] == "happy" else ["gray"]
        }
    }
}

class IntentionFlowDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Intention Flow Demo with PnR")
        self.root.geometry("500x500")
        
        # Create canvas for cloud
        self.canvas = Canvas(self.root, width=400, height=300)
        self.canvas.pack(pady=20)
        
        # Create cloud shape
        self.cloud = self.canvas.create_oval(150, 100, 250, 180, fill="gray")
        
        # Create labels for tracking intentions and PnR
        self.intention_label = tk.Label(self.root, text="Current Intention: None")
        self.intention_label.pack()
        
        self.object_label = tk.Label(self.root, text="Current Object: None")
        self.object_label.pack()
        
        self.pnr_label = tk.Label(self.root, text="Current PnR: None")
        self.pnr_label.pack()
        
        # Initialize state
        self.current_pnr = {"mycolor": ["gray"]}
        
        # Start the interaction loop
        self.root.after(1000, self.simulate_intention_flow)

    def update_labels(self, intention, object_name, pnr):
        self.intention_label.config(text=f"Current Intention: {intention}")
        self.object_label.config(text=f"Current Object: {object_name}")
        self.pnr_label.config(text=f"Current PnR: {pnr}")

    def simulate_intention_flow(self):
        # Simulate human initiating intention with PnR
        initial_pnr = {"mycolor": ["blue"]}
        self.emit_intention("change_cloud_color", initial_pnr)
        self.root.after(2000, self.continue_flow)

    def emit_intention(self, intention, pnr):
        # Find object that receives this intention
        for obj_name, obj in objects.items():
            if obj["receives"] == intention:
                # Map PnR through object
                mapped_pnr = {}
                for in_key, out_key in obj["pnr_mapping"].items():
                    if in_key in pnr:
                        mapped_pnr[out_key] = pnr[in_key]
                    else:
                        # Provide default values if key not found
                        mapped_pnr[out_key] = ["gray"] if out_key == "mycolor" else ["neutral"]
                
                self.update_labels(intention, obj_name, mapped_pnr)
                
                # Update visual state if it's the cloud object
                if obj_name == "cloud" and "mycolor" in mapped_pnr:
                    color = mapped_pnr["mycolor"][0]
                    self.canvas.itemconfig(self.cloud, fill=color)
                    self.current_pnr = mapped_pnr
                
                # Find design node that receives reflected intention
                reflected_intention = obj["reflects"]
                self.process_design_node(reflected_intention, mapped_pnr)

    def process_design_node(self, intention, pnr):
        # Find design node that handles this intention
        for node_name, node in design_nodes.items():
            if node["receives"] == intention:
                # Process the PnR through the design node
                processed_pnr = node["process_pnr"](pnr)
                # Emit new intention with processed PnR
                self.root.after(1000, lambda: self.emit_intention(node["emits"], processed_pnr))

    def continue_flow(self):
        # Toggle cloud color through PnR
        new_color = "gray" if self.current_pnr["mycolor"][0] == "blue" else "blue"
        new_pnr = {"mycolor": [new_color]}
        self.emit_intention("change_cloud_color", new_pnr)
        self.root.after(2000, self.continue_flow)

    def run(self):
        self.root.mainloop()

# Create and run the demo
if __name__ == "__main__":
    demo = IntentionFlowDemo()
    demo.run()