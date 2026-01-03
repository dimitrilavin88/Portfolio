# Deployment Checklist for Hostinger

## Required Files to Upload

### Root Directory Files:
- ✅ `index.html`
- ✅ `styles.css` (IMPORTANT: Make sure this is the updated one, not the old one)
- ✅ `script.js`
- ✅ `LICENSE` (optional)
- ✅ `README.md` (optional)

### Directory Structure:
```
/
├── index.html
├── styles.css          ← Make sure this is the UPDATED file with dark mode
├── script.js
├── src/
│   ├── app.js
│   └── images/
│       ├── DL-Logo.png
│       ├── missionarypic.png
│       ├── Dimitri-Lavin-Resume.pdf
│       ├── planno.png
│       ├── tastyfood.png
│       └── fantasyPL.png
└── pages/
    └── fpl.html (if needed)
```

## Common Issues & Solutions

### 1. CSS Not Loading
**Problem**: Website looks unstyled
**Solution**: 
- Verify `styles.css` is in the root directory
- Check file permissions (should be 644)
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser console for 404 errors

### 2. Images Not Showing
**Problem**: Images are broken
**Solution**:
- Verify all images are in `src/images/` directory
- Check file names match exactly (case-sensitive on Linux)
- Ensure file extensions are correct (.png, .pdf, etc.)

### 3. JavaScript Not Working
**Problem**: Dark mode toggle, navigation, etc. not working
**Solution**:
- Verify `src/app.js` and `script.js` are uploaded
- Check browser console for JavaScript errors
- Ensure file paths are correct

### 4. Case Sensitivity
**Problem**: Files work locally but not on server
**Solution**:
- Linux servers (Hostinger) are case-sensitive
- `DL-Logo.png` ≠ `dl-logo.png`
- Ensure all file names match exactly

## Verification Steps

1. **After uploading, check:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Reload page
   - Look for any 404 (red) errors

2. **Test these features:**
   - [ ] Dark mode toggle works
   - [ ] Navigation links work
   - [ ] Images load
   - [ ] Resume PDF loads
   - [ ] Mobile menu works
   - [ ] Smooth scrolling works

3. **Clear cache:**
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or clear browser cache completely

## File Upload Method

### Using FTP/File Manager:
1. Upload `index.html` to root (usually `public_html` or `www`)
2. Upload `styles.css` to same root directory
3. Upload `script.js` to same root directory
4. Upload entire `src/` folder maintaining structure
5. Upload `pages/` folder if needed

### Using Git (if available):
```bash
git add .
git commit -m "Update styles for dark mode"
git push origin main
```

## Quick Fix: Force Cache Refresh

If styles aren't updating, the HTML now includes version parameters (`?v=1.1`) that force browsers to reload CSS/JS files. If you update styles again, increment the version number.

## Still Having Issues?

1. Check browser console (F12 → Console tab) for errors
2. Check Network tab for failed file loads
3. Verify file structure matches exactly
4. Ensure `styles.css` is the updated file (should have dark mode variables)
5. Try accessing CSS directly: `https://yourdomain.com/styles.css`

