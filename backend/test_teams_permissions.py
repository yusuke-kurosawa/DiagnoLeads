"""
Microsoft Teams API権限テストスクリプト
各APIエンドポイントを個別にテストして、どの権限が正しく設定されているかを確認
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()


async def get_access_token():
    """アクセストークンを取得"""
    tenant_id = os.getenv("MICROSOFT_TENANT_ID")
    client_id = os.getenv("MICROSOFT_CLIENT_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        response.raise_for_status()
        result = response.json()
        return result["access_token"]


async def test_api_endpoint(name, url, token, required_permission):
    """APIエンドポイントをテスト"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print(f"\n{'=' * 60}")
    print(f"Testing: {name}")
    print(f"Endpoint: {url}")
    print(f"Required Permission: {required_permission}")
    print(f"{'=' * 60}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                result = response.json()
                count = len(result.get("value", []))
                print(f"✅ SUCCESS: Retrieved {count} items")
                print(f"Status: {response.status_code}")
                return True
            elif response.status_code == 403:
                error_data = response.json()
                print("❌ PERMISSION DENIED (403)")
                print(
                    f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                )
                print("\n💡 Solution:")
                print("   1. Go to Azure Portal → App registrations")
                print("   2. Select your app → API permissions")
                print(
                    f"   3. Add '{required_permission}' under Microsoft Graph → Application permissions"
                )
                print("   4. Click 'Grant admin consent for [Your Org]'")
                return False
            else:
                print(f"⚠️  UNEXPECTED STATUS: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


async def main():
    print("\n" + "=" * 60)
    print("Microsoft Teams API Permissions Test")
    print("=" * 60)

    # 認証
    print("\n1. Getting Access Token...")
    try:
        token = await get_access_token()
        print("✅ Access token acquired successfully")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    # テストケース
    tests = [
        {
            "name": "Organization Info",
            "url": "https://graph.microsoft.com/v1.0/organization",
            "permission": "Organization.Read.All (optional)",
        },
        {
            "name": "All Groups (for Teams)",
            "url": "https://graph.microsoft.com/v1.0/groups?$top=5",
            "permission": "Group.Read.All",
        },
        {
            "name": "Groups with Team filter",
            "url": "https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')&$top=5",
            "permission": "Group.Read.All + Team.ReadBasic.All",
        },
        {
            "name": "All Users",
            "url": "https://graph.microsoft.com/v1.0/users?$top=5",
            "permission": "User.Read.All",
        },
    ]

    results = []
    for test in tests:
        success = await test_api_endpoint(
            test["name"], test["url"], token, test["permission"]
        )
        results.append((test["name"], success))
        await asyncio.sleep(0.5)  # Rate limiting対策

    # サマリー
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Teams integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the permissions above.")
        print("\nCommon issues:")
        print("1. Permissions not added in Azure Portal")
        print("2. Admin consent not granted")
        print("3. Wrong permission type (Delegated vs Application)")
        print("4. Need to wait 5-10 minutes for permission changes to propagate")


if __name__ == "__main__":
    asyncio.run(main())
