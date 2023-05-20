import random
import io

class Fuel:
    def __init__(self):
        # Gasoline
        self.molecular_mass = 100
        self.energy_density = 48.1
        self.density = 0.755
        self.molecular_afr = 25 / 2.0
        self.max_burning_efficiency = 0.8
        self.burning_efficiency_randomness = 0.5
        self.low_efficiency_attenuation = 0.6
        self.max_turbulence_effect = 2
        self.max_dilution_effect = 10

    def generate(self):
        return """molecular_mass: {} * units.g,
            energy_density: {} * units.kJ / units.g,
            density: {} * units.kg / units.L,
            molecular_afr: {},
            max_burning_efficiency: {},
            burning_efficiency_randomness: {},
            low_efficiency_attenuation: {},
            max_turbulence_effect: {},
            max_dilution_effect: {}""".format(self.molecular_mass, self.energy_density, self.density, self.molecular_afr, self.max_burning_efficiency, self.burning_efficiency_randomness, self.low_efficiency_attenuation, self.max_turbulence_effect, self.max_dilution_effect)

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

class Transmission:
    def __init__(self, gears):
        self.gears = gears
        self.node_name = "generated_transmission"

        self.max_clutch_torque = 1000

class Vehicle:
    def __init__(self):
        self.node_name = "generated_vehicle"

        self.mass = 798
        self.drag_coefficient = 0.9
        self.cross_sectional_area = [72, 36]
        
        self.diff_ratio = 4.10
        self.tire_radius = 9
        self.rolling_resistance = 200

