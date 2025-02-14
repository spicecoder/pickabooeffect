import tkinter as tk
from tkinter import Canvas, Button
import random
import time

# Dictionary of all intention strings with their types and sequence numbers
intentions = {
    "act_now": {
        "sequence": 1,
        "type": "AFFIRMATIVE",
        "string": "act_now",
        "description": "User initiates weather check"
    },
    "check_weather": {
        "sequence": 2,
        "type": "DIRECTIVE",
        "string": "check_weather",
        "description": "Request weather forecast"
    },
    "potential_storm": {
        "sequence": 3,
        "type": "PROACTIVE",
        "string": "potential_storm",
        "description": "Storm possibility detected"
    },
    "potential_flood": {
        "sequence": 3,
        "type": "PROACTIVE",
        "string": "potential_flood",
        "description": "Flood possibility detected"
    },
    "analyze_storm": {
        "sequence": 4,
        "type": "DIRECTIVE",
        "string": "analyze_storm",
        "description": "Analyze storm conditions"
    },
    "analyze_flood": {
        "sequence": 4,
        "type": "DIRECTIVE",
        "string": "analyze_flood",
        "description": "Analyze flood conditions"
    },
    "set_storm_state": {
        "sequence": 5,
        "type": "AFFIRMATIVE",
        "string": "set_storm_state",
        "description": "Set storm state"
    },
    "set_flood_state": {
        "sequence": 5,
        "type": "AFFIRMATIVE",
        "string": "set_flood_state",
        "description": "Set flood state"
    }
}

objects = {
    "action_button": {
        "receives": intentions["act_now"]["string"],
        "reflects": intentions["check_weather"]["string"],
        "pnr_mapping": {"action": "check"}
    },
    "storm_warning": {
        "receives": intentions["potential_storm"]["string"],
        "reflects": intentions["analyze_storm"]["string"],
        "pnr_mapping": {"intensity": "storm_level"}
    },
    "flood_warning": {
        "receives": intentions["potential_flood"]["string"],
        "reflects": intentions["analyze_flood"]["string"],
        "pnr_mapping": {"intensity": "flood_level"}
    }
}

design_nodes = {
    "weather_forecaster": {
        "receives": intentions["check_weather"]["string"],
        "emits": [intentions["potential_storm"]["string"], 
                 intentions["potential_flood"]["string"]],
        "process_pnr": lambda pnr: {"intensity": ["high" if random.random() > 0.5 else "low"]}
    },
    "storm_processor": {
        "receives": intentions["analyze_storm"]["string"],
        "emits": intentions["set_storm_state"]["string"],
        "process_pnr": lambda pnr: {
            "weather_state": ["severe_storm" if pnr.get("storm_level", ["low"])[0] == "high" else "mild_storm"]
        }
    },
    "flood_processor": {
        "receives": intentions["analyze_flood"]["string"],
        "emits": intentions["set_flood_state"]["string"],
        "process_pnr": lambda pnr: {
            "weather_state": ["severe_flood" if pnr.get("flood_level", ["low"])[0] == "high" else "mild_flood"]
        }
    }
}

class WeatherIntentionFlowDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weather Warning System")
        self.root.geometry("800x600")
        
        # Create action button
        self.action_button = Button(self.root, text="Check Weather", 
                                  command=self.start_intention_flow)
        self.action_button.pack(pady=20)
        
        # Create canvas
        self.canvas = Canvas(self.root, width=400, height=300)
        self.canvas.pack(pady=20)
        
        # Create cloud shape
        self.cloud_id = self.canvas.create_oval(150, 100, 250, 180, fill="gray")
        
        # Create labels
        self.intention_label = tk.Label(self.root, 
            text="Current Intention: None\nType: None", 
            justify=tk.LEFT, font=('Arial', 10))
        self.intention_label.pack()
        
        self.state_label = tk.Label(self.root, text="Weather State: Normal",
                                  font=('Arial', 12, 'bold'))
        self.state_label.pack()
        
        self.cpux_label = tk.Label(self.root, text="Active CPUX: None",
                                 font=('Arial', 10))
        self.cpux_label.pack()

        # Initialize state
        self.current_state = "normal"

    def start_intention_flow(self):
        """Initiates the intention flow when button is clicked"""
        self.action_button.config(state='disabled')
        cpux_type = random.choice(["Storm", "Flood"])
        self.update_labels("act_now", cpux_type)
        initial_pnr = {"action": ["check_weather"]}
        self.emit_intention("act_now", initial_pnr, cpux_type)

    def emit_intention(self, intention_key, pnr, cpux_type):
        """Emits an intention to the appropriate object"""
        intention_str = intentions[intention_key]["string"]
        self.update_labels(intention_key, cpux_type)
        
        # Handle weather forecaster node specially
        if intention_str == intentions["check_weather"]["string"]:
            next_intention = "potential_storm" if cpux_type == "Storm" else "potential_flood"
            processed_pnr = design_nodes["weather_forecaster"]["process_pnr"](pnr)
            self.root.after(1000, lambda: self.emit_intention(next_intention, processed_pnr, cpux_type))
            return

        # Process through appropriate processor
        if intention_str in [intentions["analyze_storm"]["string"], 
                           intentions["analyze_flood"]["string"]]:
            processor = "storm_processor" if cpux_type == "Storm" else "flood_processor"
            processed_pnr = design_nodes[processor]["process_pnr"](pnr)
            weather_state = processed_pnr["weather_state"][0]
            self.draw_weather_state(weather_state)
            self.update_labels(intention_key, cpux_type, weather_state)
            self.root.after(2000, lambda: self.action_button.config(state='normal'))
            return

        # Process through objects
        for obj_name, obj in objects.items():
            if obj["receives"] == intention_str:
                self.process_object(obj, intention_key, pnr, cpux_type)
                break

    def process_object(self, obj, intention_key, pnr, cpux_type):
        """Processes an intention through an object"""
        # Map PnR through object
        mapped_pnr = {}
        for in_key, out_key in obj["pnr_mapping"].items():
            if in_key in pnr:
                mapped_pnr[out_key] = pnr[in_key]

        # Get next intention and emit
        reflected_intention = obj["reflects"]
        next_intention = next(k for k, v in intentions.items() 
                            if v["string"] == reflected_intention)
        self.root.after(1000, lambda: self.emit_intention(
            next_intention, mapped_pnr, cpux_type))

    def draw_weather_state(self, state):
        """Updates the visual representation of the weather state"""
        self.canvas.delete("weather_effect")
        
        if state == "severe_storm":
            self.canvas.create_line(200, 180, 180, 230, 220, 230, 200, 280,
                                  fill="yellow", width=3, tags="weather_effect")
            self.canvas.itemconfig(self.cloud_id, fill="dark gray")
            
        elif state == "severe_flood":
            for i in range(10):
                x = random.randint(150, 250)
                self.canvas.create_line(x, 180, x, 280,
                                     fill="blue", width=2, tags="weather_effect")
            self.canvas.itemconfig(self.cloud_id, fill="navy")
            
        elif state == "mild_storm":
            self.canvas.create_line(180, 180, 220, 230,
                                  fill="yellow", width=2, tags="weather_effect")
            self.canvas.itemconfig(self.cloud_id, fill="gray")
            
        elif state == "mild_flood":
            for i in range(5):
                x = random.randint(150, 250)
                self.canvas.create_line(x, 180, x, 230,
                                     fill="light blue", width=1, tags="weather_effect")
            self.canvas.itemconfig(self.cloud_id, fill="blue")
        else:
            self.canvas.itemconfig(self.cloud_id, fill="gray")

    def update_labels(self, intention_key, cpux_type, weather_state=None):
        """Updates the UI labels with current state"""
        intention = intentions[intention_key]
        self.intention_label.config(
            text=f"Step {intention['sequence']} of 5\n" +
                 f"Current Intention: {intention['string']}\n" + 
                 f"Type: {intention['type']}\n" +
                 f"Description: {intention['description']}"
        )
        self.cpux_label.config(text=f"Active CPUX: {cpux_type}")
        if weather_state:
            self.state_label.config(text=f"Weather State: {weather_state.replace('_', ' ').title()}")

    def run(self):
        """Starts the application"""
        self.root.mainloop()

if __name__ == "__main__":
    demo = WeatherIntentionFlowDemo()
    demo.run()