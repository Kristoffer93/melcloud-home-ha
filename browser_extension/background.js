// Background service worker för Chrome extension
// Lyssna på installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('MELCloud Home Cookie Extractor installerad');
});

// Lyssna på uppdateringar av cookies
chrome.cookies.onChanged.addListener((changeInfo) => {
    // Om en MELCloud-cookie ändras, notifiera användaren (optional)
    if (changeInfo.cookie.domain.includes('melcloudhome.com')) {
        console.log('MELCloud cookie updated:', changeInfo.cookie.name);
    }
});
