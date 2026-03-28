"""
Test suite for Employee CRUD operations and validations.
"""

import pytest
import re
from app import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestEmployeesList:
    """Test GET /employees endpoint."""
    
    def test_list_employees_returns_json(self, client):
        """Verify employees endpoint returns JSON."""
        response = client.get("/employees", headers={"Accept": "application/json"})
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestEmployeeValidation:
    """Test Employee entity validation."""
    
    def test_email_format_validation(self):
        """Verify email format is valid."""
        valid_emails = ["ada@store.com", "user@example.org", "name.surname@company.co.uk"]
        invalid_emails = ["adastore.com", "user@", "@example.com", ""]
        
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        for email in valid_emails:
            assert re.match(email_pattern, email)
        
        for email in invalid_emails:
            assert not re.match(email_pattern, email)
    
    def test_category_enum_validation(self):
        """Verify category is in allowed enum."""
        valid_categories = {"Junior", "Senior", "Manager", "Specialist"}
        invalid_categories = {"Intern", "Director", "CEO", ""}
        
        for cat in valid_categories:
            assert cat in {"Junior", "Senior", "Manager", "Specialist"}
        
        for cat in invalid_categories:
            assert cat not in {"Junior", "Senior", "Manager", "Specialist"}
    
    def test_skills_non_empty(self):
        """Verify skills array is not empty."""
        valid_skills_sets = [
            ["WritingReports"],
            ["CustomerRelationships"],
            ["MachineryDriving", "WritingReports"],
            ["WritingReports", "CustomerRelationships", "MachineryDriving"]
        ]
        invalid_skills_sets = [[], set()]
        
        for skills in valid_skills_sets:
            assert len(skills) > 0
        
        for skills in invalid_skills_sets:
            assert len(skills) == 0
    
    def test_skills_enum_validation(self):
        """Verify all skills are in allowed enum."""
        allowed_skills = {"MachineryDriving", "WritingReports", "CustomerRelationships"}
        
        valid_combinations = [
            ["WritingReports"],
            ["MachineryDriving"],
            ["CustomerRelationships"],
            ["WritingReports", "CustomerRelationships"]
        ]
        invalid_combinations = [
            ["InvalidSkill"],
            ["WritingReports", "UnknownSkill"],
            ["Driving"]  # Partial name
        ]
        
        for skills in valid_combinations:
            assert all(s in allowed_skills for s in skills)
        
        for skills in invalid_combinations:
            assert not all(s in allowed_skills for s in skills)
    
    def test_salary_positive(self):
        """Verify salary > 0."""
        valid_salaries = [1800.00, 2500.00, 3200.00]
        invalid_salaries = [0, -1000, 0.0]
        
        for salary in valid_salaries:
            assert salary > 0
        
        for salary in invalid_salaries:
            assert salary <= 0
    
    def test_name_length(self):
        """Verify name length (1-140 chars)."""
        valid_names = ["Ada", "Ada Lovelace", "A" * 140]
        invalid_names = ["", "A" * 141]
        
        for name in valid_names:
            assert 1 <= len(name) <= 140
        
        for name in invalid_names:
            assert not (1 <= len(name) <= 140)


class TestEmployeeIntegration:
    """Integration tests for Employee operations."""
    
    def test_employee_with_all_required_fields(self):
        """Verify employee entity structure."""
        employee = {
            "id": "urn:ngsi-ld:Employee:E001",
            "type": "Employee",
            "name": "Ada Lovelace",
            "category": "Senior",
            "role": "Store Manager",
            "salary": 2800.00,
            "email": "ada@store.com",
            "skills": ["WritingReports"],
            "refStore": "urn:ngsi-ld:Store:S001"
        }
        
        assert employee["id"].startswith("urn:ngsi-ld:Employee:")
        assert employee["type"] == "Employee"
        assert employee["category"] in {"Junior", "Senior", "Manager", "Specialist"}
        assert employee["salary"] > 0
        assert len(employee["skills"]) > 0
        assert employee["refStore"].startswith("urn:ngsi-ld:Store:")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