class Engine:
    def __init__(self, banks, firing_order):
        self.banks = banks
        self.fuel = Fuel()
        self.starter_torque = 70
        self.starter_speed = 500
        self.redline = 8000
        self.throttle_gamma = 2.0

        self.node_name = "generated_engine"
        self.engine_name = "Test Engine"

        self.hf_gain = 0.01
        self.noise = 1.0
        self.jitter = 0.1

        self.stroke = 86
        self.bore = 86
        self.rod_length = 120
        self.rod_mass = 50
        self.compression_height = 25.4
        self.crank_mass = 10
        self.flywheel_mass = 10
        self.flywheel_radius = 100
        self.piston_mass = 50
        self.piston_blowby = 0.0

        self.plenum_volume = 1.325
        self.plenum_cross_section_area = 20.0
        self.intake_flow_rate = 3000
        self.runner_flow_rate = 400
        self.runner_length = 16
        self.idle_flow_rate = 0

        self.exhaust_length = 20

        self.camshaft_node_name = "generated_camshaft"
        self.lobe_separation = 114
        self.camshaft_base_radius = 0.5
        self.intake_lobe_center = 90
        self.exhaust_lobe_center = 112

        self.intake_lobe_lift = 551
        self.intake_lobe_duration = 234
        self.intake_lobe_gamma = 1.1
        self.intake_lobe_steps = 512

        self.exhaust_lobe_lift = 551
        self.exhaust_lobe_duration = 235
        self.exhaust_lobe_gamma = 1.1
        self.exhaust_lobe_steps = 512

        self.cylinder_head_node_name = "generated_head"
        self.chamber_volume = 300
        self.intake_runner_volume = 149.6
        self.intake_runner_cross_section = [1.75, 1.75]
        self.exhaust_runner_volume = 50.0
        self.exhaust_runner_cross_section = [1.75, 1.75]

        self.intake_flow = [0,58,103,156,214,249,268,280,280,281]
        self.exhaust_flow = [0,37,72,113,160,196,222,235,245,246]

        self.rod_journals = None
        self.firing_order = firing_order

        self.simulation_frequency = 10000
        self.max_sle_solver_steps = 128
        self.fluid_simulation_steps = 4

        self.idle_throttle_plate_position = 0.999
        self.engine_sim_version = [0, 1, 12, 2]

        self.timing_curve = [
            [0,18],
            [1000,40],
            [2000,40],
            [3000,40],
            [4000,40],
            [5000,40],
            [6000,40],
            [7000,40],
            [8000,40],
            [9000,40],
        ]
        
        self.rev_limit = self.redline + 1000
        self.limiter_duration = 0.1

        self.vehicle = Vehicle()
        self.transmission = Transmission([2.8, 2.29, 1.93, 1.583, 1.375, 1.19])

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
        file.write("""private node {} {{
    input intake_camshaft;
    input exhaust_camshaft;
    input chamber_volume: {} * units.cc;
    input intake_runner_volume: {} * units.cc;
    input intake_runner_cross_section_area: {} * units.inch * {} * units.inch;
    input exhaust_runner_volume: {} * units.cc;
    input exhaust_runner_cross_section_area: {} * units.inch * {} * units.inch;

    input flow_attenuation: 1.0;
    input lift_scale: 1.0;
    input flip_display: false;
    alias output __out: head;

    function intake_flow(50 * units.thou)
    intake_flow""".format(self.cylinder_head_node_name,
           self.chamber_volume,
           self.intake_runner_volume,
           self.intake_runner_cross_section[0],
           self.intake_runner_cross_section[1],
           self.exhaust_runner_volume,
           self.exhaust_runner_cross_section[0],
           self.exhaust_runner_cross_section[1]
           ))
        
        for i in range(len(self.intake_flow)):
            file.write("\n")
            file.write("    .add_flow_sample({} * lift_scale, {} * flow_attenuation)".format(i * 50, self.intake_flow[i]))

        file.write("""\n\n    function exhaust_flow(50 * units.thou)
    exhaust_flow""")
        
        for i in range(len(self.exhaust_flow)):
            file.write("\n")
            file.write("    .add_flow_sample({} * lift_scale, {} * flow_attenuation)".format(i * 50, self.exhaust_flow[i]))

        file.write("""\n\n    generic_cylinder_head head(
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
}\n
""")
        
    def write_camshaft(self, file):
        file.write("""private node {} {{
    input lobe_profile;
    input intake_lobe_profile: lobe_profile;
    input exhaust_lobe_profile: lobe_profile;
    input lobe_separation: {} * units.deg;
    input intake_lobe_center: lobe_separation;
    input exhaust_lobe_center: lobe_separation;  
    input advance: 0 * units.deg; 
    input base_radius: {} * units.inch;""".format(self.camshaft_node_name, self.lobe_separation, self.camshaft_base_radius))

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
        file.write("""\npublic node {} {{
    alias output __out: engine;

""".format(self.node_name))
        
        file.write("""    engine engine(
        name: "{}",
        starter_torque: {} * units.lb_ft,
        starter_speed: {} * units.rpm,
        redline: {} * units.rpm,
        throttle_gamma: {},
        fuel: fuel(
            {}
        ),
        hf_gain: {},
        noise: {},
        jitter: {},
        simulation_frequency: {}
    """.format(self.engine_name, self.starter_torque, self.starter_speed, self.redline, self.throttle_gamma, self.fuel.generate(), self.hf_gain, self.noise, self.jitter, self.simulation_frequency))
        
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
        mass: ({}) * units.g, // 414 - piston mass, 152 - pin weight
        compression_height: compression_height,
        wrist_pin_position: 0.0,
        displacement: 0.0
    )\n\n""".format(self.piston_mass))

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
        plenum_volume: {} * units.L,
        plenum_cross_section_area: {} * units.cm2,
        intake_flow_rate: k_carb({}),
        runner_flow_rate: k_carb({}),
        runner_length: {} * units.inch,
        idle_flow_rate: k_carb({}),
        idle_throttle_plate_position: {},
        velocity_decay: 0.5
    )\n""".format(self.plenum_volume, self.plenum_cross_section_area, self.intake_flow_rate, self.runner_flow_rate, self.runner_length, self.idle_flow_rate, self.idle_throttle_plate_position))

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
        length: {} * units.inch,
        impulse_response: ir_lib.minimal_muffling_01
    )\n\n""".format(index, self.exhaust_length))
            
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
            piston: piston(piston_params, blowby: k_28inH2O({})),
            connecting_rod: connecting_rod(cr_params),
            rod_journal: rj{},
            intake: intake,
            exhaust_system: exhaust{},
            ignition_wire: wires.wire{},
            sound_attenuation: {},
            primary_length: {} * spacing * 0.5 * units.cm
        )\n""".format(self.piston_blowby, cylinder, index, cylinder, random.uniform(0.5, 1.0), cylinder_index))
                
            file.write("""        .set_cylinder_head(
            {}(
                intake_camshaft: camshaft.intake_cam_{},
                exhaust_camshaft: camshaft.exhaust_cam_{},
                flip_display: {},
                flow_attenuation: 1.0)
        )\n\n""".format(self.cylinder_head_node_name, index, index, "true" if bank.flip else "false"))

        file.write("    engine\n")
        for index, bank in enumerate(self.banks):
            file.write("        .add_cylinder_bank(b{})\n".format(index))
        file.write("\n")

        file.write("    engine.add_crankshaft(c0)\n\n")

        file.write("""    harmonic_cam_lobe intake_lobe(
        duration_at_50_thou: {} * units.deg,
        gamma: {},
        lift: {} * units.thou,
        steps: {}
    )

    harmonic_cam_lobe exhaust_lobe(
        duration_at_50_thou: {} * units.deg,
        gamma: {},
        lift: {} * units.thou,
        steps: {}
    )\n\n""".format(self.intake_lobe_duration, self.intake_lobe_gamma, self.intake_lobe_lift, self.intake_lobe_steps, self.exhaust_lobe_duration, self.exhaust_lobe_gamma, self.exhaust_lobe_lift, self.exhaust_lobe_steps))
        
        file.write("""    {} camshaft(
        lobe_profile: "N/A",

        intake_lobe_profile: intake_lobe,
        exhaust_lobe_profile: exhaust_lobe,
        intake_lobe_center: {} * units.deg,
        exhaust_lobe_center: {} * units.deg
    )\n\n""".format(self.camshaft_node_name, self.intake_lobe_center, self.exhaust_lobe_center))
        
        file.write("""    function timing_curve(1000 * units.rpm)
    timing_curve""")
        for point in self.timing_curve:
            file.write("\n")
            file.write("        .add_sample({} * units.rpm, {} * units.deg)".format(point[0], point[1]))

        file.write("\n\n")

        file.write("""    ignition_module ignition_module(
        timing_curve: timing_curve,
        rev_limit: {} * units.rpm,
        limiter_duration: 0.1)\n\n""".format(self.rev_limit, self.limiter_duration))

        file.write("    ignition_module\n")
        for index, cylinder in enumerate(self.firing_order):
            file.write("            .connect_wire(wires.wire{}, {} * units.deg)\n".format(cylinder, 720 * (index / len(self.firing_order))))

        file.write("\n    engine.add_ignition_module(ignition_module)\n")

        file.write("}\n\n")

    def write_vehicle_transmission(self, file):
        file.write("""private node {} {{
    alias output __out:
        vehicle(
            mass: {} * units.kg,
            drag_coefficient: {},
            cross_sectional_area: ({} * units.inch) * ({} * units.inch),
            diff_ratio: {},
            tire_radius: {} * units.inch,
            rolling_resistance: {} * units.N
        );
}}\n\n""".format(
            self.vehicle.node_name,
            self.vehicle.mass,
            self.vehicle.drag_coefficient,
            self.vehicle.cross_sectional_area[0],
            self.vehicle.cross_sectional_area[1],
            self.vehicle.diff_ratio,
            self.vehicle.tire_radius,
            self.vehicle.rolling_resistance
            ))
        
        file.write("""private node {} {{
    alias output __out:
        transmission(
            max_clutch_torque: {} * units.lb_ft
        )""".format(self.transmission.node_name, self.transmission.max_clutch_torque))
        
        for gear in self.transmission.gears:
            file.write("\n")
            file.write("    .add_gear({})".format(gear))
        
        file.write(";\n}\n\n")
        
    def write_main_node(self, file):
        file.write("""public node main {{
    run(
        engine: {}(),
        vehicle: {}(),
        transmission: {}()
    )
}}

main()\n""".format(self.node_name, self.vehicle.node_name, self.transmission.node_name))

    def __write(self, file):
        file.write(
"""import "engine_sim.mr"

units units()
constants constants()
impulse_response_library ir_lib()
            
""")

        file.write("private node wires {\n")
        for cylinder in range(self.cylinder_count()):
            file.write("    output wire{}: ignition_wire();\n".format(cylinder))
        file.write("}\n\n")

        self.write_head(file)
        self.write_camshaft(file)
        self.write_engine(file)
        self.write_vehicle_transmission(file)
        self.write_main_node(file)
        
    def write_to_string(self):
        file = io.StringIO()
        self.__write(file)
        return file.getvalue()

    def write_to_console(self):
        print(self.write_to_string())
    
    def write_to_file(self, fname):
        with open(fname, 'w') as file:
            self.__write(file)
