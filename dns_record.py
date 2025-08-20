#Enhanced DNS Record Lookup Tool
#Improved version with error handling, validation, and better functionality

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

def load_config():
    """
    Load configuration from config.json file
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
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # levelname is a valid Python logging format specifier  # cspell:ignore levelname
        }
    }

    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
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
        print(f"Warning: Could not load config.json: {e}")

    return default_config

def setup_logging(config):
    """
    Setup logging based on configuration
    """
    log_config = config['logging']

    # Create logger
    logger = logging.getLogger('dns_lookup')
    logger.setLevel(getattr(logging, log_config['level']))

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

    # Create console handler for errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def validate_domain(domain):
    """
    Validate domain name format
    Returns True if valid, False otherwise
    """
    # Basic domain validation regex
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'

    if not domain or len(domain) > 253:
        return False

    return bool(re.match(domain_pattern, domain))

def fetch_record_type(website, record_type, description, emoji, quiet=False):
    """
    Generic function to fetch a specific DNS record type with colored output
    """
    try:
        if not quiet:
            print(f"{Colors.CYAN}{emoji} Fetching {record_type} records...{Colors.END}")
        records = dns.resolver.resolve(website, record_type)
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
                    'rname': soa.rname.to_text(),  # responsible name (email address) # noqa: SC100
                    'serial': soa.serial,
                    'refresh': soa.refresh,
                    'retry': soa.retry,
                    'expire': soa.expire,
                    'minimum': soa.minimum
                })
        else:
            for record in records:
                record_list.append(record.to_text())

        if not quiet:
            print(f"{Colors.GREEN}✅ Found {len(record_list)} {record_type} record(s){Colors.END}")
        return record_list

    except dns.resolver.NXDOMAIN:  # Non-Existent Domain
        if not quiet:
            print(f"{Colors.RED}❌ Domain {website} does not exist{Colors.END}")
        return None
    except dns.resolver.NoAnswer:
        if not quiet:
            print(f"{Colors.YELLOW}⚠️  No {record_type} records found{Colors.END}")
        return []
    except Exception as e:
        if not quiet:
            print(f"{Colors.RED}❌ Error fetching {record_type} records: {e}{Colors.END}")
        return []

def get_dns_records(website, quiet=False):
    """
    Fetch comprehensive DNS records for a given website with colored output
    Returns dictionary with DNS records or None if failed
    """
    dns_record = {}

    if not validate_domain(website):
        if not quiet:
            print(f"{Colors.RED}❌ Invalid domain format: {website}{Colors.END}")
        return None

    if not quiet:
        print(f"{Colors.BOLD}{Colors.BLUE}🔍 Querying DNS records for: {Colors.UNDERLINE}{website}{Colors.END}")
        print(f"{Colors.BLUE}{'-' * 60}{Colors.END}")

    # Define record types to fetch
    record_types = [
        ('A', 'IPv4 Addresses', '📍'),
        ('AAAA', 'IPv6 Addresses', '📍'),
        ('CNAME', 'Canonical Names', '🔗'),
        ('MX', 'Mail Servers', '📧'),
        ('NS', 'Name Servers', '🌐'),
        ('TXT', 'Text Records', '📝'),
        ('SOA', 'Start of Authority', '⚡')
    ]

    domain_exists = False

    for record_type, description, emoji in record_types:
        result = fetch_record_type(website, record_type, description, emoji, quiet)

        if result is None:  # Domain doesn't exist
            return None
        elif result:  # Records found
            domain_exists = True
            dns_record[f'{record_type}_Records'] = result
        else:  # No records of this type
            dns_record[f'{record_type}_Records'] = []

    if not domain_exists and not quiet:
        print(f"{Colors.YELLOW}⚠️  Domain {website} exists but has no standard DNS records{Colors.END}")

    return dns_record

def create_table_row(columns, widths):
    """
    Create a formatted table row
    """
    row = "│"
    for i, (col, width) in enumerate(zip(columns, widths)):
        row += f" {str(col):<{width}} │"
    return row

def display_records(dns_record):
    """
    Display DNS records in a beautifully formatted way with colors and tables
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
        print(f"   ┌─────────────┬─────────────────────────────────────────────────┐")
        print(f"   │ {Colors.BOLD}Priority{Colors.END}     │ {Colors.BOLD}Mail Server{Colors.END}                                  │")
        print(f"   ├─────────────┼─────────────────────────────────────────────────┤")
        for mx in dns_record['MX_Records']:
            priority = str(mx['priority'])
            server = mx['exchange'][:45] + "..." if len(mx['exchange']) > 45 else mx['exchange']
            print(f"   │ {Colors.CYAN}{priority:<11}{Colors.END} │ {Colors.WHITE}{server:<47}{Colors.END} │")
        print(f"   └─────────────┴─────────────────────────────────────────────────┘")

    # Display NS records
    if dns_record.get('NS_Records'):
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}🌐 NS Records (Name Servers):{Colors.END}")
        for i, ns in enumerate(dns_record['NS_Records'], 1):
            print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.WHITE}{ns}{Colors.END}")

    # Display TXT records
    if dns_record.get('TXT_Records'):
        print(f"\n{Colors.BOLD}{Colors.CYAN}📝 TXT Records (Text Records):{Colors.END}")
        for i, txt in enumerate(dns_record['TXT_Records'], 1):
            # Truncate very long TXT records for display
            display_txt = txt if len(txt) <= 70 else txt[:67] + "..."
            print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.WHITE}{display_txt}{Colors.END}")

    # Display SOA records
    if dns_record.get('SOA_Records'):
        print(f"\n{Colors.BOLD}{Colors.RED}⚡ SOA Records (Start of Authority):{Colors.END}")
        for i, soa in enumerate(dns_record['SOA_Records'], 1):
            print(f"   {Colors.CYAN}{i}.{Colors.END} {Colors.BOLD}Primary NS:{Colors.END} {Colors.WHITE}{soa['mname']}{Colors.END}")
            print(f"      {Colors.BOLD}Responsible:{Colors.END} {Colors.WHITE}{soa['rname']}{Colors.END}")  # responsible person's email address
            print(f"      {Colors.BOLD}Serial:{Colors.END} {Colors.WHITE}{soa['serial']}{Colors.END}")
            print(f"      {Colors.BOLD}Refresh:{Colors.END} {Colors.WHITE}{soa['refresh']}s{Colors.END}, {Colors.BOLD}Retry:{Colors.END} {Colors.WHITE}{soa['retry']}s{Colors.END}")
            print(f"      {Colors.BOLD}Expire:{Colors.END} {Colors.WHITE}{soa['expire']}s{Colors.END}, {Colors.BOLD}Minimum:{Colors.END} {Colors.WHITE}{soa['minimum']}s{Colors.END}")

    # Check if any records were found
    has_records = any(dns_record.get(f'{record_type}_Records')
                     for record_type in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA'])

    if not has_records:
        print(f"\n{Colors.YELLOW}⚠️  No DNS records found for this domain{Colors.END}")

    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * 80}{Colors.END}")

