# 🌐 DNS Record Lookup Tool

A comprehensive, professional-grade DNS lookup tool with modern features, beautiful output formatting, and robust error handling.

## ✨ Features

### 🔍 Comprehensive DNS Record Support
- **A Records** - IPv4 addresses
- **AAAA Records** - IPv6 addresses
- **CNAME Records** - Canonical names
- **MX Records** - Mail exchange servers
- **NS Records** - Name servers
- **TXT Records** - Text records
- **SOA Records** - Start of Authority

### 🎨 Beautiful Output
- **Colorized terminal output** with emoji indicators
- **Table formatting** for MX records
- **Progress indicators** during DNS queries
- **Comprehensive error messages** with helpful suggestions

### 🛠️ Advanced Features
- **Command-line interface** with extensive options
- **Interactive mode** for user-friendly operation
- **JSON/CSV export** capabilities with timestamps
- **Configurable settings** via JSON config file
- **Comprehensive logging** with rotation
- **Input validation** and domain cleaning
- **Robust error handling** for network issues

### 🏗️ Professional Architecture
- **Class-based design** for maintainability
- **Comprehensive unit tests** for reliability
- **Modular code structure** for extensibility
- **Configuration management** for customization

## 📦 Installation

### Prerequisites
- Python 3.6 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages
- `dnspython>=2.7.0` - DNS resolution library

## 🚀 Usage

### Command Line Interface

#### Basic Usage
```bash
# Lookup all DNS records for a domain
python dns_lookup_class.py google.com

# Lookup specific record types
python dns_lookup_class.py google.com --records A MX

# Export results to JSON
python dns_lookup_class.py google.com --export-json results.json

# Export results to CSV
python dns_lookup_class.py google.com --export-csv results.csv

# Quiet mode (minimal output)
python dns_lookup_class.py google.com --quiet
```

#### Interactive Mode
```bash
# Run in interactive mode
python dns_lookup_class.py --interactive
# or
python dns_lookup_class.py
```

#### Advanced Options
```bash
# Use custom config file
python dns_lookup_class.py google.com --config my_config.json

# Combine multiple options
python dns_lookup_class.py example.com --records A AAAA MX --export-json results.json --quiet
```

### Legacy Script
The original simple script is still available:
```bash
python dns_record.py
```

## ⚙️ Configuration

The tool uses a `config.json` file for customization:

```json
{
  "dns_settings": {
    "timeout": 10,
    "retries": 3,
    "default_nameserver": null,
    "record_types": ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"]
  },
  "display_settings": {
    "use_colors": true,
    "max_txt_length": 70,
    "table_format": true,
    "show_progress": true
  },
  "export_settings": {
    "json_indent": 2,
    "csv_delimiter": ",",
    "include_timestamp": true
  },
  "logging": {
    "level": "INFO",
    "file": "dns_lookup.log",
    "max_size_mb": 10,
    "backup_count": 3,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

### Configuration Options

#### DNS Settings
- `timeout`: DNS query timeout in seconds
- `retries`: Number of retry attempts
- `default_nameserver`: Custom DNS server (optional)
- `record_types`: Default record types to query

#### Display Settings
- `use_colors`: Enable/disable colored output
- `max_txt_length`: Maximum length for TXT record display
- `table_format`: Use table formatting for MX records
- `show_progress`: Show progress indicators

#### Export Settings
- `json_indent`: JSON file indentation
- `csv_delimiter`: CSV field delimiter
- `include_timestamp`: Add timestamp to exports

#### Logging Settings
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `file`: Log file path (null to disable file logging)
- `max_size_mb`: Maximum log file size before rotation
- `backup_count`: Number of backup log files to keep

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest test_dns_lookup.py -v

# Run with coverage
python -m pytest test_dns_lookup.py --cov=dns_lookup_class --cov-report=html

# Run specific test
python -m pytest test_dns_lookup.py::TestDNSLookupTool::test_validate_domain_valid -v
```

### Test Coverage
The test suite covers:
- Domain validation and cleaning
- DNS record fetching for all types
- Error handling (NXDOMAIN, NoAnswer, timeouts)
- Export functionality (JSON/CSV)
- Configuration loading
- Color output management

## 📊 Output Examples

### Successful Lookup
```
🔧 Enhanced DNS Record Lookup Tool
==================================================
🔍 Querying DNS records for: google.com
------------------------------------------------------------
📍 Fetching A records...
✅ Found 1 A record(s)
📧 Fetching MX records...
✅ Found 1 MX record(s)

================================================================================
🌐 COMPREHENSIVE DNS RECORDS SUMMARY
================================================================================

📍 A Records (IPv4 Addresses):
   1. 142.250.191.14

📧 MX Records (Mail Servers):
   ┌─────────────┬─────────────────────────────────────────────────┐
   │ Priority     │ Mail Server                                  │
   ├─────────────┼─────────────────────────────────────────────────┤
   │ 10          │ smtp.google.com                              │
   └─────────────┴─────────────────────────────────────────────────┘
```

### Error Handling
```
❌ Domain nonexistent.domain does not exist
⚠️  No AAAA records found
❌ Error fetching TXT records: Timeout
```

## 🔧 API Reference

### DNSLookupTool Class

#### Constructor
```python
dns_tool = DNSLookupTool(config_file='config.json')
```

#### Methods

##### `get_dns_records(website, record_types=None, quiet=False)`
Fetch DNS records for a domain.

**Parameters:**
- `website` (str): Domain name to lookup
- `record_types` (list, optional): Specific record types to fetch
- `quiet` (bool): Suppress output messages

**Returns:**
- `dict`: DNS records organized by type, or `None` if domain doesn't exist

##### `validate_domain(domain)`
Validate domain name format.

**Parameters:**
- `domain` (str): Domain name to validate

**Returns:**
- `bool`: True if valid, False otherwise

##### `export_to_json(dns_record, filename)`
Export DNS records to JSON file.

##### `export_to_csv(dns_record, filename)`
Export DNS records to CSV file.

##### `run_interactive()`
Run tool in interactive mode.

##### `run_cli(domain, record_types=None, export_json=None, export_csv=None, quiet=False)`
Run tool with command-line arguments.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include unit tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Quang-Ng-Duong** - Enhanced Version with Professional Features

Original simple version enhanced with:
- Modern Python practices
- Comprehensive error handling
- Beautiful output formatting
- Export capabilities
- Configuration management
- Extensive testing
- Professional documentation

## 🙏 Acknowledgments

- Built with [dnspython](https://github.com/rthalley/dnspython) library
- Inspired by the need for a comprehensive DNS lookup tool
- Thanks to the Python community for excellent libraries and tools

## 📈 Version History

- **v2.0.0** - Complete rewrite with class-based architecture
- **v1.5.0** - Added export capabilities and configuration
- **v1.0.0** - Enhanced version with error handling and colors
- **v0.1.0** - Original simple DNS lookup script
