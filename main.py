#!/usr/bin/env python3
"""Main CLI application for GeoData-Standardizer.

This script provides a command-line interface for parsing, validating,
and standardizing geophysical data from various formats.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from src.core.dispatcher import Dispatcher
from src.processors.standardizer import Standardizer
from src.processors.qc_checker import QCChecker
from src.utils.logger import setup_logger
from src.config import setup_logging, get_output_path, APP_CONFIG


def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        Namespace object with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='GeoData-Standardizer: Standardize geophysical data formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --type electrical --output result.csv
  %(prog)s --input survey.sgy --type seismic --format json
  %(prog)s --input gpr.dzt --type radar --skip-qc --verbose
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Path to input data file'
    )
    
    parser.add_argument(
        '--type', '-t',
        type=str,
        choices=['electrical', 'seismic', 'radar'],
        required=True,
        help='Type of geophysical data'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to output file (optional, auto-generated if not provided)'
    )
    
    parser.add_argument(
        '--skip-qc',
        action='store_true',
        help='Skip quality control checks'
    )
    
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['csv', 'json', 'excel', 'parquet'],
        default='csv',
        help='Output file format (default: csv)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f"%(prog)s {APP_CONFIG['version']}"
    )
    
    return parser.parse_args()


def validate_input_file(file_path: Path) -> None:
    """Validate that input file exists and is readable.
    
    Args:
        file_path: Path to input file.
    
    Raises:
        SystemExit: If validation fails.
    """
    if not file_path.exists():
        print(f"Error: Input file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    if not file_path.is_file():
        print(f"Error: Input path is not a file: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    if file_path.stat().st_size == 0:
        print(f"Error: Input file is empty: {file_path}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main application entry point.
    
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)
    
    # Log startup
    logger.info(f"GeoData-Standardizer v{APP_CONFIG['version']}")
    logger.info(f"Processing {args.type} data from {args.input}")
    
    try:
        # Validate input
        input_path = Path(args.input)
        validate_input_file(input_path)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = get_output_path(input_path, format=args.format)
        
        logger.info(f"Output will be written to: {output_path}")
        
        # Step 1: Parse data
        logger.info("Step 1/4: Parsing data...")
        dispatcher = Dispatcher()
        parser = dispatcher.get_parser(args.type, input_path)
        parsed_data = parser.process(skip_validation=True)
        logger.info(f"✓ Parsed {parsed_data['metadata']['record_count']} records")
        
        # Step 2: Quality control (optional)
        qc_result = None
        if not args.skip_qc:
            logger.info("Step 2/4: Running quality control checks...")
            qc_checker = QCChecker()
            qc_result = qc_checker.check(parsed_data)
            
            if qc_result['passed']:
                logger.info("✓ QC checks passed")
            else:
                logger.warning("⚠ QC checks found issues:")
                for issue in qc_result['issues']:
                    logger.warning(f"  - {issue}")
            
            if qc_result.get('warnings'):
                logger.info("QC warnings:")
                for warning in qc_result['warnings']:
                    logger.info(f"  - {warning}")
        else:
            logger.info("Step 2/4: Skipping quality control checks")
        
        # Step 3: Validate data
        logger.info("Step 3/4: Validating data...")
        parser.validate()
        logger.info("✓ Validation passed")
        
        # Step 4: Standardize and output
        logger.info("Step 4/4: Standardizing and writing output...")
        standardizer = Standardizer(output_format=args.format)
        standardized_data = standardizer.standardize(parsed_data, args.type)
        standardizer.write_output(standardized_data, output_path)
        logger.info(f"✓ Output written to {output_path}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUCCESS: Data processing complete")
        print("=" * 60)
        print(f"Input file:      {input_path}")
        print(f"Data type:       {args.type}")
        print(f"Records parsed:  {parsed_data['metadata']['record_count']}")
        print(f"Output file:     {output_path}")
        print(f"Output format:   {args.format}")
        
        if qc_result:
            print(f"QC status:       {'PASSED' if qc_result['passed'] else 'ISSUES FOUND'}")
            if qc_result['issues']:
                print(f"QC issues:       {len(qc_result['issues'])}")
            if qc_result['warnings']:
                print(f"QC warnings:     {len(qc_result['warnings'])}")
        
        print("=" * 60 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user", file=sys.stderr)
        logger.info("Operation cancelled by user")
        return 130
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        print(f"\nError: {e}", file=sys.stderr)
        
        if args.verbose:
            import traceback
            traceback.print_exc()
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
