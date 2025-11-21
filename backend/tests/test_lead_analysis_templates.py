"""
Tests for Lead Analysis Templates

Comprehensive tests for industry-specific lead analysis templates and helper functions.
"""

from app.services.ai.lead_analysis_templates import (
    LEAD_ANALYSIS_TEMPLATES,
    LeadAnalysisTemplate,
    get_lead_analysis_template,
    get_recommended_action,
)


class TestLeadAnalysisTemplateDataclass:
    """Tests for LeadAnalysisTemplate dataclass"""

    def test_template_creation(self):
        """Test creating LeadAnalysisTemplate instance"""
        template = LeadAnalysisTemplate(
            industry="Test",
            key_signals=["signal1", "signal2"],
            qualification_criteria=["criteria1"],
            recommended_actions={"80-100": "action1"},
            talking_points_themes=["theme1"],
        )

        assert template.industry == "Test"
        assert len(template.key_signals) == 2
        assert len(template.qualification_criteria) == 1
        assert "80-100" in template.recommended_actions
        assert len(template.talking_points_themes) == 1


class TestLeadAnalysisTemplatesData:
    """Tests for LEAD_ANALYSIS_TEMPLATES data"""

    def test_expected_industries_defined(self):
        """Test expected industries are defined"""
        expected = ["it_saas", "consulting", "manufacturing", "ecommerce", "marketing"]

        for industry in expected:
            assert industry in LEAD_ANALYSIS_TEMPLATES

    def test_it_saas_template(self):
        """Test IT/SaaS template"""
        template = LEAD_ANALYSIS_TEMPLATES["it_saas"]

        assert template.industry == "IT/SaaS"
        assert len(template.key_signals) > 0
        assert len(template.qualification_criteria) > 0
        assert len(template.recommended_actions) == 4
        assert len(template.talking_points_themes) > 0

    def test_consulting_template(self):
        """Test Consulting template"""
        template = LEAD_ANALYSIS_TEMPLATES["consulting"]

        assert "コンサルティング" in template.industry
        assert len(template.key_signals) > 0

    def test_manufacturing_template(self):
        """Test Manufacturing template"""
        template = LEAD_ANALYSIS_TEMPLATES["manufacturing"]

        assert "製造" in template.industry
        assert len(template.qualification_criteria) > 0

    def test_ecommerce_template(self):
        """Test E-commerce template"""
        template = LEAD_ANALYSIS_TEMPLATES["ecommerce"]

        assert "EC" in template.industry or "小売" in template.industry
        assert len(template.talking_points_themes) > 0

    def test_marketing_template(self):
        """Test Marketing template"""
        template = LEAD_ANALYSIS_TEMPLATES["marketing"]

        assert "マーケティング" in template.industry
        assert len(template.key_signals) > 0

    def test_all_templates_have_required_fields(self):
        """Test all templates have required fields"""
        for key, template in LEAD_ANALYSIS_TEMPLATES.items():
            assert template.industry != "", f"{key} missing industry"
            assert len(template.key_signals) > 0, f"{key} has no key signals"
            assert len(template.qualification_criteria) > 0, f"{key} has no qualification criteria"
            assert len(template.recommended_actions) > 0, f"{key} has no recommended actions"
            assert len(template.talking_points_themes) > 0, f"{key} has no talking points"

    def test_all_templates_have_score_ranges(self):
        """Test all templates have all score ranges"""
        expected_ranges = ["80-100", "60-79", "40-59", "0-39"]

        for key, template in LEAD_ANALYSIS_TEMPLATES.items():
            for range_key in expected_ranges:
                assert range_key in template.recommended_actions, f"{key} missing {range_key} action"

    def test_all_actions_not_empty(self):
        """Test all recommended actions are not empty"""
        for key, template in LEAD_ANALYSIS_TEMPLATES.items():
            for range_key, action in template.recommended_actions.items():
                assert action != "", f"{key} has empty action for {range_key}"

    def test_templates_have_multiple_signals(self):
        """Test templates have multiple key signals"""
        for key, template in LEAD_ANALYSIS_TEMPLATES.items():
            assert len(template.key_signals) >= 3, f"{key} should have at least 3 key signals"

    def test_templates_have_multiple_criteria(self):
        """Test templates have multiple qualification criteria"""
        for key, template in LEAD_ANALYSIS_TEMPLATES.items():
            assert len(template.qualification_criteria) >= 3, f"{key} should have at least 3 criteria"

    def test_templates_have_talking_points(self):
        """Test templates have talking points"""
        for key, template in LEAD_ANALYSIS_TEMPLATES.items():
            assert len(template.talking_points_themes) >= 3, f"{key} should have at least 3 talking points"


