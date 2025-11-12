# GitHub Issues Created for Phase 1

## ✅ Created Issues

### Issue #1: [Phase1][M1] Azure AD & Bot Framework初期セットアップ
- **URL**: https://github.com/yusuke-kurosawa/DiagnoLeads/issues/1
- **Milestone**: 1 - Teams統合基盤 (Week 1-3)
- **Labels**: phase-1, infrastructure, priority-critical
- **Status**: Open

---

## 📋 Remaining Issues to Create (11 issues)

以下のIssueを手動で作成してください（GitHub UIまたはgh cliで）：

### Milestone 1: Teams統合基盤 (Week 1-3)

**Issue #2**: [Phase1][M1] Microsoft Graph API統合とTeamsClient実装
- Labels: phase-1, backend, priority-high
- Tasks: TeamsClient実装、認証フロー、DB schema、API endpoints、tests

**Issue #3**: [Phase1][M1] Adaptive Cards通知機能実装
- Labels: phase-1, backend, frontend, priority-high
- Tasks: Adaptive Card templates、通知ロジック、フロントエンド設定画面

---

### Milestone 2: Teams Bot対話機能 (Week 4-6)

**Issue #4**: [Phase1][M2] Teams Bot基礎実装とWebhook受信
- Labels: phase-1, backend, priority-high
- Tasks: Bot Framework統合、Webhook受信、セッション管理

**Issue #5**: [Phase1][M2] Bot対話型診断フロー実装
- Labels: phase-1, backend, priority-high
- Tasks: 質問送信、Quick Reply、回答処理、完了フロー

**Issue #6**: [Phase1][M2] Teams Bot E2Eテストと性能最適化
- Labels: phase-1, testing, priority-medium
- Tasks: E2Eテスト、エラーハンドリング、パフォーマンス最適化

---

### Milestone 3: LINE統合 (Week 7-9)

**Issue #7**: [Phase1][M3] LINE Messaging API統合基盤
- Labels: phase-1, backend, priority-high
- Tasks: LINE SDK統合、DB schema、API endpoints

**Issue #8**: [Phase1][M3] LINE Bot対話型診断実装
- Labels: phase-1, backend, priority-high
- Tasks: Flex Message、Bot対話、Quick Reply

**Issue #9**: [Phase1][M3] LINEブロードキャストと分析ダッシュボード
- Labels: phase-1, backend, frontend, priority-medium
- Tasks: ブロードキャスト機能、分析画面、リッチメニュー

---

### Milestone 4: QR & SMS (Week 10-11)

**Issue #10**: [Phase1][M4] QRコード生成とトラッキング実装
- Labels: phase-1, backend, frontend, priority-medium
- Tasks: QRコード生成、ポスターPDF、トラッキング

**Issue #11**: [Phase1][M4] Twilio SMS配信機能実装
- Labels: phase-1, backend, frontend, priority-medium
- Tasks: Twilio統合、SMS送信、配信ステータス追跡

---

### Milestone 5: AI A/Bテスト (Week 12)

**Issue #12**: [Phase1][M5] AI A/Bテストエンジン実装
- Labels: phase-1, backend, frontend, ai, priority-high
- Tasks: A/Bテストエンジン、統計計算、トンプソンサンプリング、ダッシュボード

---

## 🏷️ Labels Created

- ✅ phase-1 (緑)
- ✅ infrastructure (紫)
- ✅ backend (青)
- ✅ frontend (黄)
- ✅ testing (紫)
- ✅ priority-critical (赤)
- ✅ priority-high (オレンジ)
- ✅ priority-medium (黄)

---

## 📊 Milestones Created

1. ✅ Milestone 1: Teams統合基盤 (Week 1-3) - Due: 2025-12-08
2. ✅ Milestone 2: Teams Bot対話機能 (Week 4-6) - Due: 2025-12-29
3. ✅ Milestone 3: LINE統合 (Week 7-9) - Due: 2026-01-19
4. ✅ Milestone 4: QR & SMS (Week 10-11) - Due: 2026-02-02
5. ✅ Milestone 5: AI A/Bテスト (Week 12) - Due: 2026-02-09

---

## 🚀 Quick Create Commands

```bash
# Issue #2
gh issue create --title "[Phase1][M1] Microsoft Graph API統合とTeamsClient実装" \
  --milestone "Milestone 1: Teams統合基盤 (Week 1-3)" \
  --label "phase-1,backend,priority-high" \
  --body "TeamsClient実装、認証フロー、DB schema、API endpoints、tests"

# Issue #3
gh issue create --title "[Phase1][M1] Adaptive Cards通知機能実装" \
  --milestone "Milestone 1: Teams統合基盤 (Week 1-3)" \
  --label "phase-1,backend,frontend,priority-high" \
  --body "Adaptive Card templates、通知ロジック、フロントエンド設定画面"

# (以降同様に#4-#12を作成)
```

---

**Last Updated**: 2025-11-11  
**Created By**: Droid
