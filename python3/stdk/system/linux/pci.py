import os
import pwd
import subprocess

from stdk.system import SysPci, SysPciDevice


class LinuxSysPci(SysPci):

    def rescan(self):
        rescan_path = '/sys/bus/pci/rescan'
        with open(rescan_path, 'w') as fd:
            fd.write('1\n')


class LinuxSysPciDevice(SysPciDevice):

    def __init__(self, pci_slot):
        super().__init__(pci_slot)

        # Get the device's iommu_group from sysfs
        iommu_group_path = '/sys/bus/pci/devices/{}/iommu_group'.format(pci_slot)
        ret = os.readlink(iommu_group_path)
        self.iommu_group = os.path.basename(ret)

    def exists(self):
        device_path = '/sys/bus/pci/devices/{}/'.format(self.pci_slot)
        return os.path.exists(device_path)

    def remove(self):
        remove_path = '/sys/bus/pci/devices/{}/remove'.format(self.pci_slot)
        if os.path.exists(remove_path):
            with open(remove_path, 'w') as fd:
                fd.write('1\n')

    def expose(self, user):
        # Unbind from the current driver, if it is bound
        self._unbind_current_driver()

        self.exposed_device_path = self._create_device()
        if type(user) == str:
            if user.isnumeric():
                user = int(user)

        self._change_device_ownership(self.exposed_device_path, user)

    def reclaim(self, driver):
        self._unbind_current_driver()
        self._bind_to_driver(driver)

    def _unbind_current_driver(self):
        module_path = '/sys/bus/pci/devices/{}/driver/module'.format(self.pci_slot)

        # Only bound if the path exists
        if os.path.exists(module_path):

            # Get driver name
            ret = os.readlink(module_path)
            driver = os.path.basename(ret)

            # Translate to unbind path name if needed
            if driver == 'vfio_pci':
                unbind_name = 'vfio-pci'
            else:
                unbind_name = driver

            # Create unbind path
            unbind_path = '/sys/bus/pci/drivers/{}/unbind'.format(unbind_name)

            # Write pcie slot to unbind it
            with open(unbind_path, 'w') as fd:
                fd.write(self.pci_slot)

            # Remove the id
            if driver == 'vfio_pci':
                ret = subprocess.check_output(['lspci', '-n', '-s', self.pci_slot])
                ids = ret.split()[2].decode().replace(':', ' ')
                new_id_path = '/sys/bus/pci/drivers/vfio-pci/remove_id'
                with open(new_id_path, 'w') as fd:
                    fd.write(ids)

    def _bind_to_driver(self, driver):
        path = '/sys/bus/pci/drivers/{}/bind'.format(driver)
        if os.path.exists(path):
            with open(path, 'w') as fh:
                fh.write(self.pci_slot)
        else:
            print('WARNING: Could not bind to driver: {}'.format(driver))

    def _create_device(self):
        ret = subprocess.check_output(['lspci', '-n', '-s', self.pci_slot])
        ids = ret.split()[2].decode().replace(':', ' ')
        new_id_path = '/sys/bus/pci/drivers/vfio-pci/new_id'
        device_path = '/dev/vfio/{}'.format(self.iommu_group)

        with open(new_id_path, 'w') as fd:
            fd.write(ids)

        if not os.path.exists(device_path):
            device_path = None
            print('ERROR: vfio device {} was not created'.format(self.iommu_group))

        return device_path

    def _change_device_ownership(self, device_path, user):
        if type(user) == str:
            user_info = pwd.getpwnam(user)
        elif type(user) == int:
            user_info = pwd.getpwuid(user)
        else:
            raise Exception('Wrong user type: {}'.format(type(user)))

        user_id = user_info.pw_uid
        group_id = user_info.pw_gid

        os.chown(device_path, user_id, group_id)
        assert os.stat(device_path).st_uid == user_id
        assert os.stat(device_path).st_gid == group_id
