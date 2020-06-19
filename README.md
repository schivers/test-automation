# Test Automation using pyATS
This project uses Cisco's pyATS testing ecosystem to provide a reuseable set of factory & Siite Acceptance Tests.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine using the latest pyATS docker image supplied by Cisco.

### Prerequisites

What things you need to install the software and how to install them

```
install docker
```

### Download the pyATS docker image
The command below will download the image if you don’t have it, instantiate the container, and give you an interactive shell into the container that now has your environment.
```
docker run -it ciscotestautomation/pyats:latest /bin/bash
```

### Test Scripts
#### Download my Test Scripts
```
cd ./pyats
git clone https://scm.dimensiondata.com/Shaun.Chivers/test-automation/testscripts 
```

#### Cisco Example Test Scripts (optional)
The Cisco examples folder is no longer part of the pyATS docker image so you need to download it (if you want some examples).
```
root@c1cac24ee8be:/pyats/pyats_intro# git clone https://github.com/CiscoTestAutomation/examples
```

## Running the tests
Use easypy, specifying the test jobfile and testbed file. One of the useful output switches is to generate an HTML report output
```
# Run a test job & generate local TaskLog.html output in /FAThtml
easypy network_test_job.py -html_logs FAThtml -testbed_file testbed.yaml
```
network_test_job.py = the test job file <br />
-html_logs FAThtml = generate an html output and place it in folder /FAThtml (optional) <br />
Testbed filename = testbed.yaml <br />

## Acknowledgments

* https://developer.cisco.com/pyats/
* https://hub.docker.com/r/ciscotestautomation/pyats/
* https://gratuitous-arp.net/getting-started-with-pyats-and-genie/
