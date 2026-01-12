
"""
Templates for generating security scan reports.
"""

SECURITY_SCAN_REPORT_TEMPLATE = """# Code Scanner Agent - Scan Report

## Repository Information
**Repository:** {repo_url}
**Scan ID:** {scan_id}
**Date:** {scan_date}

## Scan Summary
**Total Issues:** {total_issues}
**Security Issues:** {security_issues_count}
**Quality Issues:** {quality_issues_count}
**Best Practice Issues:** {best_practice_issues_count}
**Maintainability Issues:** {maintainability_issues_count}
**Documentation Issues:** {documentation_issues_count}
**Unit Tests:** {unit_tests_passed} Passed
**Coverage:** {coverage_percentage}%

## Detailed Issues

{detailed_issues}
"""

ISSUE_TEMPLATE = """{index}. [{severity}] {category}
**File:** {file_path} (Line {line_number})
**Issue:** {issue_description}
**Code:** `{code_snippet}`
**Fix:** {fix_recommendation}
"""
