import random

class Camshaft:
    def __init__(self):
        self.lobes = []

class Bank:
    def __init__(self, cylinder_numbers, bank_angle):
        self.cylinders = cylinder_numbers
        self.bank_angle = bank_angle

        self.camshaft = Camshaft()
        self.camshaft.lobes = [0] * len(self.cylinders)

        self.flip = False

    def get_cylinder_index(self, cylinder):
        return self.cylinders.index(cylinder)

class Engine:
    def __init__(self, banks, firing_order):
        self.banks = banks
        self.starter_torque = 70
        self.starter_speed = 500
        self.redline = 18000
        self.throttle_gamma = 2.0

        self.engine_name = "Test Engine"

        self.stroke = 86
        self.bore = 86
        self.rod_length = 120
        self.rod_mass = 50
        self.compression_height = 25.4
        self.crank_mass = 10
        self.flywheel_mass = 10
        self.flywheel_radius = 100

        self.intake_lobe_lift = 551
        self.intake_lobe_duration = 234
        self.intake_lobe_gamma = 1.1

        self.exhaust_lobe_lift = 551
        self.exhaust_lobe_duration = 235
        self.exhaust_lobe_gamma = 1.1
        self.chamber_volume = 300

        self.rod_journals = None
        self.firing_order = firing_order

        self.simulation_frequency = 10000
        self.max_sle_solver_steps = 128
        self.fluid_simulation_steps = 4

        self.idle_throttle_plate_position = 0.999
        self.engine_sim_version = [0, 1, 12, 2]

    def get_cylinder_bank(self, cylinder):
        for bank in self.banks:
            if cylinder in bank.cylinders:
                return bank
            
        return None
    
    def tdc(self):
        return 90 + self.banks[0].bank_angle

    def generate_rod_journals(self):
        n_cylinders = len(self.firing_order)
        gap = 720 / n_cylinders
        tdc = self.tdc()
        current_crank_angle = 0

        self.rod_journals = [0] * n_cylinders
        for cylinder in self.firing_order:
            bank = self.get_cylinder_bank(cylinder)
            bank_angle = bank.bank_angle + 90
            self.rod_journals[cylinder] = (-current_crank_angle) + bank_angle - tdc
            current_crank_angle -= gap


    def cylinder_count(self):
        n = 0
        for bank in self.banks:
            n += len(bank.cylinders)

        return n

    def generate_camshafts(self):
        n_cylinders = len(self.firing_order)
        gap = 720 / n_cylinders
        for cylinder in self.firing_order:
            bank = self.get_cylinder_bank(cylinder)

            firing_order_position = self.firing_order.index(cylinder)
            lobe_index = bank.get_cylinder_index(cylinder)

            bank.camshaft.lobes[lobe_index] = firing_order_position * gap

    def generate(self):
        self.generate_rod_journals()
        self.generate_camshafts()

    def write_head(self, file):
        file.write("""private node generated_head {{
    input intake_camshaft;
    input exhaust_camshaft;
    input chamber_volume: {} * units.cc;
    input intake_runner_volume: 149.6 * units.cc;
    input intake_runner_cross_section_area: 1.75 * units.inch * 1.75 * units.inch;
    input exhaust_runner_volume: 50.0 * units.cc;
    input exhaust_runner_cross_section_area: 1.75 * units.inch * 1.75 * units.inch;

    input flow_attenuation: 1.0;
    input lift_scale: 1.0;
    input flip_display: false;
    alias output __out: head;

    function intake_flow(50 * units.thou)
    intake_flow
        .add_flow_sample(0 * lift_scale, 0 * flow_attenuation)
        .add_flow_sample(50 * lift_scale, 58 * flow_attenuation)
        .add_flow_sample(100 * lift_scale, 103 * flow_attenuation)
        .add_flow_sample(150 * lift_scale, 156 * flow_attenuation)
        .add_flow_sample(200 * lift_scale, 214 * flow_attenuation)
        .add_flow_sample(250 * lift_scale, 249 * flow_attenuation)
        .add_flow_sample(300 * lift_scale, 268 * flow_attenuation)
        .add_flow_sample(350 * lift_scale, 280 * flow_attenuation)
        .add_flow_sample(400 * lift_scale, 280 * flow_attenuation)
        .add_flow_sample(450 * lift_scale, 281 * flow_attenuation)

    function exhaust_flow(50 * units.thou)
    exhaust_flow
        .add_flow_sample(0 * lift_scale, 0 * flow_attenuation)
        .add_flow_sample(50 * lift_scale, 37 * flow_attenuation)
        .add_flow_sample(100 * lift_scale, 72 * flow_attenuation)
        .add_flow_sample(150 * lift_scale, 113 * flow_attenuation)
        .add_flow_sample(200 * lift_scale, 160 * flow_attenuation)
        .add_flow_sample(250 * lift_scale, 196 * flow_attenuation)
        .add_flow_sample(300 * lift_scale, 222 * flow_attenuation)
        .add_flow_sample(350 * lift_scale, 235 * flow_attenuation)
        .add_flow_sample(400 * lift_scale, 245 * flow_attenuation)
        .add_flow_sample(450 * lift_scale, 246 * flow_attenuation)

    generic_cylinder_head head(
        chamber_volume: chamber_volume,
        intake_runner_volume: intake_runner_volume,
        intake_runner_cross_section_area: intake_runner_cross_section_area,
        exhaust_runner_volume: exhaust_runner_volume,
        exhaust_runner_cross_section_area: exhaust_runner_cross_section_area,

        intake_port_flow: intake_flow,
        exhaust_port_flow: exhaust_flow,
        valvetrain: standard_valvetrain(
            intake_camshaft: intake_camshaft,
            exhaust_camshaft: exhaust_camshaft
        ),
        flip_display: flip_display
    )
}}
""".format(self.chamber_volume))
        
    def write_camshaft(self, file):
        file.write("""private node generated_camshaft {
    input lobe_profile;
    input intake_lobe_profile: lobe_profile;
    input exhaust_lobe_profile: lobe_profile;
    input lobe_separation: 114 * units.deg;
    input intake_lobe_center: lobe_separation;
    input exhaust_lobe_center: lobe_separation;  
    input advance: 0 * units.deg; 
    input base_radius: 0.5 * units.inch;""")

        for index, bank in enumerate(self.banks):
            file.write("\n")
            file.write("    output intake_cam_{}: _intake_cam_{};\n".format(index, index))
            file.write("    output exhaust_cam_{}: _exhaust_cam_{};\n".format(index, index))

        file.write(
"""    camshaft_parameters params (
        advance: advance,
        base_radius: base_radius
    )
""")
        
        for index, bank in enumerate(self.banks):
            file.write("\n")
            file.write("    camshaft _intake_cam_{}(params, lobe_profile: intake_lobe_profile)\n".format(index))
            file.write("    camshaft _exhaust_cam_{}(params, lobe_profile: exhaust_lobe_profile)\n".format(index))

        file.write("    label rot360(360 * units.deg)\n")
    
        for index, bank in enumerate(self.banks):
            file.write("    _exhaust_cam_{}\n".format(index))
            for lobe in bank.camshaft.lobes:
                file.write("        .add_lobe(rot360 - exhaust_lobe_center + {} * units.deg)\n".format(lobe))

            file.write("    _intake_cam_{}\n".format(index))
            for lobe in bank.camshaft.lobes:
                file.write("        .add_lobe(rot360 + exhaust_lobe_center + {} * units.deg)\n".format(lobe))

        file.write("}\n")

    def write_engine(self, file):
        file.write("""\npublic node generated_engine {
    alias output __out: engine;

""")
        
        file.write("""    engine engine(
        name: "{}",
        starter_torque: {} * units.lb_ft,
        starter_speed: {} * units.rpm,
        redline: {} * units.rpm,
        throttle_gamma: {},
        fuel: fuel(
            max_turbulence_effect: 10.0,
            max_dilution_effect: 5.0,
            burning_efficiency_randomness: 0.1,
            max_burning_efficiency: 1.0
        ),
        hf_gain: 0.01,
        noise: 1.0,
        jitter: 0.1,
        simulation_frequency: {}
    """.format(self.engine_name, self.starter_torque, self.starter_speed, self.redline, self.throttle_gamma, self.simulation_frequency))
        
        if self.engine_sim_version[2] >= 13:
            file.write(""",
        fluid_simulation_steps: {},
        max_sle_solver_steps: {}
        """, self.max_sle_solver_steps, self.fluid_simulation_steps)

        file.write(")\n\n    wires wires()\n")

        file.write("""
    label stroke({} * units.mm)
    label bore({} * units.mm)
    label rod_length({} * units.mm)
    label rod_mass({} * units.g)
    label compression_height({} * units.mm)
    label crank_mass({} * units.kg)
    label flywheel_mass({} * units.kg)
    label flywheel_radius({} * units.mm)

    label crank_moment(
        disk_moment_of_inertia(mass: crank_mass, radius: stroke)
    )
    label flywheel_moment(
        disk_moment_of_inertia(mass: flywheel_mass, radius: flywheel_radius)
    )
    label other_moment( // Moment from cams, pulleys, etc [estimated]
        disk_moment_of_inertia(mass: 1 * units.kg, radius: 1.0 * units.cm)
    )""".format(self.stroke, self.bore, self.rod_length, self.rod_mass, self.compression_height, self.crank_mass, self.flywheel_mass, self.flywheel_radius))

        file.write("""\n\n    crankshaft c0(
        throw: stroke / 2,
        flywheel_mass: flywheel_mass,
        mass: crank_mass,
        friction_torque: 1.0 * units.lb_ft,
        moment_of_inertia:
            crank_moment + flywheel_moment + other_moment,
        position_x: 0.0,
        position_y: 0.0,
        tdc: {} * units.deg
    )\n""".format(self.tdc()))
        
        file.write("\n")
        for index, journal in enumerate(self.rod_journals):
            file.write("    rod_journal rj{}(angle: {} * units.deg)\n".format(index, journal))

        file.write("    c0\n")
        for index, journal in enumerate(self.rod_journals):
            file.write("        .add_rod_journal(rj{})\n".format(index))

        file.write("\n")

        file.write("""    piston_parameters piston_params(
        mass: (50) * units.g, // 414 - piston mass, 152 - pin weight
        compression_height: compression_height,
        wrist_pin_position: 0.0,
        displacement: 0.0
    )\n\n""")

        file.write("""    connecting_rod_parameters cr_params(
        mass: rod_mass,
        moment_of_inertia: rod_moment_of_inertia(
            mass: rod_mass,
            length: rod_length
        ),
        center_of_mass: 0.0,
        length: rod_length
    )\n""")
        
        file.write("""    intake intake(
        plenum_volume: 1.325 * units.L,
        plenum_cross_section_area: 20.0 * units.cm2,
        intake_flow_rate: k_carb(3000.0),
        runner_flow_rate: k_carb(400.0),
        runner_length: 16.0 * units.inch,
        idle_flow_rate: k_carb(0.0),
        idle_throttle_plate_position: {},
        velocity_decay: 0.5
    )\n""".format(self.idle_throttle_plate_position))

        file.write("""    exhaust_system_parameters es_params(
        outlet_flow_rate: k_carb(2000.0),
        primary_tube_length: 20.0 * units.inch,
        primary_flow_rate: k_carb(200.0),
        velocity_decay: 0.5
    )\n""")
        
        for index, bank in enumerate(self.banks):
            file.write("""    exhaust_system exhaust{}(
        es_params,
        audio_volume: 1.0 * 0.004,
        length: 20 * units.inch,
        impulse_response: ir_lib.minimal_muffling_01
    )\n\n""".format(index))
            
        file.write("""    cylinder_bank_parameters bank_params(
        bore: bore,
        deck_height: stroke / 2 + rod_length + compression_height
    )\n\n""")
        
        file.write("    label spacing(0.0)\n")

        for index, bank in enumerate(self.banks):
            file.write("    cylinder_bank b{}(bank_params, angle: {} * units.deg)\n".format(index, bank.bank_angle))

        for index, bank in enumerate(self.banks):
            file.write("    b{}\n".format(index))
            for cylinder_index, cylinder in enumerate(bank.cylinders):
                file.write("""        .add_cylinder(
            piston: piston(piston_params, blowby: k_28inH2O(0.0)),
            connecting_rod: connecting_rod(cr_params),
            rod_journal: rj{},
            intake: intake,
            exhaust_system: exhaust{},
            ignition_wire: wires.wire{},
            sound_attenuation: {},
            primary_length: {} * spacing * 0.5 * units.cm
        )\n""".format(cylinder, index, cylinder, random.uniform(0.5, 1.0), cylinder_index))
                
            file.write("""        .set_cylinder_head(
            generated_head(
                intake_camshaft: camshaft.intake_cam_{},
                exhaust_camshaft: camshaft.exhaust_cam_{},
                flip_display: {},
                flow_attenuation: 1.0)
        )\n\n""".format(index, index, "true" if bank.flip else "false"))

        file.write("    engine\n")
        for index, bank in enumerate(self.banks):
            file.write("        .add_cylinder_bank(b{})\n".format(index))
        file.write("\n")

        file.write("    engine.add_crankshaft(c0)\n")

        file.write("""    harmonic_cam_lobe intake_lobe(
        duration_at_50_thou: {} * units.deg,
        gamma: {},
        lift: {} * units.thou,
        steps: 512
    )

    harmonic_cam_lobe exhaust_lobe(
        duration_at_50_thou: {} * units.deg,
        gamma: {},
        lift: {} * units.thou,
        steps: 512
    )\n\n""".format(self.intake_lobe_duration, self.intake_lobe_gamma, self.intake_lobe_lift, self.exhaust_lobe_duration, self.exhaust_lobe_gamma, self.exhaust_lobe_lift))
        
        file.write("""    generated_camshaft camshaft(
        lobe_profile: "N/A",

        intake_lobe_profile: intake_lobe,
        exhaust_lobe_profile: exhaust_lobe,
        intake_lobe_center: 90 * units.deg,
        exhaust_lobe_center: 112 * units.deg,
        base_radius: 1.0 * units.inch
    )\n\n""")
        
        file.write("""    function timing_curve(4000 * units.rpm)
    timing_curve
        .add_sample(0000 * units.rpm, 18 * units.deg)
        .add_sample(4000 * units.rpm, 40 * units.deg)
        .add_sample(8000 * units.rpm, 40 * units.deg)
        .add_sample(12000 * units.rpm, 40 * units.deg)
        .add_sample(14000 * units.rpm, 40 * units.deg)
        .add_sample(18000 * units.rpm, 40 * units.deg)\n\n""")

        file.write("""    ignition_module ignition_module(
        timing_curve: timing_curve,
        rev_limit: 18500 * units.rpm,
        limiter_duration: 0.1)\n\n""")

        file.write("    ignition_module\n")
        for index, cylinder in enumerate(self.firing_order):
            file.write("            .connect_wire(wires.wire{}, {} * units.deg)\n".format(cylinder, 720 * (index / len(self.firing_order))))

        file.write("\n    engine.add_ignition_module(ignition_module)\n")

        file.write("}\n\n")

    def write_vehicle_transmission(self, file):
        file.write("""private node generated_vehicle {
    alias output __out:
        vehicle(
            mass: 798 * units.kg,
            drag_coefficient: 0.9,
            cross_sectional_area: (72 * units.inch) * (36 * units.inch),
            diff_ratio: 4.10,
            tire_radius: 9 * units.inch,
            rolling_resistance: 200 * units.N
        );
}

private node generated_transmission {
    alias output __out:
        transmission(
            max_clutch_torque: 1000 * units.lb_ft
        )
        .add_gear(2.8)
        .add_gear(2.29)
        .add_gear(1.93)
        .add_gear(1.583)
        .add_gear(1.375)
        .add_gear(1.19);
}\n\n""")
        
    def write_main_node(self, file):
        file.write("""public node main {
    run(
        engine: generated_engine(),
        vehicle: generated_vehicle(),
        transmission: generated_transmission()
    )
}

main()\n""")

    def write_to_file(self, fname):
        with open(fname, 'w') as file:
            file.write(
"""import "engine_sim.mr"

units units()
constants constants()
impulse_response_library ir_lib()
            
""")

            file.write("private node wires {\n")
            for cylinder in range(self.cylinder_count()):
                file.write("    output wire{}: ignition_wire();\n".format(cylinder))
            file.write("}\n")

            self.write_head(file)
            self.write_camshaft(file)
            self.write_engine(file)
            self.write_vehicle_transmission(file)
            self.write_main_node(file)

def generate_v24():
    cylinders0 = []
    cylinders1 = []
    cylinders = []

    for i in range(12):
        cylinders0.append(i * 2)
        cylinders1.append(i * 2 + 1)
        cylinders += [i * 2, i * 2 + 1]

    b0 = Bank(cylinders0, -45)
    b1 = Bank(cylinders1, 45)
    engine = Engine([b0, b1], cylinders)
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

    b0 = Bank(cylinders0, -34.5)
    b1 = Bank(cylinders1, 34.5)
    b1.flip = True
    engine = Engine([b0, b1], cylinders)
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
    generate_v69()
