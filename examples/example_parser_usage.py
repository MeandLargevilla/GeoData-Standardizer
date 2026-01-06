"""Example usage of GeoData-Standardizer parsers.

This script demonstrates how to use the parser classes to parse,
validate, and standardize geophysical data.
"""

from pathlib import Path
from src.core.dispatcher import Dispatcher
from src.parsers.elec_parser import ElecParser
from src.parsers.seismic_parser import SeismicParser
from src.parsers.radar_parser import RadarParser
from src.processors.standardizer import Standardizer
from src.processors.qc_checker import QCChecker
from src.utils.logger import setup_logger
import logging


def example_basic_parsing():
    """Example: Basic parsing with a specific parser."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Parsing")
    print("=" * 60)
    
    # Setup logging
    logger = setup_logger('example', level=logging.INFO)
    
    # Create a sample CSV file
    sample_data = """station_id,depth_m,resistivity_ohm_m
S001,0.5,150.2
S001,1.0,145.8
S001,1.5,138.4
S002,0.5,220.1
S002,1.0,215.3
S002,1.5,210.7
"""
    
    # Write sample file
    data_file = Path('sample_electrical.csv')
    data_file.write_text(sample_data)
    
    try:
        # Parse the file
        parser = ElecParser(data_file)
        result = parser.process()
        
        print(f"\nParsed {result['metadata']['record_count']} records")
        print(f"Columns: {list(result['data'].columns)}")
        print("\nFirst few rows:")
        print(result['data'].head())
        
    finally:
        # Clean up
        if data_file.exists():
            data_file.unlink()


def example_using_dispatcher():
    """Example: Using the Dispatcher to auto-select parser."""
    print("\n" + "=" * 60)
    print("Example 2: Using Dispatcher")
    print("=" * 60)
    
    # Create sample data
    sample_data = """trace_number,time_ms,amplitude
1,0.0,0.5
1,0.1,0.8
1,0.2,1.2
2,0.0,0.3
2,0.1,0.6
2,0.2,0.9
"""
    
    data_file = Path('sample_seismic.csv')
    data_file.write_text(sample_data)
    
    try:
        # Use dispatcher to get the right parser
        dispatcher = Dispatcher()
        
        # Get parser by data type
        parser = dispatcher.get_parser('seismic', data_file)
        result = parser.process()
        
        print(f"\nParsed {result['metadata']['record_count']} records")
        print(f"Data type: {result['metadata']['data_type']}")
        print(f"Traces: {result['metadata']['traces']}")
        
    finally:
        if data_file.exists():
            data_file.unlink()


def example_full_pipeline():
    """Example: Complete processing pipeline with QC and standardization."""
    print("\n" + "=" * 60)
    print("Example 3: Full Processing Pipeline")
    print("=" * 60)
    
    # Create sample data
    sample_data = """trace_number,sample_number,amplitude
1,0,100
1,1,150
1,2,200
2,0,110
2,1,160
2,2,210
"""
    
    data_file = Path('sample_radar.csv')
    data_file.write_text(sample_data)
    
    try:
        # Step 1: Parse
        print("\nStep 1: Parsing...")
        parser = RadarParser(data_file)
        parsed_data = parser.process()
        print(f"✓ Parsed {parsed_data['metadata']['record_count']} records")
        
        # Step 2: Quality Control
        print("\nStep 2: Quality Control...")
        qc_checker = QCChecker()
        qc_result = qc_checker.check(parsed_data)
        print(f"✓ QC Status: {'PASSED' if qc_result['passed'] else 'FAILED'}")
        print(f"  Checks run: {', '.join(qc_result['checks_run'])}")
        
        if qc_result['warnings']:
            print("  Warnings:")
            for warning in qc_result['warnings']:
                print(f"    - {warning}")
        
        # Step 3: Standardize
        print("\nStep 3: Standardization...")
        standardizer = Standardizer(output_format='csv')
        standardized = standardizer.standardize(parsed_data, 'radar')
        print(f"✓ Standardized data ready")
        
        # Step 4: Output
        print("\nStep 4: Writing output...")
        output_file = Path('output_radar.csv')
        standardizer.write_output(standardized, output_file)
        print(f"✓ Output written to {output_file}")
        
        # Show result
        print("\nStandardized data:")
        print(standardized['data'])
        
        # Clean up output file
        if output_file.exists():
            output_file.unlink()
        
        # Clean up metadata file
        metadata_file = Path('output_radar_metadata.json')
        if metadata_file.exists():
            metadata_file.unlink()
        
    finally:
        if data_file.exists():
            data_file.unlink()


def example_error_handling():
    """Example: Error handling and validation."""
    print("\n" + "=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)
    
    # Create invalid data (missing required columns)
    invalid_data = """col1,col2
val1,val2
val3,val4
"""
    
    data_file = Path('invalid_electrical.csv')
    data_file.write_text(invalid_data)
    
    try:
        print("\nAttempting to parse invalid data...")
        parser = ElecParser(data_file)
        result = parser.parse()
        
        # Try to validate - this should fail
        try:
            parser.validate()
            print("Validation passed (unexpected)")
        except Exception as e:
            print(f"✓ Validation failed as expected: {e}")
            
    except Exception as e:
        print(f"✓ Error caught: {e}")
        
    finally:
        if data_file.exists():
            data_file.unlink()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("GeoData-Standardizer - Usage Examples")
    print("=" * 60)
    
    example_basic_parsing()
    example_using_dispatcher()
    example_full_pipeline()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
