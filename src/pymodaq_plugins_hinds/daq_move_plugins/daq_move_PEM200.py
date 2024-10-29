from typing import Union, List, Dict
import pyvisa

from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, main, DataActuatorType, \
    DataActuator  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand  # object used to send info back to the main thread
from pymodaq.utils.parameter import Parameter
# from pymodaq_plugins_hinds.hardware.pem200 import PEM200Driver

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

# TODO:
# (1) change the name of the following class to DAQ_Move_TheNameOfYourChoice
# (2) change the name of this file to daq_move_TheNameOfYourChoice ("TheNameOfYourChoice" should be the SAME
#     for the class name and the file name.)
# (3) this file should then be put into the right folder, namely IN THE FOLDER OF THE PLUGIN YOU ARE DEVELOPING:
#     pymodaq_plugins_my_plugin/daq_move_plugins
class DAQ_Move_PEM200(DAQ_Move_base):
    """ Instrument plugin class for an actuator.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of controllers and actuators that should be compatible with this instrument plugin.
        * With which instrument and controller it has been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    # TODO add your particular attributes here if any

    """
    is_multiaxes = True  # TODO for your plugin set to True if this plugin is controlled for a multiaxis controller
    _axis_names: Union[List[str], Dict[str, int]] = {'PEM1':1}  # TODO for your plugin: complete the list
    _controller_units: Union[str, List[str]] = 'nm'  # TODO for your plugin: put the correct unit here, it could be
    # TODO  a single str (the same one is applied to all axes) or a list of str (as much as the number of axes)
    _epsilon: Union[
        float, List[float]] = 0.1  # TODO replace this by a value that is correct depending on your controller
    # TODO it could be a single float of a list of float (as much as the number of axes)
    data_actuator_type = DataActuatorType.DataActuator  # whether you use the new data style for actuator otherwise set this
    # as  DataActuatorType.float  (or entirely remove the line)

# DK delete : list ["a", "b","c"]
# DK delete : dictionary {"xaxis": "b", "yaxis":"a", ...}
    # DK - add resource_name, wavelength, retardation, frequency, state
    params = [{'title': 'Resource Name:', 'name': 'resource_name', 'type': 'str', 'value': "VISA-RESOURCE-PLACEHOLDER"},
                # {'title': 'Drive Value:', 'name': 'drive_value', 'type': 'float', 'value': 0}, DK - drive_value is taken from the left panel of GUI
              # {},  # DK - add a parameter here for the wavelength
              #   {},  # DK - add a parameter here for the retardation
              #   {},  # DK - add a parameter here for the frequency
              #   {},  # DK - add a parameter here for the state  w
              ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    # _epsilon is the initial default value for the epsilon parameter allowing pymodaq to know if the controller reached
    # the target value. It is the developer responsibility to put here a meaningful value

    # DK - done
    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller: PEM200Driver = None
        self._move_done = False

        # TODO declare here attributes you want/need to init with a default value
        # pass

    # DK - done
    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        pos = DataActuator(
            data=self.controller.get_modulation_amplitude())  # when writing your own plugin replace this line
        pos = self.get_position_with_scaling(pos)
        return pos

    # def user_condition_to_reach_target(self) -> bool:
    #     """ Implement a condition for exiting the polling mechanism and specifying that the
    #     target value has been reached
    #
    #    Returns
    #     -------
    #     bool: if True, PyMoDAQ considers the target value has been reached
    #     """
    #     # TODO either delete this method if the usual polling is fine with you, but if need you can
    #     #  add here some other condition to be fullfilled either a completely new one or
    #     #  using or/and operations between the epsilon_bool and some other custom booleans
    #     #  for a usage example see DAQ_Move_brushlessMotor from the Thorlabs plugin
    #     return True

    def close(self):
        """Terminate the communication protocol"""
        # ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        self.controller.close()  # when writing your own plugin replace this line

    # DK - change the settings in params where this works when you change values in the GUI
    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == 'wavelength':
            self.axis_unit = self.controller.set_modulation_amplitude(
                self.settings['wavelength'], self.settings['retardation'])
        elif param.name() == 'retardation':
            # DK - do something
            pass # DK - delete pass when you add method
        elif param.name() == 'state':
            # DK - do something
            pass # DK - delete pass when you add method

            # do this only if you can and if the units are not known beforehand, for instance
            # if the motors connected to the controller are of different type (mm, µm, nm, , etc...)
            # see BrushlessDCMotor from the thorlabs plugin for an exemple

        # elif param.name() == "a_parameter_you've_added_in_self.params":
        #     self.controller.your_method_to_apply_this_param_change()
        else:
            pass

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        # raise NotImplemented  # TODO when writing your own plugin remove this line and modify the ones below
        # self.ini_stage_init(slave_controller=controller)  # will be useful when controller is slave

        if self.is_master:  # is needed when controller is master
            self.controller = PEM200Driver(self.settings['resource_name'])
            self.controller.connect()

            # todo: enter here whatever is needed for your controller initialization and eventual
            #  opening of the communication channel

        idn = self.controller.identify()
        info = f"Initialized {idn}"
        initialized = True #self.controller.a_method_or_atttribute_to_check_if_init()  # todo
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)  # if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        self.controller.set_modulation_drive(
            value.value())  # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log'])) # DK - edit  ''

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)

        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        self.controller.set_modulation_drive(
            self.target_value.value())  # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log'])) # DK - edit  ''

    def move_home(self):
        """Call the reference method of the controller"""

        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        # self.controller.your_method_to_get_to_a_known_reference()  # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log'])) # DK - edit  ''

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""

        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        self.controller.set_pem_output(0)  # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Turned of PEM output']))


if __name__ == '__main__':
    main(__file__)
