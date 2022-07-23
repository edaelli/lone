# STDK - Storage Test Development Kit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Introduction

The Storage Test Development Kit (STDK) is a set of tools and libraries primarily written in Python (with C extensions) which grants a user full control of a storage device. It uses similar concepts as [SPDK](https://www.spdk.io), but where SPDK focuses on performance, STDK focuses on testability and control.

The software takes advantage of modern IO Virtualization Hardware such as Intel VT-d and AMD VI to allow full control of a storage device in userspace using Python.

STDK aims to be the basis for writing both extremely simple and extremely complex test cases.

## Quick Start on Linux

- Prepare a system with ubuntu 20.04+, python3.5+ and pip3, running hardware with an IOMMU

- Install [docker](https://docs.docker.com/engine/install/ubuntu/) and [docker-compose](https://docs.docker.com/compose/install/)

- Clone the STDK repo, cd into it, and install python3 requirements for stdk_setup
    ```
    pip3 install -r python3/requirements.txt
    ```

- Check system requirements
   ```
   $ python3 python3/scripts/stdk_setup requirements
     Checking test system for Linux requirements:
     -- Checking for Python 3.5.0+                  3.10.4                                             OK
     -- Checking for Ubuntu 20.04+                  Ubuntu 22.04 LTS                                   OK
     -- Checking for Intel VT-d / AMD-Vi            Present                                            OK
     -- Checking for HugePages                      Present, 128 available, size: 2048 kB              OK
     -- Checking for libhugetlbfs-dev               Present                                            OK
     All requirements met
   ```

- List available devices and expose one to the STDK user (uid = 1000) in the docker container:
    ```
    $ python3 python3/scripts/stdk_setup list
      PciUserspaceDevice devices:
      slot              vid:did        driver        owner   info
      0000:3a:00.0     10EC:5763         nvme                Realtek Semiconductor Co., Ltd. Device 5763 (rev 01)

    $ sudo python3 python3/scripts/stdk_setup expose 0000:3a:00.0 1000
      SUCESS: 0000:3a:00.0 is now usable by 1000 in userspace as /dev/vfio/19
    ```

- Build and enter docker STDK environment
    ```
    $ docker compose build stdk_env
    ...

    $ docker compose run stdk_env
    stdk_user@e1337ced27c4:/$
    ```

- Run an example (nvme_list.py mimics the nvme-cli list command)
    ```
    stdk_user@e1337ced27c4:/$ python3 /opt/stdk/stdk/examples/nvme_list.py
    Node             SN                   Model                                    Namespace Usage                      Format           FW Rev
    ---------------- -------------------- ---------------------------------------- --------- -------------------------- ---------------- --------
    0000:3a:00.0     112101120390182      TEAM TM8FP6002T                          1           2.05 TB /   2.05 TB      512    B + 0 B   V9002s65
    ```


## Motivation

STDK was conceived as an alternative to current storage test tools, initially focusing on the NVMe Specification.

The driving factor for this development kit is to make storage testing straightforward by building Python objects on top of userspace PCI & NVMe register and memory access; then combining those basic building blocks into complex tasks, all while giving a user the full power of the Python language in a storage test infrastructure.

## Theory of Operation

An NVMe device is interacted with by using a combination of 3 different access mechanisms:
1. Configuration Space or PCI registers
2. Memory mapped NVMe registers
3. Operating System Memory

A very simple view of how an NVMe device operates is that a host system (or developer, or test engineer, test infrastructure, etc) changes values in PCI and NVMe registers which affect how the device behaves. In some cases, the host system allocates buffers for the device to access and communicates those buffers addresses to the device.

STDK uses IO Virtualization technology to present the 3 access mechanisms above to a userspace process. This allows the development kit to create Python objects that make testing straightforward, enables combining the basic building blocks into complex tasks, and gives a user the full power of the Python language:

    # Import modules
    >>> from stdk.system import System
    >>> from stdk.examples.nvme_demo_driver import NVMeDemoDriver
    >>> from stdk.nvme.device import NVMeDevice

    # Create objects
    >>> mem_mgr = System.MemoryMgr()
    >>> nvme_device = NVMeDevice('0000:3a:00.0')
    >>> demo_driver = NVMeDemoDriver(nvme_device, mem_mgr)

    # Access PCIe registers
    >>> hex(nvme_device.pcie_regs.ID.VID)
    '0x10ec'
    >>> hex(nvme_device.pcie_regs.ID.DID)
    '0x5763'

    # Acccess NVMe registers
    >>> hex(nvme_device.nvme_regs.VS.MJR)
    '0x1'
    >>> hex(nvme_device.nvme_regs.VS.MNR)
    '0x3'

    # Map device IOMMU memory
    >>> mem = mem_mgr.malloc(4096)
    >>> mem.iova = 0xA0000000
    >>> nvme_device.map_dma_region_read(mem.vaddr, mem.iova, 4096)

    # Enable/disable
    >>> demo_driver.cc_disable()
    >>> hex(nvme_device.nvme_regs.CSTS.RDY)
    '0x0'
    >>> demo_driver.cc_enable()
    >>> hex(nvme_device.nvme_regs.CSTS.RDY)
    '0x1'

## Design

### System Interface
A System Interface class sits at the lowest level of the STDK stack. This interface abstracts operating system and hardware access to the rest of the stack. It has the following interfaces:

1. Requirements - Implements an interface into the system running STDK application to check if all requirements are installed

2. Pci - Implements an interface into the Pci subsystem of the OS/Hardware running STDK applications. For example, it allows code to rescan the devices in the Pci bus for a system

3. PciDevice - Implements an interface into each Pci device in a system. For example, it allows code to check if a device at a certain slot exists

4. PciUserspace - Implements an interface into a system to interact with the userspace exposed functions of that system. For example, it can query the system for a list of userspace-exposed devices

5. PciUserspaceDevice - Implements an interface into each userspace-exposed device. For example, it exposes the device's registers in a system independent way

6. Memory - Implements an interface into the system running STDK applications to allocate pinned memory (special memory pages that cannot be paged out by an OS's memory management system)

### Layered Architecture
STDK software layers are organized as:

<img src=doc/stdk_layers.png width=600 align=center>

## Requirements
NOTE: STDK currently implements the System Interfaces above for Linux only. Other OS support is possible, but not yet implemented.

### Hardware
STDK relies on a systems IOMMU hardware to safely allow userspace access of storage devices. The system must have Intel Vt-d, AMD Vi, etc for STDK to work.

### Software

#### Linux
- python3.5+
- Ubuntu 20.04+
- Hugepages enabled and available
- libhugetlbfs-dev
- docker, if using the provided container

## System Setup

### Linux
STDK is meant to be run in userspace without root privileges. However, root privileges are required to expose a vfio device to a certain user. STDK provides a script (stdk_setup) to accomplish that. Once all requirements are met in the target system, it can be run by:

    cd <stdk_path>
    python3 python3/scripts/stdk_setup list  # Lists all available NVMe devices that can be exposed to userspace
    sudo python python3/scripts/stdk_setup expose pci_slot_string user  # Exposes the device at the provided pci slot to the provided user
    sudo python python3/scripts/stdk_setup reclaim pci_slot_string driver # Reclaims the device at the provided pci slot and binds it to the provided driver

## Installation
### Linux
STDK provides a docker container and docker-compose configuration file that allows a system to quickly start running. After installing [docker](https://docs.docker.com/engine/install/ubuntu/) and [docker-compose](https://docs.docker.com/compose/install/), run the following commands:

    cd <stdk_path>
    docker compose build stdk_env
    docker compose run stdk_env


## Examples

Please take a look at the repository for [examples](https://github.com/edaelli/stdk/tree/main/python3/stdk/examples). The examples folder contains a functioning demo NVMe driver that can be used to send commands to a device.

## Development
STDK is in early development. The vision is that developers and leaders in the storage industry see its value and help develop it into a sophisticated test framework.

### Discord: https://discord.gg/HxmPaSEY
### Questions, comments, ideas: https://github.com/edaelli/stdk/discussions
### Interesting things to help with: https://github.com/edaelli/stdk/issues
