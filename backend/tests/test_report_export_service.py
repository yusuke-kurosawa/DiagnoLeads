"""
Tests for Report Export Service

Comprehensive test coverage for report_export_service.py
Target: 100% coverage
"""

import io
from unittest.mock import MagicMock, patch

import pytest

from app.services.report_export_service import ReportExportService


class TestReportExportServiceCSV:
    """Tests for CSV export"""

    def test_export_to_csv_basic(self):
        """Test basic CSV export"""
        service = ReportExportService()

        data_points = [
            {"label": "January", "values": {"leads_total": 10, "conversion_rate": 25.5}},
            {"label": "February", "values": {"leads_total": 15, "conversion_rate": 30.0}},
        ]

        result = service.export_to_csv("Monthly Report", data_points)

        assert isinstance(result, bytes)
        csv_content = result.decode("utf-8")
        assert "Label" in csv_content
        assert "leads_total" in csv_content
        assert "conversion_rate" in csv_content
        assert "January" in csv_content
        assert "February" in csv_content

    def test_export_to_csv_empty_data(self):
        """Test CSV export with empty data"""
        service = ReportExportService()

        result = service.export_to_csv("Empty Report", [])

        assert result == b""

    def test_export_to_csv_multiple_metrics(self):
        """Test CSV export with multiple metrics"""
        service = ReportExportService()

        data_points = [
            {"label": "Week 1", "values": {"metric1": 100, "metric2": 200, "metric3": 300}},
            {"label": "Week 2", "values": {"metric1": 150, "metric2": 250}},  # Missing metric3
        ]

        result = service.export_to_csv("Weekly Report", data_points)

        csv_content = result.decode("utf-8")
        assert "metric1" in csv_content
        assert "metric2" in csv_content
        assert "metric3" in csv_content
        # Week 2 should have 0 for metric3
        lines = csv_content.strip().split("\n")
        assert len(lines) == 3  # Header + 2 data rows


class TestReportExportServiceExcel:
    """Tests for Excel export"""

    @patch("openpyxl.Workbook")
    def test_export_to_excel_basic(self, mock_workbook_class):
        """Test basic Excel export"""
        service = ReportExportService()

        # Mock workbook
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_wb.worksheets = [mock_ws]
        mock_wb.create_sheet.return_value = MagicMock()
        mock_workbook_class.return_value = mock_wb

        # Mock save to return bytes
        def save_side_effect(output):
            output.write(b"mock excel data")

        mock_wb.save.side_effect = save_side_effect

        data_points = [{"label": "Q1", "values": {"revenue": 10000, "customers": 50}}]

        summary = {"total_revenue": 10000, "total_customers": 50}

        config = {"metrics": ["revenue", "customers"], "group_by": "quarter"}

        result = service.export_to_excel("Quarterly Report", data_points, summary, config)

        assert isinstance(result, bytes)
        assert mock_wb.save.called

    def test_export_to_excel_import_error(self):
        """Test Excel export when openpyxl is not installed"""
        service = ReportExportService()

        with patch.dict("sys.modules", {"openpyxl": None}):
            with pytest.raises(ImportError, match="openpyxl is required"):
                service.export_to_excel("Test", [], {}, {})

    @patch("openpyxl.Workbook")
    def test_export_to_excel_empty_data(self, mock_workbook_class):
        """Test Excel export with empty data points"""
        service = ReportExportService()

        # Mock workbook
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_wb.worksheets = [mock_ws]
        mock_wb.create_sheet.return_value = MagicMock()
        mock_workbook_class.return_value = mock_wb

        def save_side_effect(output):
            output.write(b"mock excel data")

        mock_wb.save.side_effect = save_side_effect

        result = service.export_to_excel("Empty Report", [], {}, {"metrics": []})

        assert isinstance(result, bytes)

    @patch("openpyxl.Workbook")
    @patch("openpyxl.styles.Font")
    @patch("openpyxl.styles.PatternFill")
    @patch("openpyxl.utils.get_column_letter")
    def test_export_to_excel_with_formatting(self, mock_get_col, mock_fill, mock_font, mock_wb_class):
        """Test Excel export includes formatting"""
        service = ReportExportService()

        # Mock dependencies
        mock_get_col.side_effect = lambda x: chr(64 + x)  # A, B, C, etc.
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_wb.worksheets = [mock_ws]
        mock_ws.columns = []
        mock_wb.create_sheet.return_value = MagicMock()
        mock_wb_class.return_value = mock_wb

        def save_side_effect(output):
            output.write(b"formatted excel")

        mock_wb.save.side_effect = save_side_effect

        data_points = [{"label": "Test", "values": {"metric1": 123.456}}]

        result = service.export_to_excel(
            "Formatted Report", data_points, {"summary_key": "value"}, {"metrics": ["metric1"], "filters": {}}
        )

        assert isinstance(result, bytes)
        # Verify formatting functions were called
        assert mock_font.called
        assert mock_fill.called


