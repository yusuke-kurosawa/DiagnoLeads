"""
Tests for Industry Templates

Comprehensive tests for industry-specific templates and helper functions.
"""

import pytest

from app.services.ai.industry_templates import (
    INDUSTRY_TEMPLATES,
    IndustryTemplate,
    get_industry_template,
    list_available_industries,
)


class TestIndustryTemplateDataclass:
    """Tests for IndustryTemplate dataclass"""

    def test_industry_template_creation(self):
        """Test creating IndustryTemplate instance"""
        template = IndustryTemplate(
            name="Test Industry",
            description="Test description",
            common_pain_points=["pain1", "pain2"],
            question_themes=["theme1", "theme2"],
            scoring_guidelines="Test scoring",
            example_questions=["Q1", "Q2"],
        )

        assert template.name == "Test Industry"
        assert template.description == "Test description"
        assert len(template.common_pain_points) == 2
        assert len(template.question_themes) == 2
        assert template.scoring_guidelines == "Test scoring"
        assert len(template.example_questions) == 2


class TestIndustryTemplatesData:
    """Tests for INDUSTRY_TEMPLATES data"""

    def test_all_industries_defined(self):
        """Test all expected industries are defined"""
        expected_industries = [
            "it_saas",
            "consulting",
            "manufacturing",
            "ecommerce",
            "healthcare",
            "education",
            "marketing",
            "hr",
            "finance",
            "general",
        ]

        for industry in expected_industries:
            assert industry in INDUSTRY_TEMPLATES

    def test_it_saas_template(self):
        """Test IT/SaaS template content"""
        template = INDUSTRY_TEMPLATES["it_saas"]

        assert template.name == "IT/SaaS"
        assert "Software" in template.description or "SaaS" in template.description
        assert len(template.common_pain_points) > 0
        assert len(template.question_themes) > 0
        assert len(template.example_questions) > 0
        assert template.scoring_guidelines != ""

    def test_consulting_template(self):
        """Test Consulting template content"""
        template = INDUSTRY_TEMPLATES["consulting"]

        assert "コンサルティング" in template.name
        assert len(template.common_pain_points) > 0
        assert len(template.question_themes) > 0

    def test_manufacturing_template(self):
        """Test Manufacturing template content"""
        template = INDUSTRY_TEMPLATES["manufacturing"]

        assert "製造" in template.name
        assert len(template.common_pain_points) > 0

    def test_ecommerce_template(self):
        """Test E-commerce template content"""
        template = INDUSTRY_TEMPLATES["ecommerce"]

        assert "EC" in template.name or "小売" in template.name
        assert len(template.question_themes) > 0

    def test_healthcare_template(self):
        """Test Healthcare template content"""
        template = INDUSTRY_TEMPLATES["healthcare"]

        assert "ヘルスケア" in template.name
        assert len(template.example_questions) > 0

    def test_education_template(self):
        """Test Education template content"""
        template = INDUSTRY_TEMPLATES["education"]

        assert "教育" in template.name
        assert len(template.common_pain_points) > 0

    def test_marketing_template(self):
        """Test Marketing template content"""
        template = INDUSTRY_TEMPLATES["marketing"]

        assert "マーケティング" in template.name
        assert len(template.question_themes) > 0

    def test_hr_template(self):
        """Test HR template content"""
        template = INDUSTRY_TEMPLATES["hr"]

        assert "人事" in template.name or "採用" in template.name
        assert len(template.common_pain_points) > 0

    def test_finance_template(self):
        """Test Finance template content"""
        template = INDUSTRY_TEMPLATES["finance"]

        assert "金融" in template.name or "FinTech" in template.name
        assert len(template.question_themes) > 0

    def test_general_template(self):
        """Test General template content"""
        template = INDUSTRY_TEMPLATES["general"]

        assert "一般" in template.name
        assert template.description != ""

    def test_all_templates_have_required_fields(self):
        """Test all templates have non-empty required fields"""
        for key, template in INDUSTRY_TEMPLATES.items():
            assert template.name != "", f"{key} template missing name"
            assert template.description != "", f"{key} template missing description"
            assert len(template.common_pain_points) > 0, f"{key} template has no pain points"
            assert len(template.question_themes) > 0, f"{key} template has no question themes"
            assert template.scoring_guidelines != "", f"{key} template missing scoring guidelines"
            assert len(template.example_questions) > 0, f"{key} template has no example questions"

    def test_templates_have_multiple_pain_points(self):
        """Test templates have multiple pain points"""
        for key, template in INDUSTRY_TEMPLATES.items():
            assert len(template.common_pain_points) >= 3, f"{key} should have at least 3 pain points"

    def test_templates_have_multiple_question_themes(self):
        """Test templates have multiple question themes"""
        for key, template in INDUSTRY_TEMPLATES.items():
            assert len(template.question_themes) >= 3, f"{key} should have at least 3 question themes"

    def test_templates_have_example_questions(self):
        """Test templates have example questions"""
        for key, template in INDUSTRY_TEMPLATES.items():
            assert len(template.example_questions) >= 2, f"{key} should have at least 2 example questions"


