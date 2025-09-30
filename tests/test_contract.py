import unittest
from scripts.deploy import ContractDeployer
from scripts.interact import ContractInteractor
import os
import tempfile


class TestSimpleStorage(unittest.TestCase):

    def setUp(self):
        """Set up test environment"""
        # You would typically use a test blockchain like Ganache
        self.deployer = ContractDeployer()

        # Mock addresses for testing
        self.test_address = "0x742286B2a9D7615F9a5e5b7C8b3F2b8f0F8D8E8F"
        self.test_private_key = "0x" + "0" * 64  # Don't use this in production!

    def test_contract_compilation(self):
        """Test that contract compiles successfully"""
        contract_interface = self.deployer.compile_contract('contracts/SimpleStorage.sol')

        self.assertIn('abi', contract_interface)
        self.assertIn('bin', contract_interface)
        self.assertTrue(len(contract_interface['bin']) > 0)

    def test_contract_has_required_functions(self):
        """Test that contract has all required functions"""
        contract_interface = self.deployer.compile_contract('contracts/SimpleStorage.sol')
        abi = contract_interface['abi']

        function_names = [item['name'] for item in abi if item['type'] == 'function']

        self.assertIn('set', function_names)
        self.assertIn('get', function_names)
        self.assertIn('getOwner', function_names)


if __name__ == '__main__':
    unittest.main()