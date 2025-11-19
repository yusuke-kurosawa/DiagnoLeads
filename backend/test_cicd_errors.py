"""
Test file to verify CI/CD error detection system

This file intentionally contains linter errors that should be:
1. Detected by the CI/CD pipeline
2. Captured in error logs
3. Auto-fixed by the auto-fix-linter workflow
4. Commented on the PR by comment-on-failure workflow
"""

# Linter error: unused import (will be auto-fixed)
import os
import sys
import json

# Linter error: unused variable (will be auto-fixed)
unused_variable = "This should be removed"

# Linter error: line too long (will be auto-fixed)
very_long_line_that_exceeds_the_maximum_line_length_and_should_be_wrapped_by_the_formatter_to_comply_with_pep8_standards = "test"


def test_cicd_error_detection():
    """Test function to verify error detection"""
    # Linter error: missing docstring formatting
    x=1+2  # Linter error: no spaces around operators

    # This will pass
    result = x * 2
    assert result == 6

    return result


# Linter error: multiple blank lines at end of file