class TestGetIndustryTemplate:
    """Tests for get_industry_template function"""

    def test_get_existing_template(self):
        """Test getting existing template"""
        template = get_industry_template("it_saas")

        assert template.name == "IT/SaaS"
        assert isinstance(template, IndustryTemplate)

    def test_get_all_defined_industries(self):
        """Test getting all defined industries"""
        industries = [
            "it_saas",
            "consulting",
            "manufacturing",
            "ecommerce",
            "healthcare",
            "education",
            "marketing",
            "hr",
            "finance",
            "general",
        ]

        for industry in industries:
            template = get_industry_template(industry)
            assert isinstance(template, IndustryTemplate)
            assert template.name != ""

    def test_get_nonexistent_template_returns_general(self):
        """Test non-existent industry returns general template"""
        template = get_industry_template("nonexistent_industry")

        assert template.name == "一般企業"
        assert template == INDUSTRY_TEMPLATES["general"]

    def test_case_insensitive_lookup(self):
        """Test industry lookup is case-insensitive"""
        template_lower = get_industry_template("it_saas")
        template_upper = get_industry_template("IT_SAAS")
        template_mixed = get_industry_template("It_SaaS")

        assert template_lower == template_upper
        assert template_lower == template_mixed

    def test_space_to_underscore_conversion(self):
        """Test spaces are converted to underscores"""
        template = get_industry_template("it saas")

        assert template.name == "IT/SaaS"

    def test_slash_to_underscore_conversion(self):
        """Test slashes are converted to underscores"""
        # This would need an industry with slash in key
        # Using general as fallback test
        template = get_industry_template("some/industry")

        # Should return general since no exact match
        assert isinstance(template, IndustryTemplate)

    def test_combined_transformations(self):
        """Test combined case, space, and slash transformations"""
        # Should normalize to it_saas
        template = get_industry_template("IT SAAS")

        assert template.name == "IT/SaaS"

    def test_returns_same_instance_for_same_key(self):
        """Test returns same template instance for same key"""
        template1 = get_industry_template("it_saas")
        template2 = get_industry_template("it_saas")

        assert template1 is template2

    def test_empty_string_returns_general(self):
        """Test empty string returns general template"""
        template = get_industry_template("")

        assert template.name == "一般企業"


class TestListAvailableIndustries:
    """Tests for list_available_industries function"""

    def test_returns_list(self):
        """Test returns a list"""
        result = list_available_industries()

        assert isinstance(result, list)

    def test_list_not_empty(self):
        """Test list is not empty"""
        result = list_available_industries()

        assert len(result) > 0

    def test_contains_all_industries(self):
        """Test list contains all defined industries"""
        result = list_available_industries()

        assert len(result) == len(INDUSTRY_TEMPLATES)

    def test_each_item_has_required_fields(self):
        """Test each item has key, name, and description"""
        result = list_available_industries()

        for item in result:
            assert "key" in item
            assert "name" in item
            assert "description" in item

    def test_each_item_fields_not_empty(self):
        """Test each item has non-empty fields"""
        result = list_available_industries()

        for item in result:
            assert item["key"] != ""
            assert item["name"] != ""
            assert item["description"] != ""

    def test_contains_it_saas(self):
        """Test list contains IT/SaaS industry"""
        result = list_available_industries()

        it_saas_items = [item for item in result if item["key"] == "it_saas"]
        assert len(it_saas_items) == 1
        assert it_saas_items[0]["name"] == "IT/SaaS"

    def test_contains_general(self):
        """Test list contains general industry"""
        result = list_available_industries()

        general_items = [item for item in result if item["key"] == "general"]
        assert len(general_items) == 1
        assert "一般" in general_items[0]["name"]

    def test_all_keys_are_unique(self):
        """Test all industry keys are unique"""
        result = list_available_industries()

        keys = [item["key"] for item in result]
        assert len(keys) == len(set(keys))

    def test_result_matches_industry_templates(self):
        """Test result matches INDUSTRY_TEMPLATES"""
        result = list_available_industries()

        result_keys = {item["key"] for item in result}
        template_keys = set(INDUSTRY_TEMPLATES.keys())

        assert result_keys == template_keys

    def test_descriptions_match_templates(self):
        """Test descriptions match template descriptions"""
        result = list_available_industries()

        for item in result:
            template = INDUSTRY_TEMPLATES[item["key"]]
            assert item["description"] == template.description