def export_to_json(dns_record, filename):
    """
    Export DNS records to JSON file
    """
    try:
        with open(filename, 'w') as f:
            json.dump(dns_record, f, indent=2)
        print(f"✅ DNS records exported to {filename}")
    except Exception as e:
        print(f"❌ Error exporting to JSON: {e}")

def export_to_csv(dns_record, filename):
    """
    Export DNS records to CSV file
    """
    try:
        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Record Type', 'Value', 'Additional Info'])

            for record_type, records in dns_record.items():
                if records:
                    for record in records:
                        if isinstance(record, dict):
                            if 'exchange' in record:  # MX record
                                writer.writerow([record_type, record['exchange'], f"Priority: {record['priority']}"])
                            elif 'mname' in record:  # SOA record
                                writer.writerow([record_type, record['mname'], f"Serial: {record['serial']}"])
                        else:
                            writer.writerow([record_type, record, ''])
        print(f"✅ DNS records exported to {filename}")
    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")

def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Enhanced DNS Record Lookup Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dns_record.py google.com
  python dns_record.py google.com --records A MX
  python dns_record.py google.com --export-json results.json
  python dns_record.py google.com --export-csv results.csv
  python dns_record.py --interactive
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

    return parser.parse_args()

def clean_domain(domain):
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

def main():
    """
    Main function to run the DNS lookup tool with enhanced features
    """
    args = parse_arguments()

    # Disable colors if output is redirected or quiet mode
    if args.quiet or not sys.stdout.isatty():
        Colors.disable()

    # Determine if running in interactive mode
    if args.interactive or not args.domain:
        print(f"{Colors.BOLD}{Colors.BLUE}🔧 Enhanced DNS Record Lookup Tool{Colors.END}")
        print(f"{Colors.BLUE}{'=' * 50}{Colors.END}")

        try:
            # Get website from user
            website = input(f"{Colors.CYAN}Enter the domain name (e.g., google.com): {Colors.END}").strip()

            if not website:
                print(f"{Colors.RED}❌ Please enter a valid domain name{Colors.END}")
                return

            website = clean_domain(website)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 Program interrupted by user{Colors.END}")
            return
    else:
        website = clean_domain(args.domain)
        if not args.quiet:
            print(f"{Colors.BOLD}{Colors.BLUE}🔧 Enhanced DNS Record Lookup Tool{Colors.END}")
            print(f"{Colors.BLUE}{'=' * 50}{Colors.END}")

    try:
        # Get DNS records
        dns_record = get_dns_records(website, args.quiet)

        if not dns_record:
            return

        # Filter records if specific types requested
        if args.records:
            filtered_records = {}
            for record_type in args.records:
                key = f'{record_type}_Records'
                if key in dns_record:
                    filtered_records[key] = dns_record[key]
            dns_record = filtered_records

        # Display results
        if not args.quiet:
            display_records(dns_record)

        # Export if requested
        if args.export_json:
            export_to_json(dns_record, args.export_json)

        if args.export_csv:
            export_to_csv(dns_record, args.export_csv)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Program interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")

if __name__ == "__main__":
    main()

#Enhanced by Quang-Ng-Duong