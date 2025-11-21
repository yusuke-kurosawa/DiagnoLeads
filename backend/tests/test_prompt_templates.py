"""
Tests for Prompt Templates

Comprehensive tests for AI prompt generation templates.
"""

import pytest

from app.services.ai.prompt_templates import (
    IndustryTemplateData,
    LeadAnalysisTemplateData,
    PromptTemplates,
)


class TestPromptTemplatesVersion:
    """Tests for PromptTemplates version"""

    def test_version_exists(self):
        """Test VERSION constant exists"""
        assert hasattr(PromptTemplates, "VERSION")

    def test_version_is_string(self):
        """Test VERSION is a string"""
        assert isinstance(PromptTemplates.VERSION, str)

    def test_version_not_empty(self):
        """Test VERSION is not empty"""
        assert PromptTemplates.VERSION != ""


class TestIndustryTemplateDataDataclass:
    """Tests for IndustryTemplateData dataclass"""

    def test_creation(self):
        """Test creating IndustryTemplateData"""
        data = IndustryTemplateData(
            name="IT",
            description="IT services",
            common_pain_points=["pain1"],
            question_themes=["theme1"],
            scoring_guidelines="scoring",
            example_questions=["q1"],
        )

        assert data.name == "IT"
        assert data.description == "IT services"


class TestLeadAnalysisTemplateDataDataclass:
    """Tests for LeadAnalysisTemplateData dataclass"""

    def test_creation(self):
        """Test creating LeadAnalysisTemplateData"""
        data = LeadAnalysisTemplateData(
            industry="IT",
            key_signals=["signal1"],
            qualification_criteria=["criteria1"],
            talking_points_themes=["theme1"],
        )

        assert data.industry == "IT"
        assert len(data.key_signals) == 1


