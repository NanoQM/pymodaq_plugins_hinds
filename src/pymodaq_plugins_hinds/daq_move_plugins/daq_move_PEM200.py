from typing import Union, List, Dict

from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, main, DataActuatorType,\
    DataActuator  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand # object used to send info back to the main thread
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_hinds.hardware.pem200_driver import PEM200Driver
# from pymodaq.utils.logger import set_logger, get_module_name
#
# logger = set_logger(get_module_name(__file__))

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
    is_multiaxes = False  # TODO for your plugin set to True if this plugin is controlled for a multiaxis controller
    _axis_names: Union[List[str], Dict[str, int]] = ['PEM_200']  # TODO for your plugin: complete the list
    _controller_units: Union[str, List[str]] = 'nm'  # TODO for your plugin: put the correct unit here, it could be
    # TODO  a single str (the same one is applied to all axes) or a list of str (as much as the number of axes)
    _epsilon: Union[float, List[float]] = 0.1  # TODO replace this by a value that is correct depending on your controller
    # TODO it could be a single float of a list of float (as much as the number of axes)
    data_actuator_type = DataActuatorType.DataActuator  # wether you use the new data style for actuator otherwise set this
    # as  DataActuatorType.float  (or entirely remove the line)

# DK - you need retardation, drive_value, state
    params = [
                 {'title': 'Resource Name:', 'name': 'resource_name', 'type': 'str', 'value': "ASRL6::INSTR"},
                 {'title': 'Retardation:', 'name': 'retardation', 'type': 'float', 'value': 0.5, 'min': 0, 'max': 1},
                 {'title': 'Drive Value:', 'name': 'drive_value', 'type': 'float', 'value': 0.1, 'min': 0, 'max': 1},
                 {'title': 'State:', 'name': 'state', 'type': 'list', 'value': 0, 'limits': [0, 1]},
                 {'title': 'Info', 'name': 'info', 'type': 'str', 'value': '', 'readonly': True},
                 {'title': 'Frequency (Hz)', 'name': 'frequency', 'type': 'float', 'value': 0, 'readonly': True},
                 # TODO for your custom plugin: elements to be added here as dicts in order to control your custom stage
                ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)
    # _epsilon is the initial default value for the epsilon parameter allowing pymodaq to know if the controller reached
    # the target value. It is the developer responsibility to put here a meaningful value

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller: PEM200Driver = None

        #TODO declare here attributes you want/need to init with a default value
        # pass

    def get_actuator_value(self):
        """Get the current value fget wavelnengthrom the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        pos = DataActuator(data=self.controller.get_wavelength())  # when writing your own plugin replace this line
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

    # DK - call close method
    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        self.controller.set_pem_output(0)
        self.settings['state'] = 0
        self.controller.close()  # when writing your own plugin replace this line

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'state':
            self.controller.set_pem_output(self.settings['state'])

        elif param.name() == "retardation":
            self.controller.set_retardation(self.settings['retardation'])

        elif param.name() == "drive_value":
           self.controller.set_modulation_drive(self.settings["drive_value"])

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
        self.ini_stage_init(slave_controller=controller)  # will be useful when controller is slave

        if self.is_master:  # is needed when controller is master
            self.controller = PEM200Driver(self.settings["resource_name"]) #  arguments for instantiation!)
            self.controller.connect()

            # todo: enter here whatever is needed for your controller initialization and eventual
            #  opening of the communication channel

        self.controller.set_retardation(self.settings['retardation'])

        info = self.controller.identify()
        self.settings.child('info').setValue(info)

        self.settings.child('frequency').setValue(self.controller.get_frequency())
        self.settings.child("retardation").setValue(self.controller.get_retardation())
        self.settings.child("drive_value").setValue(self.controller.get_modulation_drive())

        self.controller.set_pem_output(1) # turn on
        self.settings.child("state").setValue(1)

        initialized = True
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (DataActuator) object of the absolute target positioning
        """

        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        self.controller.set_modulation_amplitude(value.value())
        # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (DataActuator) object of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_with_scaling(self.target_value)
        # value = self.set_position_relative_with_scaling(value)

        self.controller.set_modulation_amplitude(value.value())  # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def move_home(self):
        """Call the reference method of the controller"""

        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        self.controller.set_modulation_amplitude(0)  # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    # DK - turn off by set_pem_output
    def stop_motion(self):
      """Stop the actuator and emits move_done signal"""

      ## TODO for your custom plugin
      # raise NotImplemented  # when writing your own plugin remove this line
      # self.controller.set_pem_output(0) # when writing your own plugin replace this line
      # self.emit_status(ThreadCommand('Updat_Status', ['Some info you want to log']))

      return ''

if __name__ == '__main__':
    main(__file__)
