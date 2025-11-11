"""
Microsoft Teams Incoming Webhook セットアップアシスタント
対話的にWebhook URLを設定
"""
import os
import sys

def print_header():
    print("\n" + "="*60)
    print("Microsoft Teams Incoming Webhook Setup")
    print("="*60)

def print_instructions():
    print("\n📋 このスクリプトはTeams Webhook URLを設定します。")
    print("\n⚠️  事前準備:")
    print("1. Microsoft Teams でテスト用チャネルを作成")
    print("   推奨名: 'DiagnoLeads Test'")
    print("2. チャネルで Incoming Webhook を設定")
    print("   チャネル名の横の ... → コネクタ → Incoming Webhook")
    print("3. Webhook URL をコピー")
    print("\n詳細な手順は docs/TEAMS_WEBHOOK_SETUP.md を参照してください。")

def validate_webhook_url(url: str) -> bool:
    """Webhook URLの基本的な検証"""
    if not url:
        return False
    
    if not url.startswith('https://'):
        print("❌ Error: Webhook URL must start with 'https://'")
        return False
    
    if 'webhook.office.com' not in url:
        print("❌ Error: This doesn't look like a valid Teams Webhook URL")
        print("   Expected: https://...webhook.office.com/...")
        return False
    
    return True

def read_existing_env():
    """既存の.envファイルを読み込み"""
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print("❌ Error: .env file not found")
        print(f"   Expected path: {os.path.abspath(env_path)}")
        return None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        return f.read()

def update_env_file(webhook_url: str):
    """環境変数ファイルを更新"""
    env_path = ".env"
    
    # 既存の内容を読み込み
    content = read_existing_env()
    if content is None:
        return False
    
    # TEAMS_WEBHOOK_URLが既に存在するか確認
    if 'TEAMS_WEBHOOK_URL=' in content:
        print("\n⚠️  TEAMS_WEBHOOK_URL is already set in .env")
        choice = input("Do you want to overwrite it? (yes/no): ")
        if choice.lower() != 'yes':
            print("❌ Setup cancelled")
            return False
        
        # 既存の行を置換
        lines = content.split('\n')
        new_lines = []
        replaced = False
        
        for line in lines:
            if line.startswith('TEAMS_WEBHOOK_URL='):
                new_lines.append(f"TEAMS_WEBHOOK_URL={webhook_url}")
                replaced = True
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    else:
        # 新規追加
        if not content.endswith('\n'):
            content += '\n'
        content += f"\n# Microsoft Teams Incoming Webhook\n"
        content += f"TEAMS_WEBHOOK_URL={webhook_url}\n"
    
    # ファイルに書き込み
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ Error writing to .env file: {e}")
        return False

def test_webhook_import():
    """Webhook Clientをインポート可能か確認"""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from app.integrations.microsoft.teams_webhook_client import TeamsWebhookClient
        return True
    except ImportError as e:
        print(f"⚠️  Warning: Cannot import TeamsWebhookClient: {e}")
        return False

def main():
    print_header()
    print_instructions()
    
    print("\n" + "="*60)
    
    # Webhook URLの入力
    print("\n📝 Please enter your Teams Incoming Webhook URL:")
    print("(Or press Ctrl+C to cancel)")
    
    try:
        webhook_url = input("\nWebhook URL: ").strip()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return
    
    # 検証
    if not validate_webhook_url(webhook_url):
        print("\n❌ Invalid Webhook URL")
        print("\nPlease check:")
        print("1. URL starts with 'https://'")
        print("2. URL contains 'webhook.office.com'")
        print("3. URL is complete (no line breaks)")
        return
    
    print("\n✅ Webhook URL looks valid")
    
    # URL の一部を表示（セキュリティのため）
    url_preview = webhook_url[:50] + "..." if len(webhook_url) > 50 else webhook_url
    print(f"Preview: {url_preview}")
    
    # 確認
    print("\n" + "="*60)
    print("Confirmation")
    print("="*60)
    confirm = input("\nSave this Webhook URL to .env file? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Setup cancelled")
        return
    
    # .envファイルを更新
    print("\n💾 Updating .env file...")
    if update_env_file(webhook_url):
        print("✅ Webhook URL saved successfully!")
        
        # 次のステップを表示
        print("\n" + "="*60)
        print("✅ Setup Complete!")
        print("="*60)
        print("\n🎯 Next Steps:")
        print("\n1. Test the webhook:")
        print("   ./venv/bin/python app/integrations/microsoft/teams_webhook_client.py")
        print("\n2. Check your Teams channel for test messages")
        print("\n3. If successful, you can now integrate into DiagnoLeads app")
        print("\n📖 For more details, see: docs/TEAMS_WEBHOOK_SETUP.md")
        print("="*60)
    else:
        print("❌ Failed to save Webhook URL")
        print("Please check file permissions and try again")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
