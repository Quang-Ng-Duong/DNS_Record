#!/usr/bin/env python3
"""
Demo script for Enhanced DNS Record Lookup Tool
Demonstrates various features and capabilities
"""

import sys
import os
from dns_lookup_class import DNSLookupTool, Colors

def demo_basic_lookup():
    """
    Demonstrate basic DNS lookup functionality
    """
    print(f"{Colors.BOLD}{Colors.BLUE}=== DEMO: Basic DNS Lookup ==={Colors.END}")
    
    dns_tool = DNSLookupTool()
    
    # Test domains
    test_domains = ['google.com', 'github.com', 'stackoverflow.com']  # noqa: spelling
    
    for domain in test_domains:
        print(f"\n{Colors.CYAN}Testing domain: {domain}{Colors.END}")
        dns_records = dns_tool.get_dns_records(domain, quiet=True)
        
        if dns_records:
            # Count records
            total_records = sum(len(records) for records in dns_records.values() if records)
            print(f"{Colors.GREEN}✅ Found {total_records} total DNS records{Colors.END}")
            
            # Show summary
            for record_type, records in dns_records.items():
                if records:
                    print(f"   {record_type}: {len(records)} record(s)")
        else:
            print(f"{Colors.RED}❌ Failed to lookup {domain}{Colors.END}")

def demo_specific_records():
    """
    Demonstrate lookup of specific record types
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== DEMO: Specific Record Types ==={Colors.END}")
    
    dns_tool = DNSLookupTool()
    
    # Test specific record types
    domain = 'google.com'
    record_types = ['A', 'MX', 'NS']
    
    print(f"\n{Colors.CYAN}Looking up {', '.join(record_types)} records for {domain}{Colors.END}")
    
    dns_records = dns_tool.get_dns_records(domain, record_types=record_types, quiet=True)
    
    if dns_records:
        dns_tool.display_records(dns_records)

def demo_export_functionality():
    """
    Demonstrate export capabilities
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== DEMO: Export Functionality ==={Colors.END}")
    
    dns_tool = DNSLookupTool()
    
    domain = 'example.com'
    print(f"\n{Colors.CYAN}Exporting DNS records for {domain}{Colors.END}")
    
    dns_records = dns_tool.get_dns_records(domain, quiet=True)
    
    if dns_records:
        # Export to JSON
        json_file = 'demo_export.json'
        dns_tool.export_to_json(dns_records, json_file)
        
        # Export to CSV
        csv_file = 'demo_export.csv'
        dns_tool.export_to_csv(dns_records, csv_file)
        
        print(f"{Colors.GREEN}✅ Exported to {json_file} and {csv_file}{Colors.END}")
        
        # Clean up demo files
        try:
            os.remove(json_file)
            os.remove(csv_file)
            print(f"{Colors.YELLOW}🧹 Cleaned up demo files{Colors.END}")
        except:
            pass

def demo_error_handling():
    """
    Demonstrate error handling capabilities
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== DEMO: Error Handling ==={Colors.END}")
    
    dns_tool = DNSLookupTool()
    
    # Test invalid domains
    invalid_domains = [
        'nonexistent-domain-12345.com',
        'invalid..domain.com',
        '',
        'a' * 300  # Too long
    ]
    
    for domain in invalid_domains:
        print(f"\n{Colors.CYAN}Testing invalid domain: '{domain[:50]}{'...' if len(domain) > 50 else ''}'{Colors.END}")
        
        if not dns_tool.validate_domain(domain):
            print(f"{Colors.YELLOW}⚠️  Domain validation failed (as expected){Colors.END}")
            continue
        
        dns_records = dns_tool.get_dns_records(domain, quiet=True)
        if not dns_records:
            print(f"{Colors.YELLOW}⚠️  DNS lookup failed (as expected){Colors.END}")

def demo_domain_cleaning():
    """
    Demonstrate domain cleaning functionality
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== DEMO: Domain Cleaning ==={Colors.END}")
    
    dns_tool = DNSLookupTool()
    
    # Test domain cleaning
    test_inputs = [
        'http://www.google.com',
        'https://github.com/user/repo',
        'www.example.org',
        'example.com/path/to/page'
    ]
    
    for input_domain in test_inputs:
        cleaned = dns_tool.clean_domain(input_domain)
        print(f"{Colors.CYAN}Input:{Colors.END} {input_domain}")
        print(f"{Colors.GREEN}Cleaned:{Colors.END} {cleaned}")
        print()

def demo_configuration():
    """
    Demonstrate configuration capabilities
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== DEMO: Configuration ==={Colors.END}")
    
    dns_tool = DNSLookupTool()
    
    print(f"{Colors.CYAN}Current Configuration:{Colors.END}")
    print(f"DNS Timeout: {dns_tool.config['dns_settings']['timeout']}s")
    print(f"Max TXT Length: {dns_tool.config['display_settings']['max_txt_length']}")
    print(f"Use Colors: {dns_tool.config['display_settings']['use_colors']}")
    print(f"Table Format: {dns_tool.config['display_settings']['table_format']}")
    print(f"Log Level: {dns_tool.config['logging']['level']}")

def main():
    """
    Run all demos
    """
    print(f"{Colors.BOLD}{Colors.MAGENTA}🚀 Enhanced DNS Record Lookup Tool - DEMO{Colors.END}")
    print(f"{Colors.MAGENTA}{'=' * 60}{Colors.END}")
    
    try:
        # Run demos
        demo_basic_lookup()
        demo_specific_records()
        demo_export_functionality()
        demo_error_handling()
        demo_domain_cleaning()
        demo_configuration()
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Demo completed successfully!{Colors.END}")
        print(f"{Colors.GREEN}Try running the tool yourself:{Colors.END}")
        print(f"  {Colors.CYAN}python dns_lookup_class.py google.com{Colors.END}")
        print(f"  {Colors.CYAN}python dns_lookup_class.py --interactive{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Demo interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Demo error: {e}{Colors.END}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Check if dnspython is available
    try:
        import dns.resolver
    except ImportError:
        print(f"{Colors.RED}❌ Error: dnspython is not installed{Colors.END}")
        print(f"{Colors.CYAN}Please install it with: pip install dnspython{Colors.END}")
        sys.exit(1)
    
    sys.exit(main())