class TestBuildAssessmentGenerationPrompt:
    """Tests for build_assessment_generation_prompt"""

    @pytest.fixture
    def industry_data(self):
        """Fixture providing industry template data"""
        return IndustryTemplateData(
            name="IT/SaaS",
            description="Software as a Service",
            common_pain_points=["Scalability", "Security", "Cost"],
            question_themes=["Current tools", "Team size", "Budget"],
            scoring_guidelines="Score based on maturity",
            example_questions=["What tools do you use?", "Team size?", "Budget?"],
        )

    def test_prompt_contains_topic(self, industry_data):
        """Test prompt contains the topic"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Lead Qualification",
            num_questions=5,
            industry_template=industry_data,
        )

        assert "Lead Qualification" in prompt

    def test_prompt_contains_industry_name(self, industry_data):
        """Test prompt contains industry name"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=5,
            industry_template=industry_data,
        )

        assert "IT/SaaS" in prompt

    def test_prompt_contains_num_questions(self, industry_data):
        """Test prompt contains number of questions"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=7,
            industry_template=industry_data,
        )

        assert "7" in prompt

    def test_prompt_contains_pain_points(self, industry_data):
        """Test prompt contains pain points"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=5,
            industry_template=industry_data,
        )

        assert "Scalability" in prompt
        assert "Security" in prompt
        assert "Cost" in prompt

    def test_prompt_contains_question_themes(self, industry_data):
        """Test prompt contains question themes"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=5,
            industry_template=industry_data,
        )

        assert "Current tools" in prompt
        assert "Team size" in prompt

    def test_prompt_contains_scoring_guidelines(self, industry_data):
        """Test prompt contains scoring guidelines"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=5,
            industry_template=industry_data,
        )

        assert "Score based on maturity" in prompt

    def test_prompt_contains_example_questions(self, industry_data):
        """Test prompt contains example questions"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=5,
            industry_template=industry_data,
        )

        assert "What tools do you use?" in prompt

    def test_prompt_contains_json_format_instructions(self, industry_data):
        """Test prompt contains JSON format instructions"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=5,
            industry_template=industry_data,
        )

        assert "JSON" in prompt
        assert "title" in prompt
        assert "questions" in prompt

    def test_prompt_returns_string(self, industry_data):
        """Test prompt returns string"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=5,
            industry_template=industry_data,
        )

        assert isinstance(prompt, str)

    def test_prompt_not_empty(self, industry_data):
        """Test prompt is not empty"""
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic="Test",
            num_questions=5,
            industry_template=industry_data,
        )

        assert len(prompt) > 100

    def test_different_topics_generate_different_prompts(self, industry_data):
        """Test different topics generate different prompts"""
        prompt1 = PromptTemplates.build_assessment_generation_prompt(
            topic="Topic A",
            num_questions=5,
            industry_template=industry_data,
        )
        prompt2 = PromptTemplates.build_assessment_generation_prompt(
            topic="Topic B",
            num_questions=5,
            industry_template=industry_data,
        )

        assert prompt1 != prompt2
        assert "Topic A" in prompt1
        assert "Topic B" in prompt2


class TestBuildLeadAnalysisPrompt:
    """Tests for build_lead_analysis_prompt"""

    @pytest.fixture
    def lead_data(self):
        """Fixture providing lead analysis template data"""
        return LeadAnalysisTemplateData(
            industry="IT/SaaS",
            key_signals=["System challenges", "Budget", "Timeline"],
            qualification_criteria=["Has budget", "Decision authority", "Urgency"],
            talking_points_themes=["ROI", "Integration", "Security"],
        )

    @pytest.fixture
    def responses(self):
        """Fixture providing assessment responses"""
        return {
            "q1": "Current system is slow",
            "q2": "Budget: $50k",
            "q3": "Timeline: 3 months",
        }

    def test_prompt_contains_industry(self, lead_data, responses):
        """Test prompt contains industry"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Test Assessment",
            lead_template=lead_data,
        )

        assert "IT/SaaS" in prompt

    def test_prompt_contains_assessment_title(self, lead_data, responses):
        """Test prompt contains assessment title"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Lead Qualification",
            lead_template=lead_data,
        )

        assert "Lead Qualification" in prompt

    def test_prompt_contains_key_signals(self, lead_data, responses):
        """Test prompt contains key signals"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Test",
            lead_template=lead_data,
        )

        assert "System challenges" in prompt
        assert "Budget" in prompt
        assert "Timeline" in prompt

    def test_prompt_contains_qualification_criteria(self, lead_data, responses):
        """Test prompt contains qualification criteria"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Test",
            lead_template=lead_data,
        )

        assert "Has budget" in prompt
        assert "Decision authority" in prompt

    def test_prompt_contains_talking_points(self, lead_data, responses):
        """Test prompt contains talking points"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Test",
            lead_template=lead_data,
        )

        assert "ROI" in prompt
        assert "Integration" in prompt
        assert "Security" in prompt

    def test_prompt_contains_responses_data(self, lead_data, responses):
        """Test prompt contains response data"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Test",
            lead_template=lead_data,
        )

        # Should contain response values
        assert "Current system is slow" in prompt or "q1" in prompt

    def test_prompt_contains_json_format_instructions(self, lead_data, responses):
        """Test prompt contains JSON format instructions"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Test",
            lead_template=lead_data,
        )

        assert "JSON" in prompt
        assert "overall_score" in prompt
        assert "hot_lead" in prompt

    def test_prompt_returns_string(self, lead_data, responses):
        """Test prompt returns string"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Test",
            lead_template=lead_data,
        )

        assert isinstance(prompt, str)

    def test_prompt_not_empty(self, lead_data, responses):
        """Test prompt is not empty"""
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses,
            assessment_title="Test",
            lead_template=lead_data,
        )

        assert len(prompt) > 100

    def test_different_responses_generate_different_prompts(self, lead_data):
        """Test different responses generate different prompts"""
        responses1 = {"q1": "Answer A"}
        responses2 = {"q1": "Answer B"}

        prompt1 = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses1,
            assessment_title="Test",
            lead_template=lead_data,
        )
        prompt2 = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=responses2,
            assessment_title="Test",
            lead_template=lead_data,
        )

        assert prompt1 != prompt2


class TestBuildRephrasePrompt:
    """Tests for build_rephrase_prompt"""

    def test_prompt_contains_text(self):
        """Test prompt contains the text to rephrase"""
        prompt = PromptTemplates.build_rephrase_prompt(
            text="Hello world",
            style="professional",
            target_audience="executives",
        )

        assert "Hello world" in prompt

    def test_prompt_contains_style(self):
        """Test prompt contains the style"""
        prompt = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="casual",
            target_audience="students",
        )

        assert "casual" in prompt

    def test_prompt_contains_target_audience(self):
        """Test prompt contains target audience"""
        prompt = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="formal",
            target_audience="executives",
        )

        assert "executives" in prompt

    def test_prompt_contains_json_format(self):
        """Test prompt contains JSON format instructions"""
        prompt = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="formal",
            target_audience="general",
        )

        assert "JSON" in prompt
        assert "original" in prompt
        assert "rephrased" in prompt
        assert "alternatives" in prompt

    def test_prompt_returns_string(self):
        """Test prompt returns string"""
        prompt = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="formal",
            target_audience="general",
        )

        assert isinstance(prompt, str)

    def test_prompt_not_empty(self):
        """Test prompt is not empty"""
        prompt = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="formal",
            target_audience="general",
        )

        assert len(prompt) > 50

    def test_different_texts_generate_different_prompts(self):
        """Test different texts generate different prompts"""
        prompt1 = PromptTemplates.build_rephrase_prompt(
            text="Text A",
            style="formal",
            target_audience="general",
        )
        prompt2 = PromptTemplates.build_rephrase_prompt(
            text="Text B",
            style="formal",
            target_audience="general",
        )

        assert prompt1 != prompt2

    def test_different_styles_generate_different_prompts(self):
        """Test different styles generate different prompts"""
        prompt1 = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="formal",
            target_audience="general",
        )
        prompt2 = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="casual",
            target_audience="general",
        )

        assert prompt1 != prompt2
        assert "formal" in prompt1
        assert "casual" in prompt2

    def test_different_audiences_generate_different_prompts(self):
        """Test different audiences generate different prompts"""
        prompt1 = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="formal",
            target_audience="executives",
        )
        prompt2 = PromptTemplates.build_rephrase_prompt(
            text="Test",
            style="formal",
            target_audience="students",
        )

        assert prompt1 != prompt2
        assert "executives" in prompt1
        assert "students" in prompt2
