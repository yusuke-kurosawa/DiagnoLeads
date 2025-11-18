# Frontend Setup Instructions

## Google Analytics 4 Integration

The DiagnoLeads frontend now includes Google Analytics 4 (GA4) tracking capabilities. Follow these instructions to set up the required dependencies.

### Required Dependencies

The following packages are required for GA4 tracking:

- `react-ga4`: Google Analytics 4 for React
- `react-cookie-consent`: GDPR/CCPA compliant cookie consent banner

### Installation

These packages are already listed in `package.json`, but you need to install them:

```bash
cd frontend
npm install
```

This will install:
- `react-ga4@^2.1.0`
- `react-cookie-consent@^9.0.0`

### Verify Installation

After installation, verify the packages are installed:

```bash
npm list react-ga4
npm list react-cookie-consent
```

You should see the installed versions.

### Development Server

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### GA4 Setup (Backend Required)

For GA4 tracking to work, you also need:

1. **Backend running** with GA4 integration endpoints
2. **GA4 configured** in Settings → Integrations → Google Analytics 4
3. **Measurement ID** entered (format: G-XXXXXXXXXX)

### Testing GA4 Tracking

1. **Open browser console**
   ```
   Right-click → Inspect → Console tab
   ```

2. **Navigate the app**
   - You should see console logs like:
   ```
   GA4: Initialized with Measurement ID: G-XXXXXXXXXX
   GA4: Page view tracked - /dashboard
   GA4: Event tracked - assessment_created {...}
   ```

3. **Check GA4 Realtime Report**
   - Go to [Google Analytics](https://analytics.google.com/)
   - Select your property
   - Reports → Realtime
   - Events should appear within 30 seconds

### Cookie Consent

On first visit, a cookie consent banner will appear at the bottom of the screen. Users must click "同意する" (Agree) to enable GA4 tracking.

To reset cookie consent for testing:

```javascript
// In browser console
localStorage.removeItem('diagnoleads_cookie_consent');
location.reload();
```

### Troubleshooting

#### GA4 not initializing

1. Check backend is running: `http://localhost:8000`
2. Check GA4 is configured in Settings → Integrations
3. Check browser console for error messages
4. Verify Measurement ID format (G-XXXXXXXXXX)

#### Events not appearing in GA4

1. Ensure cookie consent is given
2. Wait 30-60 seconds (GA4 has some latency)
3. Check GA4 Realtime Report (not Overview Report)
4. Verify browser console shows "GA4: Event tracked" messages

#### Cookie consent banner not showing

```javascript
// Reset and reload
localStorage.removeItem('diagnoleads_cookie_consent');
location.reload();
```

## Additional Resources

- [GA4 Tracking Examples](../docs/GA4_TRACKING_EXAMPLES.md)
- [Phase 3 Summary](../docs/GOOGLE_ANALYTICS_PHASE3_SUMMARY.md)
- [react-ga4 Documentation](https://github.com/codler/react-ga4)

---

**Last Updated:** 2025-11-18
**Version:** Phase 3
