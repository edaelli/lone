import sys
import platform
import subprocess

from lone.system import SysRequirements


class LinuxRequirements(SysRequirements):

    def __init__(self):
        self.failure = False

    def print_status(self, description, failure=False, extra=''):
        fmt = ' -- Checking for {:30} {:50} {:>4}'
        print(fmt.format(description,
              extra, '\033[91mFAIL\033[0m' if failure else '\033[92mOK\033[0m'))

        if self.failure is False and failure is True:
            self.failure = True

    def check_requirements(self):
        print('Checking test system for Linux requirements:')
        self.check_python()
        self.check_ubuntu()
        self.check_VT_VI()
        self.check_hugepages()
        self.check_hugepages_lib()

        if self.failure:
            print('ERROR: One or more requirements not met')
        else:
            print('All requirements met')

    def check_python(self):
        # Check for Python 3.5+
        python_required_version = (3, 5, 0)
        python_version_string = platform.python_version()
        if sys.version_info < python_required_version:
            self.print_status('Python 3.5.0+', True, python_version_string)
        else:
            self.print_status('Python 3.5.0+', False, python_version_string)

    def check_ubuntu(self):
        # Check for Ubuntu 22.04
        release = None
        try:
            lsb_release = subprocess.check_output(['lsb_release', '-a'],
                                                  stderr=subprocess.PIPE).decode('utf-8')
            for line in lsb_release.splitlines():
                if 'Distributor ID:' in line:
                    dist_id = line.split(':')[1].strip()
                elif 'Description:' in line:
                    description = line.split(':')[1].strip()
                elif 'Release:' in line:
                    release = line.split(':')[1].strip()
                    release_major = int(release.split('.')[0])

            if dist_id != 'Ubuntu' or release_major < 20:
                self.print_status('Ubuntu 20.04+', True, description)
            else:
                self.print_status('Ubuntu 20.04+', False, description)

        except Exception:
            # Can not get lsb_release info
            self.print_status('Ubuntu 20.04', True, release)

    def check_VT_VI(self):
        # Check if iommu_groups exist which imply VT-d/AMD-Vi
        iommu_path = '''/sys/kernel/iommu_groups/*/devices/*'''
        try:
            subprocess.check_call(['compgen -G "{}"'.format(iommu_path)], shell=True,
                                  executable='/bin/bash',
                                  stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            self.print_status('Intel VT-d / AMD-Vi', False, 'Present')
        except subprocess.CalledProcessError:
            self.print_status('Intel VT-d / AMD-Vi', True, 'Not Present')

    def check_hugepages_lib(self):
        # Check that the libhugetlbfs-dev library is installed
        cmd = '''echo "#include \\"hugetlbfs.h\\"" | cpp -o /dev/null'''
        try:
            subprocess.check_call(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            self.print_status('libhugetlbfs-dev', False, 'Present')
        except subprocess.CalledProcessError:
            self.print_status('libhugetlbfs-dev', True, 'Not Present')

    def check_hugepages(self):
        # Check hugepages support
        with open('/proc/meminfo', 'r') as fh:
            meminfo = fh.read()
            for line in meminfo.splitlines():
                if 'HugePages_Total' in line:
                    hugepages_present = True
                elif 'HugePages_Free' in line:
                    hugepages_available = int(line.split(':')[-1])
                elif 'Hugepagesize' in line:
                    hugepages_size, hugepages_size_unit = line.split(':')[-1].split()[:2]

            # Requirements met if present and at least one available
            hp_failure = not (hugepages_present and hugepages_available)

            self.print_status('HugePages', hp_failure, '{}, {} available, size: {} {}'.format(
                              'Present' if hugepages_present else 'NOT Present',
                              hugepages_available, hugepages_size, hugepages_size_unit))
