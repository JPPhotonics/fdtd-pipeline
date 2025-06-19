#!/usr/bin/env python3
"""
Codebase Validation Script

This script validates the codebase for common issues and ensures it's ready for publication.
It checks for:
- Missing files
- Import errors
- Configuration issues
- Code style issues

Author: Zuyang Liu
Date: 2024
"""

import os
import sys
import json
import importlib
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CodebaseValidator:
    """Validates the codebase for publication readiness."""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.errors = []
        self.warnings = []
        
    def validate_file_structure(self) -> bool:
        """Validate that all required files and directories exist."""
        logger.info("Validating file structure...")
        
        required_files = [
            "config.json",
            "environment.yml", 
            "readme.md",
            "stack.json",
            "stack_universal.json"
        ]
        
        required_dirs = [
            "gds_library",
            "helper_functions",
            "materials_library", 
            "projects"
        ]
        
        # Check required files
        for file in required_files:
            if not (self.root_dir / file).exists():
                self.errors.append(f"Missing required file: {file}")
                
        # Check required directories
        for dir_name in required_dirs:
            if not (self.root_dir / dir_name).is_dir():
                self.errors.append(f"Missing required directory: {dir_name}")
                
        return len(self.errors) == 0
    
    def validate_config_files(self) -> bool:
        """Validate configuration files."""
        logger.info("Validating configuration files...")
        
        # Check config.json
        config_file = self.root_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                
                required_keys = ["wavelength", "wav_step", "temperature", "material_type", 
                               "guiding_material", "lumapi_path", "solver_z_min", "solver_z_max"]
                
                for key in required_keys:
                    if key not in config:
                        self.warnings.append(f"Missing key in config.json: {key}")
                        
            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in config.json: {e}")
        else:
            self.errors.append("config.json not found")
            
        return len(self.errors) == 0
    
    def validate_device_scripts(self) -> bool:
        """Validate device simulation scripts."""
        logger.info("Validating device simulation scripts...")
        
        device_scripts = {
            "coupler": "directional_coupler.py",
            "crossing": "crossing.py", 
            "mmi2x2": "mmi2x2.py",
            "mode_converter": "mode_converter.py",
            "polarization_splitter_rotator": "polarization_splitter_rotator.py"
        }
        
        for device, script_name in device_scripts.items():
            script_path = self.root_dir / "projects" / "FDTD_solvers" / device / script_name
            if not script_path.exists():
                self.warnings.append(f"Missing device script: {script_path}")
                
        return len(self.errors) == 0
    
    def validate_imports(self) -> bool:
        """Validate that all Python modules can be imported."""
        logger.info("Validating Python imports...")
        
        # Add root directory to path
        sys.path.insert(0, str(self.root_dir))
        
        # Test imports
        try:
            import helper_functions.generic.misc
            import helper_functions.lumerical.simulate_device
            import helper_functions.tidy3d.simulate_device
            logger.info("Core modules imported successfully")
        except ImportError as e:
            self.errors.append(f"Import error: {e}")
            
        return len(self.errors) == 0
    
    def check_for_debug_code(self) -> bool:
        """Check for debug code that should be removed."""
        logger.info("Checking for debug code...")
        
        debug_patterns = [
            "print(",
            "pdb.set_trace()",
            "import pdb",
            "breakpoint()",
            "TODO:",
            "FIXME:",
            "XXX:",
            "HACK:"
        ]
        
        python_files = list(self.root_dir.rglob("*.py"))
        
        for file_path in python_files:
            # Skip the validation script itself
            if file_path.name == "validate_codebase.py":
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in debug_patterns:
                    if pattern in content:
                        self.warnings.append(f"Debug code found in {file_path}: {pattern}")
                        
            except Exception as e:
                self.warnings.append(f"Could not read {file_path}: {e}")
                
        return len(self.errors) == 0
    
    def validate_gds_files(self) -> bool:
        """Validate that GDS files exist."""
        logger.info("Validating GDS files...")
        
        gds_dir = self.root_dir / "gds_library" / "cells_from_gds"
        if gds_dir.exists():
            gds_files = list(gds_dir.rglob("*.gds"))
            if not gds_files:
                self.warnings.append("No GDS files found in gds_library/cells_from_gds/")
        else:
            self.warnings.append("GDS directory not found")
            
        return len(self.errors) == 0
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all validation checks."""
        logger.info("Starting codebase validation...")
        
        checks = [
            self.validate_file_structure,
            self.validate_config_files,
            self.validate_device_scripts,
            self.validate_imports,
            self.check_for_debug_code,
            self.validate_gds_files
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.errors.append(f"Check failed: {e}")
        
        # Summary
        result = {
            "passed": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings)
        }
        
        return result
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """Print validation results."""
        print("\n" + "="*60)
        print("CODEBASE VALIDATION RESULTS")
        print("="*60)
        
        if results["passed"]:
            print("✅ Codebase validation PASSED")
        else:
            print("❌ Codebase validation FAILED")
            
        print(f"\nErrors: {results['total_errors']}")
        print(f"Warnings: {results['total_warnings']}")
        
        if results["errors"]:
            print("\n❌ ERRORS:")
            for error in results["errors"]:
                print(f"  • {error}")
                
        if results["warnings"]:
            print("\n⚠️  WARNINGS:")
            for warning in results["warnings"]:
                print(f"  • {warning}")
                
        print("\n" + "="*60)

def main():
    """Main validation function."""
    validator = CodebaseValidator()
    results = validator.run_all_checks()
    validator.print_results(results)
    
    # Exit with error code if validation failed
    if not results["passed"]:
        sys.exit(1)

if __name__ == "__main__":
    main() 