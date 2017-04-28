class ResourceNonExistentException(Exception):
    """
    raised when trying to access non-existent resource
    """


class ResourceNameNotStringException(Exception):
    """
    raised when trying to use a resource name that is not a string
    """


class ResourceAlreadyInSystemException(Exception):
    """
    raised when trying to add already existing resource to the system
    """


class ResourceInUseException(Exception):
    """
    raised when trying to remove resource in use from the system
    """


class ServiceIsNotCurrentlyUsingResourceException(Exception):
    """
    raised when trying to release a resource not currently used by given service
    """


class ResourceSystem(object):
    """
    implements central locking system
    """
    def __init__(self):
        """
        Initialize a ResourceSystem instance
        queues: a dictionary with keys as resources names and values as queues in form of lists.
        The queues show the services waiting for each resource. Initially, the queues are empty
        locks: a dictionary with keys as resource names (str) as lock states as values.
        False represents free resource. If the value == service name, then this service is using the resource.
        """
        self.locks = {}
        self.queues = {}

    def get_resources(self):
        """
        :return: list of all resources in the system
        """
        return list(self.locks.keys())

    def get_system_state(self):
        """
        :return: a dictionary with keys as resource names (str) as lock states (bool) as values.
        True represents locked resource.
        """
        return self.locks

    def get_queues(self):
        """
        :return: a dictionary with keys as resources names and values as queues in form of lists.
        The queues show the services waiting for each resource. Initially, the queues are empty
        """
        return self.queues

    def add_resource(self, resource_name):
        """
        adds resource to a resource system. resource name must be a string
        :param resource_name: name of a particular resource (string).
        :return: None
        """
        if type(resource_name) == str:
            if resource_name in self.locks.keys():
                raise ResourceAlreadyInSystemException
            else:
                self.locks[resource_name] = False
                self.queues[resource_name] = []
        else:
            raise ResourceNameNotStringException

    def remove_resource(self, resource_name):
        """
        removes resource to a resource system. resource name must be a string
        :param resource_name: name of a particular resource (string).
        :return: None
        """
        if type(resource_name) == str:
            if resource_name in self.locks.keys():
                if self.locks[resource_name]:
                    raise ResourceInUseException
                else:
                    del self.locks[resource_name]
                    del self.queues[resource_name]
            else:
                raise ResourceNonExistentException
        else:
            raise ResourceNameNotStringException

    def access_resource(self, resource_name, service):
        """
        service tries to access resource with resource_name, if resource is free, it is given access,
        else it is put in the queue. resource name must be a string
        :param resource_name: name of a particular resource (string). 
        :param service: name of a service. String preferred, but other types are also accepted
        :return: True if access is granted, False otherwise
        """
        if type(resource_name) == str:
            if resource_name in self.locks.keys():
                if self.locks[resource_name]:
                    self.queues[resource_name].append(service)
                    # add timeout in queue
                    return False
                else:
                    self.locks[resource_name] = service
                    # add timeout for accesing
                    return True
            else:
                raise ResourceNonExistentException
        else:
            raise ResourceNameNotStringException

    def release_resource(self, resource_name, service):
        """
        service curently using the resource releases the resource. resource name must be a string.
        next service in the queue automatically accesses the resource
        :param resource_name: name of a particular resource (string).
        :param service: name of a service. String preferred, but other types are also accepted
        :return: None
        """

        if type(resource_name) == str:
            if resource_name in self.locks.keys():
                if self.locks[resource_name] == service:
                    self.locks[resource_name] = False
                    if self.queues[resource_name]:  # list is not empty
                        self.access_resource(resource_name, self.queues[resource_name][0])
                        self.queues[resource_name].pop(0)
                else:
                    raise ServiceIsNotCurrentlyUsingResourceException
            else:
                raise ResourceNonExistentException
        else:
            raise ResourceNameNotStringException

    def detect_simple_deadlocks(self):
        """
        detects simple - non circular deadlocks. does not detect more complex deadlocks
        :return: None
        """
        for key, value in self.locks.items():
            if value:  # resource is used
                for key_q, value_q in self.queues.items():
                    if value_q:  # queue is not empty
                        if value in value_q:  # service using a resource is also waiting for another resource
                            # deadlock is possible
                            service_2 = self.locks[key_q]  # service using the resource the 1st service is waiting for
                            if service_2 in self.queues[key]:  # service 2 is waiting for res. being used by serv 1
                                # deadlock detected
                                # resolve deadlock by releasing first resource
                                self.release_resource(key, value)
