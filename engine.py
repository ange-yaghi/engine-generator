
import engine_generator

def generate_i4():
    cylinders0 = []
    cylinders = [0,2,3,1]

    for i in range(4):
        cylinders0.append(i)

    bank = engine_generator.Bank(cylinders0, 0)
    engine = engine_generator.Engine([bank], cylinders)
    engine.engine_name = "I4"
    engine.starter_torque = 400
    engine.chamber_volume = 70

    engine.generate()
    engine.write_to_file("i4.mr")


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
