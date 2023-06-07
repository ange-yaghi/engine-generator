
import engine_generator
import re

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
    
    return left_bank + right_bank, left_bank, right_bank

def generate_inline(cylinderCount):
    print("Generating inline style engine...")
    cylinders = generate_firing_order_inline(cylinderCount)
    cylinders0 = []

    for i in range(1, cylinderCount + 1):
        cylinders0.append(i)
    
    bank = engine_generator.Bank(cylinders0, 0)
    engine = engine_generator.Engine([bank], cylinders)
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

def generate_v(cylinderCount):
    print("Generating V style engine...")

def generate_custom_engine():
    print("Generating custom engine...")
    print("Engine Styles:\n   - Inline\n   - V")
    style = input("Enter style: ")
    if style.lower() != "inline" or style.lower() != "v":
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
        generate_inline(cylinderCount)
    elif style.lower() == "v":
        generate_v(cylinderCount)

def generate_v24():
    cylinders0 = []
    cylinders1 = []
    cylinders = []

    for i in range(12):
        cylinders0.append(i * 2)
        cylinders1.append(i * 2 + 1)
        cylinders += [i * 2, i * 2 + 1]

    b0 = engine_generator.Bank(cylinders0, -45)
    b1 = engine_generator.Bank(cylinders1, 45)
    engine = engine_generator.Engine([b0, b1], cylinders)
    engine.engine_name = "V24"
    engine.starter_torque = 400
    engine.crank_mass = 200

    engine.generate()
    engine.write_to_file("test.mr")

def generate_v69():
    cylinders0 = []
    cylinders1 = []
    cylinders = []

    for i in range(34):
        cylinders0.append(i * 2)
        cylinders1.append(i * 2 + 1)
        cylinders += [i * 2, i * 2 + 1]

    cylinders0.append(68)
    cylinders.append(68)

    b0 = engine_generator.Bank(cylinders0, -34.5)
    b1 = engine_generator.Bank(cylinders1, 34.5)
    b1.flip = True
    engine = engine_generator.Engine([b0, b1], cylinders)
    engine.engine_name = "V69"
    engine.starter_torque = 10000
    engine.crank_mass = 2000
    engine.bore = 197.9
    engine.stroke = 197.9
    engine.chamber_volume = 3000
    engine.rod_length = engine.stroke * 1.75
    engine.simulation_frequency = 1200
    engine.max_sle_solver_steps = 4
    engine.fluid_simulation_steps = 4
    engine.idle_throttle_plate_position = 0.9

    engine.generate()
    engine.write_to_file("v69_engine.mr")

if __name__ == "__main__":
    generate_i4()
