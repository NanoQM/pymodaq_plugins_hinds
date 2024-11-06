import pyvisa

class PEM200Driver:
    def __init__(self, resource_name):
        """Initialize the PEM200 driver"""
        self.rm = None
        self.instrument = None
        self.resource_name = resource_name

    def connect(self):
        """Connect to the PEM200 device"""
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(self.resource_name)
        self.instrument.timeout = 5000  # Set timeout to 5 seconds
        self.instrument.read_termination = '\n'  # Set read termination to newline

    def identify(self):
        response = self.instrument.query('*IDN?')
        # Extract the desired part from the response and remove the trailing ')'
        return response.split('](')[1].strip().rstrip(')')

    def set_modulation_drive(self, drive_value):
        if 0.0 <= drive_value <= 1.0:
            self.instrument.write(f':MOD:DRV {drive_value}')
        else:
            raise ValueError("Drive value must be between 0.0 and 1.0")

    def get_modulation_drive(self):
        response = self.instrument.query(':MOD:DRV?')
        # Extract the float value from the response
        return float(response.split('](')[1].strip().rstrip(')'))

    # def set_modulation_amplitude(self, amplitude):
    #     self.instrument.write(f':MOD:AMP {amplitude}')

    def set_modulation_amplitude(self, wavelength, retardation):
        amplitude =  wavelength * retardation
        self.instrument.write(f':MOD:AMP {amplitude}')

    # def get_modulation_amplitude(self):
    #     """Get the modulation amplitude for a given wavelength"""
    #     response = self.instrument.query(':MOD:AMP?')
    #     # Extract the float value from the response
    #     return float(response.split('](')[1].strip().rstrip(')'))

    def get_modulation_amplitude(self):
        """Get the modulation amplitude for a given wavelength
        The modulation amplitude is the product of the wavelength and retardation

        """
        response = self.instrument.query(':MOD:AMP?')
        amplitude = float(response.split('](')[1].strip().rstrip(')'))
        # retardation = amplitude / wavelength

        # Extract the float value from the response
        return amplitude


    def get_frequency(self):

        response = self.instrument.query(':MOD:FREQ?')
        # Extract the float value from the response
        return float(response.split('](')[1].strip().rstrip(')'))

    def set_pem_output(self, state):
        """Set the state of the PEM output"""
        if state in [0, 1]:
            self.instrument.write(f':SYS:PEMO {state}')
        else:
            raise ValueError("State must be 0 (off) or 1 (on)")

    def close(self):
        if self.instrument:
            self.instrument.close()
        if self.rm:
            self.rm.close()

# Example usage:
if __name__ == "__main__":
    pem_driver = PEM200Driver()
    pem_driver.connect('USB0::0x1AB1::0x0588::DS1ZA171234567::INSTR')
    print(pem_driver.identify())
    pem_driver.set_modulation_drive(0.5)
    print(f"Modulation Drive: {pem_driver.get_modulation_drive()}")
    pem_driver.set_modulation_amplitude(316.5)
    print(f"Modulation Amplitude: {pem_driver.get_modulation_amplitude()}")
    print(f"Frequency: {pem_driver.get_frequency()}")
    pem_driver.set_pem_output(1)
    pem_driver.close()