class TestReportExportServicePDF:
    """Tests for PDF export"""

    @patch("reportlab.platypus.SimpleDocTemplate")
    @patch("reportlab.lib.styles.getSampleStyleSheet")
    @patch("reportlab.platypus.Paragraph")
    @patch("reportlab.platypus.Table")
    def test_export_to_pdf_basic(self, mock_table, mock_paragraph, mock_styles, mock_doc_class):
        """Test basic PDF export"""
        service = ReportExportService()

        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc_class.return_value = mock_doc

        def build_side_effect(story):
            # Simulate writing to buffer
            pass

        mock_doc.build.side_effect = build_side_effect

        # Mock styles
        mock_styles.return_value = {
            "Heading1": MagicMock(),
            "Heading2": MagicMock(),
            "Normal": MagicMock(),
        }

        data_points = [{"label": "Product A", "values": {"sales": 5000, "profit": 1000}}]

        summary = {"total_sales": 5000, "total_profit": 1000}

        config = {"metrics": ["sales", "profit"], "group_by": "product", "visualization": "table"}

        result = service.export_to_pdf("Sales Report", data_points, summary, config, include_charts=False)

        assert isinstance(result, bytes)
        assert mock_doc.build.called

    def test_export_to_pdf_import_error(self):
        """Test PDF export when reportlab is not installed"""
        service = ReportExportService()

        with patch.dict("sys.modules", {"reportlab": None, "reportlab.lib": None, "reportlab.platypus": None}):
            with pytest.raises(ImportError, match="reportlab is required"):
                service.export_to_pdf("Test", [], {}, {})

    @patch("reportlab.platypus.SimpleDocTemplate")
    @patch("reportlab.lib.styles.getSampleStyleSheet")
    @patch("reportlab.platypus.Paragraph")
    @patch("reportlab.platypus.Table")
    @patch("reportlab.platypus.TableStyle")
    @patch("reportlab.platypus.Spacer")
    @patch("reportlab.platypus.PageBreak")
    def test_export_to_pdf_empty_data(
        self, mock_pagebreak, mock_spacer, mock_tablestyle, mock_table, mock_paragraph, mock_styles, mock_doc_class
    ):
        """Test PDF export with empty data points"""
        service = ReportExportService()

        mock_doc = MagicMock()
        mock_doc_class.return_value = mock_doc
        mock_doc.build.side_effect = lambda story: None

        mock_styles.return_value = {
            "Heading1": MagicMock(),
            "Heading2": MagicMock(),
            "Normal": MagicMock(),
        }

        result = service.export_to_pdf("Empty Report", [], {"period": "custom"}, {"metrics": []})

        assert isinstance(result, bytes)
        assert mock_doc.build.called

    @patch("reportlab.platypus.SimpleDocTemplate")
    @patch("reportlab.lib.styles.getSampleStyleSheet")
    @patch("reportlab.platypus.Paragraph")
    @patch("reportlab.platypus.Table")
    @patch("reportlab.platypus.TableStyle")
    @patch("reportlab.lib.styles.ParagraphStyle")
    def test_export_to_pdf_with_filters(
        self, mock_para_style, mock_tablestyle, mock_table, mock_paragraph, mock_styles, mock_doc_class
    ):
        """Test PDF export with filters in config"""
        service = ReportExportService()

        mock_doc = MagicMock()
        mock_doc_class.return_value = mock_doc
        mock_doc.build.side_effect = lambda story: None

        mock_styles.return_value = {
            "Heading1": MagicMock(),
            "Heading2": MagicMock(),
            "Normal": MagicMock(),
        }

        # Mock ParagraphStyle to return a mock style
        mock_style = MagicMock()
        mock_para_style.return_value = mock_style

        data_points = [{"label": "Filtered", "values": {"count": 10}}]

        summary = {"total": 10}

        config = {
            "metrics": ["count"],
            "filters": {"status": ["active"], "date_range": {"start": "2024-01-01"}},
            "group_by": "status",
            "visualization": "bar_chart",
        }

        result = service.export_to_pdf("Filtered Report", data_points, summary, config, include_charts=True)

        assert isinstance(result, bytes)

    @patch("reportlab.platypus.SimpleDocTemplate")
    @patch("reportlab.lib.styles.getSampleStyleSheet")
    @patch("reportlab.platypus.Paragraph")
    @patch("reportlab.platypus.Table")
    def test_export_to_pdf_float_formatting(self, mock_table, mock_paragraph, mock_styles, mock_doc_class):
        """Test PDF export formats float values correctly"""
        service = ReportExportService()

        mock_doc = MagicMock()
        mock_doc_class.return_value = mock_doc
        mock_doc.build.side_effect = lambda story: None

        mock_styles.return_value = {
            "Heading1": MagicMock(),
            "Heading2": MagicMock(),
            "Normal": MagicMock(),
        }

        data_points = [
            {"label": "Item 1", "values": {"rate": 12.3456, "count": 100}},
            {"label": "Item 2", "values": {"rate": 98.7654, "count": 200}},
        ]

        summary = {}
        config = {"metrics": ["rate", "count"]}

        result = service.export_to_pdf("Float Test", data_points, summary, config)

        assert isinstance(result, bytes)
        # Verify Table was called (formatting happens inside)
        assert mock_table.called
