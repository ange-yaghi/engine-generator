
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

if __name__ == "__main__":
    generate_i4()
