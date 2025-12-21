import simpy
import random
from flask import Flask, render_template_string

# --- Energy Grid Simulation ---
class EnergyGrid:
    def __init__(self, env):
        self.env = env
        self.power_generated = 0
        self.power_consumed = 0
        self.grid_stable = True
        self.alerts = []

    def generate_power(self, amount):
        self.power_generated += amount
        self.alerts.append(f"Generated {amount} MW at {self.env.now}")

    def consume_power(self, amount):
        if self.power_generated >= amount:
            self.power_generated -= amount
            self.power_consumed += amount
            self.alerts.append(f"Consumed {amount} MW at {self.env.now}")
        else:
            self.alerts.append(f"Grid overload! Demand exceeds supply at {self.env.now}")
            self.grid_stable = False

# --- Guardian Network ---
class LifeSafetyGuardian:
    def check_action(self, action, grid):
        if action == "overload":
            grid.alerts.append("Life Safety Guardian: VETO - Action would overload the grid!")
            return False
        return True

class HumanOversightGuardian:
    def check_action(self, action, grid):
        if action == "critical_adjustment":
            grid.alerts.append("Human Oversight Guardian: Approval required for critical adjustment.")
            # Simulate human approval via dashboard
            return True  # Assume approval for simulation
        return True

class ConsensusEngine:
    def __init__(self):
        self.guardians = [LifeSafetyGuardian(), HumanOversightGuardian()]

    def request_approval(self, action, grid):
        for guardian in self.guardians:
            if not guardian.check_action(action, grid):
                return False
        return True

# --- Simulation Process ---
def run_simulation(env, grid, consensus_engine):
    while True:
        # Simulate power generation
        grid.generate_power(100)
        yield env.timeout(5)

        # Simulate normal consumption
        if consensus_engine.request_approval("consume", grid):
            grid.consume_power(80)
        yield env.timeout(5)

        # Simulate a sudden demand spike
        if consensus_engine.request_approval("overload", grid):
            grid.consume_power(150)
        yield env.timeout(10)

# --- Flask Dashboard ---
app = Flask(__name__)

def get_grid_status():
    env = simpy.Environment()
    grid = EnergyGrid(env)
    consensus_engine = ConsensusEngine()
    env.process(run_simulation(env, grid, consensus_engine))
    env.run(until=30)
    return grid

 @app.route("/")
def dashboard():
    grid = get_grid_status()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Guardian OS Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .status { font-weight: bold; color: {{ "green" if grid.grid_stable else "red" }}; }
                .alerts { background: #f0f0f0; padding: 10px; margin-top: 10px; }
            </style>
        </head>
        <body>
            <h1>Guardian OS Dashboard</h1>
            <p>Grid Status: <span class="status">{{ "Stable" if grid.grid_stable else "Unstable" }}</span></p>
            <p>Power Generated: {{ grid.power_generated }} MW</p>
            <p>Power Consumed: {{ grid.power_consumed }} MW</p>
            <div class="alerts">
                <h3>Alerts:</h3>
                <ul>
                    {% for alert in grid.alerts %}
                        <li>{{ alert }}</li>
                    {% endfor %}
                </ul>
            </div>
        </body>
        </html>
    ''', grid=grid)

if __name__ == "__main__":
    app.run(debug=True, port=5000)