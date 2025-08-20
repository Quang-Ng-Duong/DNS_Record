#!/usr/bin/env python3
"""
Unit tests for DNS Lookup Tool
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
import sys

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dns_lookup_class import DNSLookupTool, Colors


class TestDNSLookupTool(unittest.TestCase):
    """
    Test cases for DNSLookupTool class
    """
    
    def setUp(self):
        """
        Set up test fixtures
        """
        # Create a temporary config for testing
        self.test_config = {
            "dns_settings": {
                "timeout": 5,
                "retries": 2,
                "default_nameserver": None,
                "record_types": ["A", "MX", "NS"]
            },
            "display_settings": {
                "use_colors": False,
                "max_txt_length": 50,
                "table_format": True,
                "show_progress": False
            },
            "export_settings": {
                "json_indent": 2,
                "csv_delimiter": ",",
                "include_timestamp": False
            },
            "logging": {
                "level": "ERROR",
                "file": None,
                "max_size_mb": 1,
                "backup_count": 1,
                "format": "%(message)s"
            }
        }
        
        # Create tool instance with test config
        with patch.object(DNSLookupTool, 'load_config', return_value=self.test_config):
            self.dns_tool = DNSLookupTool()
    
    def test_validate_domain_valid(self):
        """
        Test domain validation with valid domains
        """
        valid_domains = [
            'google.com',
            'example.org',
            'sub.domain.com',
            'test-domain.net',
            'a.b.c.d.e.f'
        ]
        
        for domain in valid_domains:
            with self.subTest(domain=domain):
                self.assertTrue(self.dns_tool.validate_domain(domain))
    
    def test_validate_domain_invalid(self):
        """
        Test domain validation with invalid domains
        """
        invalid_domains = [
            '',
            None,
            'invalid..domain.com',
            '-invalid.com',
            'invalid-.com',
            'a' * 254,  # Too long
            'invalid domain.com',  # Space
            '.invalid.com',  # Leading dot
            'invalid.com.',  # Trailing dot (actually valid but our regex doesn't allow it)
        ]
        
        for domain in invalid_domains:
            with self.subTest(domain=domain):
                self.assertFalse(self.dns_tool.validate_domain(domain))
    
    def test_clean_domain(self):
        """
        Test domain cleaning functionality
        """
        test_cases = [
            ('http://example.com', 'example.com'),
            ('https://www.google.com', 'google.com'),
            ('www.test.org', 'test.org'),
            ('example.com/path/to/page', 'example.com'),
            ('https://www.example.com/path', 'example.com'),
            ('', ''),
            (None, None)
        ]
        
        for input_domain, expected in test_cases:
            with self.subTest(input_domain=input_domain):
                result = self.dns_tool.clean_domain(input_domain)
                self.assertEqual(result, expected)
    
    @patch('dns.resolver.Resolver.resolve')
    def test_fetch_record_type_success(self, mock_resolve):
        """
        Test successful DNS record fetching
        """
        # Mock DNS response for A record
        mock_record = MagicMock()
        mock_record.to_text.return_value = '192.168.1.1'
        mock_resolve.return_value = [mock_record]
        
        result = self.dns_tool.fetch_record_type('example.com', 'A', quiet=True)
        
        self.assertEqual(result, ['192.168.1.1'])
        mock_resolve.assert_called_once_with('example.com', 'A')
    
    @patch('dns.resolver.Resolver.resolve')
    def test_fetch_record_type_mx(self, mock_resolve):
        """
        Test MX record fetching
        """
        # Mock MX record
        mock_mx = MagicMock()
        mock_mx.preference = 10
        mock_mx.exchange.to_text.return_value = 'mail.example.com'
        mock_resolve.return_value = [mock_mx]
        
        result = self.dns_tool.fetch_record_type('example.com', 'MX', quiet=True)
        
        expected = [{'priority': 10, 'exchange': 'mail.example.com'}]
        self.assertEqual(result, expected)
    
    @patch('dns.resolver.Resolver.resolve')
    def test_fetch_record_type_soa(self, mock_resolve):
        """
        Test SOA record fetching
        """
        # Mock SOA record
        mock_soa = MagicMock()
        mock_soa.mname.to_text.return_value = 'ns1.example.com'
        mock_soa.rname.to_text.return_value = 'admin.example.com'
        mock_soa.serial = 2023010101
        mock_soa.refresh = 3600
        mock_soa.retry = 1800
        mock_soa.expire = 604800
        mock_soa.minimum = 86400
        mock_resolve.return_value = [mock_soa]
        
        result = self.dns_tool.fetch_record_type('example.com', 'SOA', quiet=True)
        
        expected = [{
            'mname': 'ns1.example.com',
            'rname': 'admin.example.com',
            'serial': 2023010101,
            'refresh': 3600,
            'retry': 1800,
            'expire': 604800,
            'minimum': 86400
        }]
        self.assertEqual(result, expected)
    
    @patch('dns.resolver.Resolver.resolve')
    def test_fetch_record_type_nxdomain(self, mock_resolve):
        """
        Test handling of non-existent domain
        """
        import dns.resolver
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()
        
        result = self.dns_tool.fetch_record_type('nonexistent.domain', 'A', quiet=True)
        
        self.assertIsNone(result)
    
    @patch('dns.resolver.Resolver.resolve')
    def test_fetch_record_type_no_answer(self, mock_resolve):
        """
        Test handling of no answer for record type
        """
        import dns.resolver
        mock_resolve.side_effect = dns.resolver.NoAnswer()
        
        result = self.dns_tool.fetch_record_type('example.com', 'AAAA', quiet=True)
        
        self.assertEqual(result, [])
    
    def test_export_to_json(self):
        """
        Test JSON export functionality
        """
        test_data = {
            'A_Records': ['192.168.1.1', '192.168.1.2'],
            'MX_Records': [{'priority': 10, 'exchange': 'mail.example.com'}]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_filename = f.name
        
        try:
            # Capture stdout to suppress print statements
            with patch('sys.stdout'):
                self.dns_tool.export_to_json(test_data, temp_filename)
            
            # Verify file was created and contains correct data
            with open(temp_filename, 'r') as f:
                exported_data = json.load(f)
            
            self.assertEqual(exported_data['A_Records'], test_data['A_Records'])
            self.assertEqual(exported_data['MX_Records'], test_data['MX_Records'])
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_export_to_csv(self):
        """
        Test CSV export functionality
        """
        test_data = {
            'A_Records': ['192.168.1.1'],
            'MX_Records': [{'priority': 10, 'exchange': 'mail.example.com'}]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_filename = f.name
        
        try:
            # Capture stdout to suppress print statements
            with patch('sys.stdout'):
                self.dns_tool.export_to_csv(test_data, temp_filename)
            
            # Verify file was created
            self.assertTrue(os.path.exists(temp_filename))
            
            # Read and verify content
            with open(temp_filename, 'r') as f:
                content = f.read()
                self.assertIn('A_Records', content)
                self.assertIn('192.168.1.1', content)
                self.assertIn('MX_Records', content)
                self.assertIn('mail.example.com', content)
                self.assertIn('Priority: 10', content)
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_colors_disable(self):
        """
        Test color disabling functionality
        """
        # Save original values
        original_red = Colors.RED
        original_end = Colors.END
        
        # Disable colors
        Colors.disable()
        
        # Check that colors are disabled
        self.assertEqual(Colors.RED, '')
        self.assertEqual(Colors.END, '')
        
        # Restore original values for other tests
        Colors.RED = original_red
        Colors.END = original_end


class TestConfigLoading(unittest.TestCase):
    """
    Test configuration loading functionality
    """
    
    def test_load_config_file_exists(self):
        """
        Test loading configuration from existing file
        """
        test_config = {
            "dns_settings": {
                "timeout": 15,
                "retries": 5
            }
        }
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(test_config))):
                dns_tool = DNSLookupTool('test_config.json')
                
                # Should merge with defaults
                self.assertEqual(dns_tool.config['dns_settings']['timeout'], 15)
                self.assertEqual(dns_tool.config['dns_settings']['retries'], 5)
                # Should have default values for missing keys
                self.assertIn('record_types', dns_tool.config['dns_settings'])
    
    def test_load_config_file_not_exists(self):
        """
        Test loading configuration when file doesn't exist
        """
        with patch('os.path.exists', return_value=False):
            dns_tool = DNSLookupTool('nonexistent_config.json')
            
            # Should use default configuration
            self.assertEqual(dns_tool.config['dns_settings']['timeout'], 10)
            self.assertIn('record_types', dns_tool.config['dns_settings'])


if __name__ == '__main__':
    # Disable colors for testing
    Colors.disable()
    
    # Run tests
    unittest.main(verbosity=2)
