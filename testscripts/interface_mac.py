"""
interface_MAC.py
gathers interface MAC addresses of devices in the testbed.
"""
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

__author__ = "Shaun Chivers"
__copyright__ = "Copyright (c) 2020, Cisco Systems Inc."
__contact__ = ["shaun.chivers@global.ntt"]
__credits__ = []
__version__ = 1.0

import logging
import csv

from pyats import aetest
from genie.testbed import load
from unicon.core.errors import TimeoutError, StateMachineError, ConnectionError
from genie.conf import Genie

# create a logger for this module
logger = logging.getLogger(__name__)

###################################################################
#                  COMMON SETUP SECTION                           #
###################################################################

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, testbed):
        # Convert pyATS testbed to Genie Testbed
        logger.info(
            "Converting pyATS testbed to Genie Testbed to support pyATS Library features"
        )
        testbed = load(testbed)
        self.parent.parameters.update(testbed=testbed)

    @aetest.subsection
    def connect(self, testbed):
        """
        establishes connection to all your testbed devices.
        """
        # make sure testbed is provided
        assert testbed, "Testbed is not provided!"

        # connect to all testbed devices
        #   By default ANY error in the CommonSetup will fail the entire test run
        #   Here we catch common exceptions if a device is unavailable to allow test to continue
        try:
            testbed.connect()
        except (TimeoutError, StateMachineError, ConnectionError):
            logger.error("Unable to connect to all devices")


###################################################################
#                     TESTCASES SECTION                           #
###################################################################

class interface_mac(aetest.Testcase):
    """interface_mac
    < docstring description of this testcase >
    """

    # List of keys to check for interface
    #   Model details: https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/_models/platform.pdf
    interface_input_keys = ("interface")

    @aetest.setup
    def setup(self, testbed):
        """Learn and save the interface details from the testbed devices."""
        self.learnt_interface_info = {}
        for device_name, device in testbed.devices.items():
            # Only attempt to learn details on supported network operation systems
            if device.os in ("ios", "iosxe", "iosxr", "nxos"):
                logger.info(f"{device_name} connected status: {device.connected}")
                logger.info(f"Learning interface for {device_name}")
                self.learnt_interface_info[device_name] = device.learn("interface")
                

    @aetest.test
    def test(self, testbed, steps):

                # using python "with" statement and steps parameter
        with steps.start('Interface Read',
                         description = 'Read the interfaces and MAC addresses on the device and write it to a file') as step:
            print('Current step index: ', step.index)
 
            # Create an empty dictionary that will hold the details we will write to the CSV
            device_interface_details = {}

            # Loop over each device in teh network testbed
            for device_name in testbed.devices:
                # Connect to device
                testbed.devices[device_name].connect

                # Run the "show interfaces" command on the device
                interface_details = testbed.devices[device_name].parse("show interfaces")

                # Store this device interface details in the dictionary
                device_interface_details[device_name] = interface_details

            # the name for our report file
            interface_file = "interfaces.csv"

            # The headers we'll use in the CSV file
            report_fields = ["Device", "Interface", "MAC Address"]

            # Open up the new fiule for "w"riting
            with open(interface_file, "w") as f:
                # Create a CSN "DictWriter" object providing the list of fields
                writer = csv.DictWriter(f, report_fields)
                # Write the header row to the start of the file
                writer.writeheader()

                # Loop over each device and interface details we gathered and stored
                for device_name, interfaces in device_interface_details.items():
                    # Loop over each interface for the current device in the outer loop
                    for interface, details in interfaces.items():
                        # Attempt to write a row. If an interface lacks MAC (ie Loopback)
                        # it will raise a "KeyError"
                        try:
                            writer.writerow(
                                {
                                    "Device": device_name,
                                    "Interface": interface,
                                    "MAC Address": details["mac_address"],
                                }
                            )
                        except KeyError:
                            # Loopback interfaces lack a mac_address, mark it as "N/A"
                            writer.writerow(
                                {"Device": device_name, "Interface": interface, "MAC Address": "N/A"}
                            )
                logger.info(f" Interface details for {device_name} have been written to file")

  

###################################################################
#                     CLEANUP SECTION                           #
###################################################################

class CommonCleanup(aetest.CommonCleanup):
    """CommonCleanup Section
    < common cleanup docstring >
    """

    # uncomment to add new subsections
    # @aetest.subsection
    # def subsection_cleanup_one(self):
    #     pass


if __name__ == "__main__":
    # for stand-alone execution
    import argparse
    from pyats import topology

    # from genie.conf import Genie

    parser = argparse.ArgumentParser(description="standalone parser")
    parser.add_argument(
        "--testbed",
        dest="testbed",
        help="testbed YAML file",
        type=topology.loader.load,
        # type=Genie.init,
        default=None,
    )

    # do the parsing
    args = parser.parse_known_args()[0]

    aetest.main(testbed=args.testbed)
