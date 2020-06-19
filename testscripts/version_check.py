"""
version_check.py
Verify OS version of devices in the testbed.
"""
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts
# FIXME: Doesnt currently work for NXOS devices as 'version' key is not present

__author__ = "Shaun Chivers"
__copyright__ = "Copyright (c) 2020, Cisco Systems Inc."
__contact__ = ["shaun.chivers@global.ntt"]
__credits__ = []
__version__ = 1.0

import logging
import csv
import os.path

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

class version_check(aetest.Testcase):
    """version_check
    < docstring description of this testcase >
    """

    # List of keys to check for version
    #   Model details: https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/_models/version.pdf
    version_input_keys = ("version")

    @aetest.setup
    def setup(self, testbed):
        """Learn and save the platform details from the testbed devices."""
        self.learnt_platform_info = {}
        for device_name, device in testbed.devices.items():
            # Only attempt to learn details on supported network operation systems
            if device.os in ("ios", "iosxe", "iosxr", "nxos"):
                logger.info(f"{device_name} connected status: {device.connected}")
#                logger.info(f"Learning platform for {device_name}")
#                self.learnt_platform_info[device_name] = device.learn("platform")
                

    @aetest.test
    def test(self, testbed, steps):

                # using python "with" statement and steps parameter
        with steps.start('Version Read/Write',
                         description = 'Read the software version running on the device and write it to a file') as step:
            print('Current step index: ', step.index)
 
            # Create an empty dictionary that will hold the details we will write to the CSV
            device_version_details = {}

            # Loop over each device in the network testbed
            for device_name in testbed.devices:
                # Connect to device
                testbed.devices[device_name].connect

                # Run the "show version" command on the device
                version_details = testbed.devices[device_name].parse("show version")

                # Store this device version details in the dictionary
                device_version_details[device_name] = version_details

                # the name for our report file
                version_file = "device_software.csv"

                file_exists = os.path.isfile('device_software.csv')

                # The headers we'll use in the CSV file
                report_fields = ["Device", "Version"]

                # Open up the new file for "w"riting
                with open(version_file, "a") as f:
                    # Create a CSV "DictWriter" object providing the list of fields
                    writer = csv.DictWriter(f, delimiter=',', lineterminator='\n',fieldnames=report_fields)
                    
                    # Write the header row to the start of the file
                    if not file_exists:
                        writer.writeheader()

                    # Loop over each device and version details we gathered and stored
                    for devices, version in version_details.items():
                        writer.writerow(
                            {
                            "Device": device_name,
                            "Version": version["version"],
                            }
                        )
                    logger.info ('Version information written for %s' % device_name)
#        logger.info(f" Version details for {device_name} have been written to file")



        # Verify that the device "version" is correct       



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
