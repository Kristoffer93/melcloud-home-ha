# Hämta Cookie från Network-fliken (Fungerar alltid!)

## ⚠️ Problem med document.cookie
Om `document.cookie` returnerar `undefined`, betyder det att cookies är **HttpOnly** och inte tillgängliga via JavaScript. Detta är vanligt för säkerhet.

## ✅ Lösning: Använd Network-fliken

### Steg 1: Förbered
1. Öppna **Chrome**
2. Gå till: **https://melcloudhome.com**
3. **Logga in** (om du inte redan är inloggad)

### Steg 2: Öppna Developer Tools
1. Tryck **F12**
2. Klicka på fliken **Network** (överst)
3. Se till att **recording** är aktivt (röd cirkel ska lysa)

### Steg 3: Ladda om sidan
1. Tryck **F5** eller **Ctrl+R** för att ladda om sidan
2. Vänta tills sidan laddats helt

### Steg 4: Hitta ett API-anrop
1. I Network-listan, hitta en request till **melcloudhome.com**
2. Leta efter något som heter:
   - `dashboard` (första requesten)
   - `configuration`
   - `user/context`
3. **Klicka** på requesten

### Steg 5: Kopiera Cookie
1. I högra panelen, scrolla ner till **Request Headers**
2. Leta efter raden som börjar med `cookie:`
3. **Högerklicka** på cookie-värdet
4. Välj **Copy value**

Exempel på hur det ser ut:
```
cookie: .AspNetCore.Antiforgery.xxx=...; .AspNetCore.Session.xxx=...; ARRAffinity=...
```

### Steg 6: Spara Cookie
1. Öppna **Notepad** (eller textredigerare)
2. **Klistra in** cookie-värdet
3. Spara som: **`melcloud_cookie.txt`**
4. Spara i mappen: **`c:\git\melcloud-home-ha\`**

### Steg 7: Testa
Öppna PowerShell i `c:\git\melcloud-home-ha\` och kör:
```powershell
python test_ha_integration.py
```

## 🎯 Tips

### Hitta rätt Request snabbt:
1. I Network-fliken, skriv **"api"** i sökfältet (filter)
2. Detta visar bara API-anrop
3. Klicka på vilket som helst (de har samma cookies)

### Om du inte ser cookie-headern:
1. Se till att du är inloggad
2. Ladda om sidan (F5)
3. Klicka på den **första** requesten som laddas

### Verifiera att cookien fungerar:
När du kör `python test_ha_integration.py` ska du se:
```
✓ Inloggad som: Kristoffer Gustavsson
✓ Email: kristoffer.gustafsson1@gmail.com
✓ Byggnader: 1
✓ Hittade X ATW-enhet(er)
```

## ❓ Felsökning

### "Cookie ogiltig"
- Kontrollera att du kopierade **hela** cookie-strängen
- Se till att du är inloggad när du kopierar
- Försök logga ut och in igen, sedan kopiera igen

### "Inga requests i Network"
- Tryck F5 för att ladda om sidan
- Kontrollera att Recording är aktivt (röd cirkel)

### Cookien slutar fungera efter ett tag
- Cookies upphör automatiskt efter en tid
- Hämta bara en ny cookie (samma process)
- Detta är normalt!
