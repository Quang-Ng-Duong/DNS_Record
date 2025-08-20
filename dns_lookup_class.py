#!/usr/bin/env python3
"""
Enhanced DNS Record Lookup Tool - Class-based Architecture
A comprehensive DNS lookup tool with modern features and clean architecture.

Author: Quang-Ng-Duong (Enhanced Version)
"""

import dns.resolver
import re
import sys
import argparse
import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @staticmethod
    def disable():
        """Disable colors for non-terminal output"""
        Colors.RED = Colors.GREEN = Colors.YELLOW = ''
        Colors.BLUE = Colors.MAGENTA = Colors.CYAN = ''
        Colors.WHITE = Colors.BOLD = Colors.UNDERLINE = Colors.END = ''

class DNSLookupTool:
    """
    Enhanced DNS Lookup Tool with comprehensive features
    """
    
    def __init__(self, config_file='config.json'):
        """
        Initialize the DNS lookup tool
        """
        self.config = self.load_config(config_file)
        self.logger = self.setup_logging()
        self.dns_resolver = dns.resolver.Resolver()
        
        # Configure DNS resolver
        dns_config = self.config['dns_settings']
        self.dns_resolver.timeout = dns_config['timeout']
        self.dns_resolver.lifetime = dns_config['timeout']
        
        if dns_config['default_nameserver']:
            self.dns_resolver.nameservers = [dns_config['default_nameserver']]
    
    def load_config(self, config_file):
        """
        Load configuration from JSON file
        """
        default_config = {
            "dns_settings": {
                "timeout": 10,
                "retries": 3,
                "default_nameserver": None,
                "record_types": ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"]
            },
            "display_settings": {
                "use_colors": True,
                "max_txt_length": 70,
                "table_format": True,
                "show_progress": True
            },
            "export_settings": {
                "json_indent": 2,
                "csv_delimiter": ",",
                "include_timestamp": True
            },
            "logging": {
                "level": "INFO",
                "file": "dns_lookup.log",
                "max_size_mb": 10,
                "backup_count": 3,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for section in default_config:
                        if section not in config:
                            config[section] = default_config[section]
                        else:
                            for key in default_config[section]:
                                if key not in config[section]:
                                    config[section][key] = default_config[section][key]
                    return config
        except Exception as e:
            print(f"Warning: Could not load {config_file}: {e}")
        
        return default_config
    
    def setup_logging(self):
        """
        Setup logging based on configuration
        """
        log_config = self.config['logging']
        
        # Create logger
        logger = logging.getLogger('dns_lookup')
        logger.setLevel(getattr(logging, log_config['level']))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(log_config['format'])
        
        # Create rotating file handler
        if log_config['file']:
            file_handler = RotatingFileHandler(
                log_config['file'],
                maxBytes=log_config['max_size_mb'] * 1024 * 1024,
                backupCount=log_config['backup_count']
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def validate_domain(self, domain):
        """
        Validate domain name format
        """
        if not domain or len(domain) > 253:
            return False
        
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, domain))
    
    def clean_domain(self, domain):
        """
        Clean domain name by removing protocols and www
        """
        if not domain:
            return domain
        
        domain = domain.strip()
        domain = domain.replace('http://', '').replace('https://', '')
        domain = domain.replace('www.', '')
        domain = domain.split('/')[0]  # Remove path if present
        
        return domain
    
    def fetch_record_type(self, website, record_type, quiet=False):
        """
        Fetch a specific DNS record type
        """
        try:
            if not quiet and self.config['display_settings']['show_progress']:
                emoji_map = {
                    'A': '📍', 'AAAA': '📍', 'CNAME': '🔗', 'MX': '📧',
                    'NS': '🌐', 'TXT': '📝', 'SOA': '⚡'
                }
                emoji = emoji_map.get(record_type, '🔍')
                print(f"{Colors.CYAN}{emoji} Fetching {record_type} records...{Colors.END}")
            
            records = self.dns_resolver.resolve(website, record_type)
            record_list = []
            
            if record_type == 'MX':
                for server in records:
                    record_list.append({
                        'priority': server.preference,
                        'exchange': server.exchange.to_text()
                    })
            elif record_type == 'SOA':
                for soa in records:
                    record_list.append({
                        'mname': soa.mname.to_text(),
                        'rname': soa.rname.to_text(),  # responsible name
                        'serial': soa.serial,
                        'refresh': soa.refresh,
                        'retry': soa.retry,
                        'expire': soa.expire,
                        'minimum': soa.minimum
                    })
            else:
                for record in records:
                    record_list.append(record.to_text())
            
            if not quiet and self.config['display_settings']['show_progress']:
                print(f"{Colors.GREEN}✅ Found {len(record_list)} {record_type} record(s){Colors.END}")
            
            self.logger.info(f"Successfully fetched {len(record_list)} {record_type} records for {website}")
            return record_list
            
        except dns.resolver.NXDOMAIN:
            if not quiet:
                print(f"{Colors.RED}❌ Domain {website} does not exist{Colors.END}")
            self.logger.error(f"Domain {website} does not exist")
            return None
        except dns.resolver.NoAnswer:
            if not quiet and self.config['display_settings']['show_progress']:
                print(f"{Colors.YELLOW}⚠️  No {record_type} records found{Colors.END}")
            self.logger.info(f"No {record_type} records found for {website}")
            return []
        except Exception as e:
            if not quiet:
                print(f"{Colors.RED}❌ Error fetching {record_type} records: {e}{Colors.END}")
            self.logger.error(f"Error fetching {record_type} records for {website}: {e}")
            return []
    
    def get_dns_records(self, website, record_types=None, quiet=False):
        """
        Fetch comprehensive DNS records for a website
        """
        website = self.clean_domain(website)
        
        if not self.validate_domain(website):
            if not quiet:
                print(f"{Colors.RED}❌ Invalid domain format: {website}{Colors.END}")
            self.logger.error(f"Invalid domain format: {website}")
            return None
        
        if not quiet:
            print(f"{Colors.BOLD}{Colors.BLUE}🔍 Querying DNS records for: {Colors.UNDERLINE}{website}{Colors.END}")
            print(f"{Colors.BLUE}{'-' * 60}{Colors.END}")
        
        # Use provided record types or default from config
        if not record_types:
            record_types = self.config['dns_settings']['record_types']
        
        dns_record = {}
        domain_exists = False
        
        for record_type in record_types:
            result = self.fetch_record_type(website, record_type, quiet)
            
            if result is None:  # Domain doesn't exist
                return None
            elif result:  # Records found
                domain_exists = True
                dns_record[f'{record_type}_Records'] = result
            else:  # No records of this type
                dns_record[f'{record_type}_Records'] = []
        
        if not domain_exists and not quiet:
            print(f"{Colors.YELLOW}⚠️  Domain {website} exists but has no standard DNS records{Colors.END}")
        
        self.logger.info(f"DNS lookup completed for {website}")
        return dns_record

    def display_records(self, dns_record):
        """
        Display DNS records in a beautifully formatted way
        """
        if not dns_record:
            return

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}🌐 COMPREHENSIVE DNS RECORDS SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * 80}{Colors.END}")

        # Display A records (IPv4)
        if dns_record.get('A_Records'):
            print(f"\n{Colors.BOLD}{Colors.GREEN}📍 A Records (IPv4 Addresses):{Colors.END}")
            for i, ip in enumerate(dns_record['A_Records'], 1):
                print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.WHITE}{ip}{Colors.END}")

        # Display AAAA records (IPv6)
        if dns_record.get('AAAA_Records'):
            print(f"\n{Colors.BOLD}{Colors.GREEN}📍 AAAA Records (IPv6 Addresses):{Colors.END}")
            for i, ip in enumerate(dns_record['AAAA_Records'], 1):
                print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.WHITE}{ip}{Colors.END}")

        # Display CNAME records
        if dns_record.get('CNAME_Records'):
            print(f"\n{Colors.BOLD}{Colors.BLUE}🔗 CNAME Records (Canonical Names):{Colors.END}")
            for i, cname in enumerate(dns_record['CNAME_Records'], 1):
                print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.WHITE}{cname}{Colors.END}")

        # Display MX records with table format
        if dns_record.get('MX_Records'):
            print(f"\n{Colors.BOLD}{Colors.YELLOW}📧 MX Records (Mail Servers):{Colors.END}")
            if self.config['display_settings']['table_format']:
                print(f"   ┌─────────────┬─────────────────────────────────────────────────┐")
                print(f"   │ {Colors.BOLD}Priority{Colors.END}     │ {Colors.BOLD}Mail Server{Colors.END}                                  │")
                print(f"   ├─────────────┼─────────────────────────────────────────────────┤")
                for mx in dns_record['MX_Records']:
                    priority = str(mx['priority'])
                    server = mx['exchange'][:45] + "..." if len(mx['exchange']) > 45 else mx['exchange']
                    print(f"   │ {Colors.CYAN}{priority:<11}{Colors.END} │ {Colors.WHITE}{server:<47}{Colors.END} │")
                print(f"   └─────────────┴─────────────────────────────────────────────────┘")
            else:
                for i, mx in enumerate(dns_record['MX_Records'], 1):
                    print(f"   {Colors.CYAN}{i}.{Colors.END} Priority: {Colors.WHITE}{mx['priority']}{Colors.END}, Server: {Colors.WHITE}{mx['exchange']}{Colors.END}")

        # Display NS records
        if dns_record.get('NS_Records'):
            print(f"\n{Colors.BOLD}{Colors.MAGENTA}🌐 NS Records (Name Servers):{Colors.END}")
            for i, ns in enumerate(dns_record['NS_Records'], 1):
                print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.WHITE}{ns}{Colors.END}")

        # Display TXT records
        if dns_record.get('TXT_Records'):
            print(f"\n{Colors.BOLD}{Colors.CYAN}📝 TXT Records (Text Records):{Colors.END}")
            max_length = self.config['display_settings']['max_txt_length']
            for i, txt in enumerate(dns_record['TXT_Records'], 1):
                display_txt = txt if len(txt) <= max_length else txt[:max_length-3] + "..."
                print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.WHITE}{display_txt}{Colors.END}")

        # Display SOA records
        if dns_record.get('SOA_Records'):
            print(f"\n{Colors.BOLD}{Colors.RED}⚡ SOA Records (Start of Authority):{Colors.END}")
            for i, soa in enumerate(dns_record['SOA_Records'], 1):
                print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.BOLD}Primary NS:{Colors.END} {Colors.WHITE}{soa['mname']}{Colors.END}")
                print(f"      {Colors.BOLD}Responsible:{Colors.END} {Colors.WHITE}{soa['rname']}{Colors.END}")
                print(f"      {Colors.BOLD}Serial:{Colors.END} {Colors.WHITE}{soa['serial']}{Colors.END}")
                print(f"      {Colors.BOLD}Refresh:{Colors.END} {Colors.WHITE}{soa['refresh']}s{Colors.END}, {Colors.BOLD}Retry:{Colors.END} {Colors.WHITE}{soa['retry']}s{Colors.END}")
                print(f"      {Colors.BOLD}Expire:{Colors.END} {Colors.WHITE}{soa['expire']}s{Colors.END}, {Colors.BOLD}Minimum:{Colors.END} {Colors.WHITE}{soa['minimum']}s{Colors.END}")

        # Check if any records were found
        has_records = any(dns_record.get(f'{record_type}_Records')
                         for record_type in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA'])

        if not has_records:
            print(f"\n{Colors.YELLOW}⚠️  No DNS records found for this domain{Colors.END}")

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * 80}{Colors.END}")

    def export_to_json(self, dns_record, filename):
        """
        Export DNS records to JSON file
        """
        try:
            export_data = dns_record.copy()
            if self.config['export_settings']['include_timestamp']:
                export_data['export_timestamp'] = datetime.now().isoformat()

            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=self.config['export_settings']['json_indent'])

            print(f"{Colors.GREEN}✅ DNS records exported to {filename}{Colors.END}")
            self.logger.info(f"DNS records exported to JSON: {filename}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error exporting to JSON: {e}{Colors.END}")
            self.logger.error(f"Error exporting to JSON: {e}")

    def export_to_csv(self, dns_record, filename):
        """
        Export DNS records to CSV file
        """
        try:
            import csv
            delimiter = self.config['export_settings']['csv_delimiter']

            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=delimiter)

                # Write header
                headers = ['Record Type', 'Value', 'Additional Info']
                if self.config['export_settings']['include_timestamp']:
                    headers.append('Export Time')
                writer.writerow(headers)

                export_time = datetime.now().isoformat() if self.config['export_settings']['include_timestamp'] else None

                for record_type, records in dns_record.items():
                    if records:
                        for record in records:
                            row = [record_type]
                            if isinstance(record, dict):
                                if 'exchange' in record:  # MX record
                                    row.extend([record['exchange'], f"Priority: {record['priority']}"])
                                elif 'mname' in record:  # SOA record
                                    row.extend([record['mname'], f"Serial: {record['serial']}"])
                                else:
                                    row.extend([str(record), ''])
                            else:
                                row.extend([record, ''])

                            if export_time:
                                row.append(export_time)
                            writer.writerow(row)

            print(f"{Colors.GREEN}✅ DNS records exported to {filename}{Colors.END}")
            self.logger.info(f"DNS records exported to CSV: {filename}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error exporting to CSV: {e}{Colors.END}")
            self.logger.error(f"Error exporting to CSV: {e}")

    def run_interactive(self):
        """
        Run the tool in interactive mode
        """
        print(f"{Colors.BOLD}{Colors.BLUE}🔧 Enhanced DNS Record Lookup Tool{Colors.END}")
        print(f"{Colors.BLUE}{'=' * 50}{Colors.END}")

        try:
            website = input(f"{Colors.CYAN}Enter the domain name (e.g., google.com): {Colors.END}").strip()

            if not website:
                print(f"{Colors.RED}❌ Please enter a valid domain name{Colors.END}")
                return

            dns_record = self.get_dns_records(website)
            if dns_record:
                self.display_records(dns_record)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 Program interrupted by user{Colors.END}")

    def run_cli(self, domain, record_types=None, export_json=None, export_csv=None, quiet=False):
        """
        Run the tool with command line arguments
        """
        if not quiet:
            print(f"{Colors.BOLD}{Colors.BLUE}🔧 Enhanced DNS Record Lookup Tool{Colors.END}")
            print(f"{Colors.BLUE}{'=' * 50}{Colors.END}")

        try:
            dns_record = self.get_dns_records(domain, record_types, quiet)

            if not dns_record:
                return

            # Display results
            if not quiet:
                self.display_records(dns_record)

            # Export if requested
            if export_json:
                self.export_to_json(dns_record, export_json)

            if export_csv:
                self.export_to_csv(dns_record, export_csv)

        except Exception as e:
            print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
            self.logger.error(f"Unexpected error: {e}")


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Enhanced DNS Record Lookup Tool - Class-based Architecture',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dns_lookup_class.py google.com
  python dns_lookup_class.py google.com --records A MX
  python dns_lookup_class.py google.com --export-json results.json
  python dns_lookup_class.py google.com --export-csv results.csv
  python dns_lookup_class.py --interactive
        """
    )

    parser.add_argument('domain', nargs='?', help='Domain name to lookup (e.g., google.com)')
    parser.add_argument('--records', '-r', nargs='+',
                       choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA'],
                       help='Specific record types to fetch (default: all)')
    parser.add_argument('--export-json', '-j', metavar='FILE',
                       help='Export results to JSON file')
    parser.add_argument('--export-csv', '-c', metavar='FILE',
                       help='Export results to CSV file')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress progress messages')
    parser.add_argument('--config', metavar='FILE', default='config.json',
                       help='Configuration file path (default: config.json)')

    return parser.parse_args()


def main():
    """
    Main function
    """
    args = parse_arguments()

    # Disable colors if output is redirected or quiet mode
    if args.quiet or not sys.stdout.isatty():
        Colors.disable()

    # Create DNS lookup tool instance
    dns_tool = DNSLookupTool(args.config)

    # Determine mode
    if args.interactive or not args.domain:
        dns_tool.run_interactive()
    else:
        dns_tool.run_cli(
            domain=args.domain,
            record_types=args.records,
            export_json=args.export_json,
            export_csv=args.export_csv,
            quiet=args.quiet
        )


if __name__ == "__main__":
    main()