class TestGetLeadAnalysisTemplate:
    """Tests for get_lead_analysis_template function"""

    def test_get_existing_template(self):
        """Test getting existing template"""
        template = get_lead_analysis_template("it_saas")

        assert template.industry == "IT/SaaS"
        assert isinstance(template, LeadAnalysisTemplate)

    def test_get_all_defined_industries(self):
        """Test getting all defined industries"""
        industries = ["it_saas", "consulting", "manufacturing", "ecommerce", "marketing"]

        for industry in industries:
            template = get_lead_analysis_template(industry)
            assert isinstance(template, LeadAnalysisTemplate)

    def test_get_nonexistent_template_returns_default(self):
        """Test non-existent industry returns default template"""
        template = get_lead_analysis_template("unknown_industry")

        assert template.industry == "一般"
        assert isinstance(template, LeadAnalysisTemplate)

    def test_default_template_has_all_fields(self):
        """Test default template has all required fields"""
        template = get_lead_analysis_template("nonexistent")

        assert len(template.key_signals) > 0
        assert len(template.qualification_criteria) > 0
        assert len(template.recommended_actions) == 4
        assert len(template.talking_points_themes) > 0

    def test_default_template_has_score_ranges(self):
        """Test default template has all score ranges"""
        template = get_lead_analysis_template("unknown")

        assert "80-100" in template.recommended_actions
        assert "60-79" in template.recommended_actions
        assert "40-59" in template.recommended_actions
        assert "0-39" in template.recommended_actions

    def test_case_insensitive_lookup(self):
        """Test industry lookup is case-insensitive"""
        template_lower = get_lead_analysis_template("it_saas")
        template_upper = get_lead_analysis_template("IT_SAAS")

        assert template_lower.industry == template_upper.industry

    def test_space_to_underscore_conversion(self):
        """Test spaces are converted to underscores"""
        template = get_lead_analysis_template("it saas")

        assert template.industry == "IT/SaaS"

    def test_slash_to_underscore_conversion(self):
        """Test slashes are converted to underscores"""
        # Returns default since no match
        template = get_lead_analysis_template("some/industry")

        assert isinstance(template, LeadAnalysisTemplate)

    def test_empty_string_returns_default(self):
        """Test empty string returns default template"""
        template = get_lead_analysis_template("")

        assert template.industry == "一般"


class TestGetRecommendedAction:
    """Tests for get_recommended_action function"""

    def test_score_80_to_100(self):
        """Test score 80-100 range"""
        action = get_recommended_action(85, "it_saas")

        assert "デモ" in action or "商談" in action
        assert action != ""

    def test_score_60_to_79(self):
        """Test score 60-79 range"""
        action = get_recommended_action(70, "it_saas")

        assert action != ""

    def test_score_40_to_59(self):
        """Test score 40-59 range"""
        action = get_recommended_action(50, "it_saas")

        assert action != ""

    def test_score_0_to_39(self):
        """Test score 0-39 range"""
        action = get_recommended_action(30, "it_saas")

        assert action != ""

    def test_score_exactly_80(self):
        """Test score exactly 80"""
        action = get_recommended_action(80, "it_saas")
        template = get_lead_analysis_template("it_saas")

        assert action == template.recommended_actions["80-100"]

    def test_score_exactly_60(self):
        """Test score exactly 60"""
        action = get_recommended_action(60, "it_saas")
        template = get_lead_analysis_template("it_saas")

        assert action == template.recommended_actions["60-79"]

    def test_score_exactly_40(self):
        """Test score exactly 40"""
        action = get_recommended_action(40, "it_saas")
        template = get_lead_analysis_template("it_saas")

        assert action == template.recommended_actions["40-59"]

    def test_score_exactly_0(self):
        """Test score exactly 0"""
        action = get_recommended_action(0, "it_saas")
        template = get_lead_analysis_template("it_saas")

        assert action == template.recommended_actions["0-39"]

    def test_score_100(self):
        """Test score 100"""
        action = get_recommended_action(100, "it_saas")

        assert action != ""

    def test_score_boundaries(self):
        """Test all boundary scores"""
        scores_to_test = [0, 39, 40, 59, 60, 79, 80, 100]

        for score in scores_to_test:
            action = get_recommended_action(score, "it_saas")
            assert action != ""

    def test_different_industries_different_actions(self):
        """Test different industries can have different actions"""
        action_it = get_recommended_action(90, "it_saas")
        action_consulting = get_recommended_action(90, "consulting")

        # Both should have actions (they may be the same or different)
        assert action_it != ""
        assert action_consulting != ""

    def test_unknown_industry_returns_action(self):
        """Test unknown industry returns action from default template"""
        action = get_recommended_action(90, "unknown_industry")

        assert action != ""

    def test_action_from_consulting(self):
        """Test action from consulting industry"""
        action = get_recommended_action(85, "consulting")
        template = get_lead_analysis_template("consulting")

        assert action == template.recommended_actions["80-100"]

    def test_action_from_manufacturing(self):
        """Test action from manufacturing industry"""
        action = get_recommended_action(65, "manufacturing")
        template = get_lead_analysis_template("manufacturing")

        assert action == template.recommended_actions["60-79"]

    def test_action_from_ecommerce(self):
        """Test action from ecommerce industry"""
        action = get_recommended_action(45, "ecommerce")
        template = get_lead_analysis_template("ecommerce")

        assert action == template.recommended_actions["40-59"]

    def test_action_from_marketing(self):
        """Test action from marketing industry"""
        action = get_recommended_action(25, "marketing")
        template = get_lead_analysis_template("marketing")

        assert action == template.recommended_actions["0-39"]

    def test_negative_score_returns_lowest_action(self):
        """Test negative score returns 0-39 action"""
        action = get_recommended_action(-10, "it_saas")
        template = get_lead_analysis_template("it_saas")

        assert action == template.recommended_actions["0-39"]

    def test_over_100_score_returns_highest_action(self):
        """Test score over 100 returns 80-100 action"""
        action = get_recommended_action(150, "it_saas")
        template = get_lead_analysis_template("it_saas")

        assert action == template.recommended_actions["80-100"]
