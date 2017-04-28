from centralized_locking_system import *
import unittest


class ResourceSystemTests(unittest.TestCase):

    def setUp(self):
        self.system = ResourceSystem()

    def test_get_resources(self):
        self.assertEqual(self.system.get_resources(), [],
                         'get_resources does not return a list of resources')

    def test_get_system_state(self):
        self.assertEqual(self.system.get_system_state(), {},
                         'get_system_state does not return system state')

    def test_get_queues(self):
        self.assertEqual(self.system.get_queues(), {},
                         'get_system_state does not return the queues')

    def test_add_resource(self):
        self.system.add_resource('Resource 1')
        self.assertEqual(self.system.get_queues(), {'Resource 1': []},
                         'add_resource does not add resource to the queues')
        self.assertEqual(self.system.get_resources(), ['Resource 1'],
                         'add_resource does not add resource to the list of resources')
        self.assertEqual(self.system.get_system_state(), {'Resource 1': False},
                         'add_resource does not add resource to the locks')

        self.assertRaises(ResourceNameNotStringException, self.system.add_resource, 1)

        self.assertRaises(ResourceAlreadyInSystemException, self.system.add_resource, 'Resource 1')

    def test_remove_resource(self):
        self.system.add_resource('Resource 1')
        self.system.remove_resource('Resource 1')
        self.assertEqual(self.system.get_queues(), {},
                         'remove_resource does not remove resource from the queues')
        self.assertEqual(self.system.get_resources(), [],
                         'remove_resource does not remove resource from the list of resources')
        self.assertEqual(self.system.get_system_state(), {},
                         'remove_resource does not remove resource from the locks')

        self.assertRaises(ResourceNameNotStringException, self.system.remove_resource, 1)

        self.assertRaises(ResourceNonExistentException, self.system.remove_resource, '1')
        # test below assumes that access_resource works properly
        self.system.add_resource('Resource 1')
        self.system.access_resource('Resource 1', 'Service')
        self.assertRaises(ResourceInUseException, self.system.remove_resource, 'Resource 1')

    def test_access_resource(self):
        self.system.add_resource('Resource 1')
        self.system.access_resource('Resource 1', 'Service')
        self.assertEqual(self.system.get_system_state(), {'Resource 1': 'Service'},
                         'access_resource does not change the lock status')
        self.assertEqual(self.system.access_resource('Resource 1', 'Service'), False,
                         'access_resource does grant access to a used resource')
        self.assertEqual(self.system.get_queues(), {'Resource 1': ['Service']},
                         'access_resource does not add a service to the queue')

        self.system.add_resource('Resource 2')
        self.assertEqual(self.system.access_resource('Resource 2', 'Service'), True,
                         'access_resource does not grant the access to free resource')

        self.assertRaises(ResourceNameNotStringException, self.system.access_resource, 1, 'Service')

        self.assertRaises(ResourceNonExistentException, self.system.access_resource, '1', 'Service')

    def test_release_resource(self):
        self.system.add_resource('Resource 1')
        self.system.access_resource('Resource 1', 'Service')
        self.system.release_resource('Resource 1', 'Service')
        self.assertEqual(self.system.get_system_state(), {'Resource 1': False},
                         'release_resource does not change the lock status')

        self.system.add_resource('Resource 2')
        self.system.access_resource('Resource 2', 'Service')
        self.system.access_resource('Resource 2', 'Service2')
        self.system.release_resource('Resource 2', 'Service')
        self.assertEqual(self.system.get_system_state(), {'Resource 1': False, 'Resource 2': 'Service2'},
                         'release_resource does not grant access to the next resource in the queue')
        self.assertEqual(self.system.get_queues(), {'Resource 1': [], 'Resource 2': []},
                         'access_resource does not remove the service that just accessed the resource from the queue')

        self.assertRaises(ServiceIsNotCurrentlyUsingResourceException,
                          self.system.release_resource, 'Resource 1', 'Service2')

        self.assertRaises(ResourceNameNotStringException, self.system.release_resource, 1, 'Service')

        self.assertRaises(ResourceNonExistentException, self.system.release_resource, '1', 'Service')

        self.system.access_resource('Resource 1', 'Service2')

    def test_detect_simple_deadlocks(self):
        self.system.add_resource('Resource 1')
        self.system.add_resource('Resource 2')
        self.system.access_resource('Resource 1', 'Service 1')
        self.system.access_resource('Resource 2', 'Service 2')
        self.system.access_resource('Resource 2', 'Service 1')
        self.system.access_resource('Resource 1', 'Service 2')
        self.system.detect_simple_deadlocks()
        self.assertEqual(self.system.get_system_state(), {'Resource 1': 'Service 2', 'Resource 2': 'Service 2'},
                         'deadlock is not resolved')

    def test_detect_simple_deadlocks_2(self):
        self.system.add_resource('Resource 1')
        self.system.add_resource('Resource 2')
        self.system.access_resource('Resource 1', 'Service 1')
        self.system.access_resource('Resource 2', 'Service 2')
        self.system.detect_simple_deadlocks()
        self.assertEqual(self.system.get_system_state(), {'Resource 1': 'Service 1', 'Resource 2': 'Service 2'},
                         'deadlock detection removes the service, when there is no deadlock')


unittest.main(exit=False)
