import time


class Injector:
    ''' Generic Injector class
    '''
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.ack = False

    def wait(self, timeout_s=1):
        # Wait for an ack on this injector
        for i in range(int(timeout_s * 1000)):
            if self.ack:
                break
            time.sleep(timeout_s / 1000)
        else:
            assert False, '{} never acked'.format(self.__class__.__name__)


class Injection:
    ''' Injection class which tracks all registered injectors
    '''
    def __init__(self):
        self.injectors = []

    def register(self, injector):
        assert issubclass(type(injector), Injector), (
            'Injectors must be a subclass of Injector')
        self.injectors.append(injector)

    def get(self, injector_type):
        ''' When a caller calls get on an Injection object, injectors
            are searched for and the first one found is returned and removed from
            the list of registered injectors
            injector_type is a string for the type of injector to look for. This makes it
            convinient to identify injectors without having them defined everywhere
        '''
        assert type(injector_type) is str, "injector_type must be a string"
        injectors = [i for i in self.injectors if i.__class__.__name__ == injector_type]
        if len(injectors) == 0:
            # Not found, return None
            return None
        else:
            injector = injectors[0]
            self.injectors.remove(injector)
            return injector
