document.getElementById('extractBtn').addEventListener('click', async () => {
    const statusDiv = document.getElementById('status');
    const extractBtn = document.getElementById('extractBtn');
    const copyBtn = document.getElementById('copyBtn');
    const textarea = document.getElementById('cookieValue');
    
    // Visa laddar-status
    statusDiv.className = 'info';
    statusDiv.textContent = '⏳ Hämtar cookies...';
    statusDiv.style.display = 'block';
    extractBtn.disabled = true;
    
    try {
        // Hämta alla cookies från melcloudhome.com
        const cookies = await chrome.cookies.getAll({
            domain: 'melcloudhome.com'
        });
        
        if (!cookies || cookies.length === 0) {
            throw new Error('Inga cookies hittades. Är du inloggad på melcloudhome.com?');
        }
        
        // Filtrera och formatera cookies
        const relevantCookies = cookies.filter(cookie => 
            cookie.name.includes('Secure-monitorandcontrol') || 
            cookie.name.includes('Host-blazor')
        );
        
        if (relevantCookies.length === 0) {
            throw new Error('Inga MELCloud-cookies hittades. Logga in först på melcloudhome.com');
        }
        
        // Bygg cookie-sträng
        const cookieString = relevantCookies
            .map(cookie => `${cookie.name}=${cookie.value}`)
            .join('; ');
        
        // Visa framgång
        statusDiv.className = 'success';
        statusDiv.textContent = `✅ ${relevantCookies.length} cookie(s) extraherad!`;
        
        // Visa cookie och kopieringsknapp
        textarea.value = cookieString;
        textarea.style.display = 'block';
        copyBtn.style.display = 'block';
        extractBtn.disabled = false;
        
        // Spara i storage för framtida användning
        await chrome.storage.local.set({ 
            lastCookie: cookieString,
            lastUpdate: new Date().toISOString()
        });
        
    } catch (error) {
        statusDiv.className = 'error';
        statusDiv.textContent = `❌ ${error.message}`;
        extractBtn.disabled = false;
        console.error('Cookie extraction error:', error);
    }
});

document.getElementById('copyBtn').addEventListener('click', () => {
    const textarea = document.getElementById('cookieValue');
    const copyBtn = document.getElementById('copyBtn');
    
    textarea.select();
    document.execCommand('copy');
    
    const originalText = copyBtn.textContent;
    copyBtn.textContent = '✅ Kopierad!';
    setTimeout(() => {
        copyBtn.textContent = originalText;
    }, 2000);
});

// Kolla om det finns sparad cookie
chrome.storage.local.get(['lastCookie', 'lastUpdate'], (result) => {
    if (result.lastCookie) {
        const statusDiv = document.getElementById('status');
        const lastUpdate = new Date(result.lastUpdate);
        const now = new Date();
        const hoursSince = (now - lastUpdate) / (1000 * 60 * 60);
        
        if (hoursSince < 24) {
            statusDiv.className = 'info';
            statusDiv.textContent = `ℹ️ Senaste cookie: ${Math.round(hoursSince)}h sedan`;
            statusDiv.style.display = 'block';
        }
    }
});
