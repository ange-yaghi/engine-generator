
import engine_generator
import re

import engine_generator

class Fuel_Type:
    fuel_types = {
        "regular": engine_generator.gasoline_regular,
        "midgrade": engine_generator.gasoline_midgrade,
        "premium": engine_generator.gasoline_premium,
        "hexane": engine_generator.hexane,
        "high octane": engine_generator.high_octane,
        "pure octane": engine_generator.pure_octane,
        "hydrogen": engine_generator.hydrogen,
        "oxygen": engine_generator.oxygen,
        "hydrogen oxygen": engine_generator.hydrogen_oxygen,
        "hydrazine": engine_generator.hydrazine,
        "ethanol": engine_generator.ethanol,
        "isopropyl alcohol": engine_generator.isopropyl_alcohol,
        "butyl alcohol": engine_generator.butyl_alcohol,
        "kerosene": engine_generator.kerosene,
        "nos": engine_generator.nos,
        "nos octane": engine_generator.nos_octane,
        "diesel": engine_generator.diesel
    }

    @staticmethod
    def getFuelType(fuel_type):
        fuel_type = fuel_type.lower()
        if fuel_type in Fuel_Type.fuel_types:
            return Fuel_Type.fuel_types[fuel_type]
        else:
            print(f"{fuel_type} is an invalid fuel type")

    @staticmethod
    def printAvailableFuelTypes():
        print("Available fuel types:")
        for fuel_type in Fuel_Type.fuel_types:
            print(f"- {fuel_type.capitalize()}")


def strip_special_characters(string):
    # Replace spaces and special characters with underscores
    stripped_string = re.sub(r'\W+', '_', string.replace(' ', '_'))

    return stripped_string

def generate_firing_order_inline(cylinders):
    if cylinders < 2:
        return "Invalid number of cylinders. Minimum of 2 cylinders required."

    if cylinders % 2 != 0:
        firing_order = [1]
        for i in range(3, cylinders + 1, 2):
            firing_order.append(i)
        firing_order.append(2)
    else:
        adjusted_cylinders = cylinders - 1
        firing_order = [2]
        for i in range(4, adjusted_cylinders + 1, 2):
            firing_order.insert(0, i)
        firing_order.append(1)
        firing_order.append(cylinders)

    return firing_order

def generate_firing_order_v(cylinders):
    if cylinders < 4:
        return "Invalid number of cylinders. Minimum of 4 cylinders required."

    left_bank = []
    right_bank = []
    for i in range(1, cylinders + 1):
        if i % 2 == 0:
            right_bank.append(i)
        else:
            left_bank.append(i)

    extra_cylinders = cylinders % 2
    if extra_cylinders == 1:
        if len(left_bank) > len(right_bank):
            right_bank.append(cylinders)
        else:
            left_bank.append(cylinders)
    
    return left_bank + right_bank, left_bank, right_bank

def generate_inline(cylinderCount, fuel_type):
    print("Generating inline style engine...")
    cylinders = generate_firing_order_inline(cylinderCount)
    cylinders0 = []

    for i in range(1, cylinderCount + 1):
        cylinders0.append(i)
    
    bank = engine_generator.Bank(cylinders0, 0)
    engine = engine_generator.Engine([bank], cylinders, fuel_type)
    engine.engine_name = input("Engine name: ")
    engine.starter_torque = int(input("Starter torque: "))
    engine.crank_mass = int(input("Crank mass: "))
    engine.bore = float(input("Cylinder bore: "))
    engine.stroke = float(input("Cylinder stroke: "))
    engine.chamber_volume = int(input("Chamber volume: "))
    engine.rod_length = float(input("Cylinder rod length: "))
    engine.simulation_frequency = int(input("Simulation frequency (default 1200): "))
    engine.max_sle_solver_steps = int(input("Max sle solver steps (default 4): "))
    engine.fluid_simulation_steps = int(input("Fluid simulation steps (default 4): "))
    engine.idle_throttle_plate_position = float(input("Idle throttle plate position: "))

    engine.generate()
    engine.write_to_file(strip_special_characters(engine.engine_name) + ".mr")

def generate_v(cylinderCount, fuel_type):
    print("Generating V style engine...")
    cylinders, cylinders0, cylinders1 = generate_firing_order_v(cylinderCount)

    bank0 = engine_generator.Bank(cylinders0, -45)
    bank1 = engine_generator.Bank(cylinders1, 45)

    engine = engine_generator.Engine([bank0, bank1], cylinders, fuel_type)
    
    engine.engine_name = input("Engine name: ")
    engine.starter_torque = int(input("Starter torque: "))
    engine.crank_mass = int(input("Crank mass: "))
    engine.bore = float(input("Cylinder bore: "))
    engine.stroke = float(input("Cylinder stroke: "))
    engine.chamber_volume = int(input("Chamber volume: "))
    engine.rod_length = float(input("Cylinder rod length: "))
    engine.simulation_frequency = int(input("Simulation frequency (default 1200): "))
    engine.max_sle_solver_steps = int(input("Max sle solver steps (default 4): "))
    engine.fluid_simulation_steps = int(input("Fluid simulation steps (default 4): "))
    engine.idle_throttle_plate_position = float(input("Idle throttle plate position: "))

    engine.generate()
    engine.write_to_file(strip_special_characters(engine.engine_name) + ".mr")

def generate_custom_engine():
    print("Generating custom engine...")

    Fuel_Type.printAvailableFuelTypes()
    fuel_type = Fuel_Type.getFuelType(input("Fuel type: "))

    print("Engine Styles:\n   - Inline\n   - V")
    style = input("Enter style: ")
    if style.lower() != "inline" and style.lower() != "v":
        print("Invalid style. Must either be inline or v.")
        return
    cylinderCount = int(input("Enter cylinder count: "))
    if cylinderCount < 2:
        print("Invalid cylinders, must be greater than 1 for inline style.")
        return
    if cylinderCount < 4 and style.lower() == "v":
        print("Invalid cylinders, must be greater than 3 for V style.")
        return
    if style.lower() == "inline":
        generate_inline(cylinderCount, fuel_type)
    elif style.lower() == "v":
        generate_v(cylinderCount, fuel_type)

if __name__ == "__main__":
    generate_custom_engine()
