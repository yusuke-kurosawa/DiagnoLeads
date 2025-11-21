"""
Tests for Redirect API Helper Functions

Test coverage for device parsing and IP extraction functions.
"""

from unittest.mock import MagicMock

from app.api.v1.redirect import get_client_ip, parse_device_info


class TestParseDeviceInfo:
    """Tests for parse_device_info function"""

    def test_parse_mobile_user_agent(self):
        """Test parsing mobile device user agent"""
        ua_string = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"

        result = parse_device_info(ua_string)

        assert result["device_type"] == "mobile"
        assert "iOS" in result["os"] or "iPhone" in result["os"]

    def test_parse_tablet_user_agent(self):
        """Test parsing tablet device user agent"""
        ua_string = "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15"

        result = parse_device_info(ua_string)

        assert result["device_type"] in ["tablet", "mobile"]  # iPad can be detected as either

    def test_parse_desktop_user_agent(self):
        """Test parsing desktop user agent"""
        ua_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124"

        result = parse_device_info(ua_string)

        assert result["device_type"] == "desktop"
        assert "Windows" in result["os"]
        assert "Chrome" in result["browser"]

    def test_parse_mac_desktop_user_agent(self):
        """Test parsing Mac desktop user agent"""
        ua_string = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"

        result = parse_device_info(ua_string)

        assert result["device_type"] == "desktop"
        assert "Mac" in result["os"]

    def test_parse_android_mobile_user_agent(self):
        """Test parsing Android mobile user agent"""
        ua_string = "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/91.0.4472.120"

        result = parse_device_info(ua_string)

        # user_agents library may classify some Android devices as tablet
        assert result["device_type"] in ("mobile", "tablet")
        assert "Android" in result["os"]

    def test_parse_unknown_user_agent(self):
        """Test parsing unknown/empty user agent"""
        ua_string = ""

        result = parse_device_info(ua_string)

        assert result["device_type"] == "unknown"
        # user_agents library returns "Other" for empty UA
        assert result["os"] in ("Unknown", "Other")
        assert result["browser"] in ("Unknown", "Other")

    def test_parse_firefox_user_agent(self):
        """Test parsing Firefox user agent"""
        ua_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"

        result = parse_device_info(ua_string)

        assert result["device_type"] == "desktop"
        assert "Firefox" in result["browser"]

    def test_parse_edge_user_agent(self):
        """Test parsing Edge user agent"""
        ua_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/91.0.864.59"

        result = parse_device_info(ua_string)

        assert result["device_type"] == "desktop"
        assert result["browser"] is not None


class TestGetClientIP:
    """Tests for get_client_ip function"""

    def test_get_ip_from_direct_connection(self):
        """Test getting IP from direct connection"""
        request = MagicMock()
        request.client.host = "192.168.1.100"
        request.headers.get.return_value = None

        ip = get_client_ip(request)

        assert ip == "192.168.1.100"

    def test_get_ip_from_x_forwarded_for(self):
        """Test getting IP from X-Forwarded-For header"""
        request = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers.get.return_value = "203.0.113.1, 198.51.100.1"

        ip = get_client_ip(request)

        # Should get first IP from X-Forwarded-For
        assert ip == "203.0.113.1"

    def test_get_ip_from_single_x_forwarded_for(self):
        """Test getting IP from X-Forwarded-For with single IP"""
        request = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers.get.return_value = "203.0.113.1"

        ip = get_client_ip(request)

        assert ip == "203.0.113.1"

    def test_get_ip_no_client(self):
        """Test getting IP when client is None"""
        request = MagicMock()
        request.client = None
        request.headers.get.return_value = None

        ip = get_client_ip(request)

        assert ip == "unknown"

    def test_get_ipv6_address(self):
        """Test getting IPv6 address"""
        request = MagicMock()
        request.client.host = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        request.headers.get.return_value = None

        ip = get_client_ip(request)

        assert "2001" in ip
