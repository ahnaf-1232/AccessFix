
            // @ts-check
            const { test, expect } = require('@playwright/test');
            const AxeBuilder = require('@axe-core/playwright').default;
            const fileReader = require('fs');

            test('all violations', async ({ page }) => {
                await page.goto("https://calendar.google.com/");
                await page.setContent(`<!DOCTYPE html>
<html dir="ltr" lang="en">
 <head>
  <base href="https://calendar.google.com/"/>
  <link href="https://calendar.google.com/" rel="canonical"/>
  <meta content="origin-when-cross-origin" name="referrer"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <link href="https://workspace.google.com/lp/static/images/favicon.ico?fingerprint=913d48cd5d48ba34313131f246f99d6b" rel="shortcut icon"/>
  <title>
   Google Calendar - Easier Time Management, Appointments &amp; Scheduling
  </title>
  <meta content="Learn how Google Calendar helps you stay on top of your plans - at home, at work and everywhere in between." name="description"/>
  <meta content="summary" name="twitter:card">
   <meta content="Learn how Google Calendar helps you stay on top of your plans - at home, at work and everywhere in between." name="twitter:description">
    <meta content="Google Calendar - Easier Time Management, Appointments &amp; Scheduling" name="twitter:title">
     <meta content="https://fonts.gstatic.com/s/i/productlogos/calendar_2020q4/v13/192px.svg" name="twitter:image"/>
     <meta content="@googleworkspace" name="twitter:site"/>
     <meta content="@googleworkspace" name="twitter:creator"/>
     <meta content="https://calendar.google.com/" property="og:url"/>
     <meta content="website" property="og:type"/>
     <meta content="Google Workspace" property="og:site_name"/>
     <meta content="Google Calendar - Easier Time Management, Appointments &amp; Scheduling" property="og:title"/>
     <meta content="Learn how Google Calendar helps you stay on top of your plans - at home, at work and everywhere in between." property="og:description"/>
     <meta content="https://fonts.gstatic.com/s/i/productlogos/calendar_2020q4/v13/192px.svg" property="og:image"/>
    </meta>
   </meta>
  </meta>
 </head>
 <body style="height:100%;overflow:hidden;-webkit-font-smoothing:antialiased;color:rgba(0,0,0,0.87);font-family:Roboto,RobotoDraft,Helvetica,Arial,sans-serif;font-weight:400;margin:0;-webkit-text-size-adjust:100%;-webkit-text-size-adjust:100%;text-size-adjust:100%;-webkit-user-select:none">
  <div class="root">
   <div style="padding:32px 64px">
    <img alt="Google Calendar" src="https://fonts.gstatic.com/s/i/productlogos/calendar_2020q4/v13/192px.svg" style="border:none"/>
   </div>
   <div style="color:#5f6368;font-size:20px;font-weight:500;padding-left:16px">
    Google Calendar - Easier Time Management, Appointments &amp; Scheduling
   </div>
   <div style="color:rgba(0,0,0,0.871);font-size:15px;padding:16px">
    Learn how Google Calendar helps you stay on top of your plans - at home, at work and everywhere in between.
   </div>
   <script nonce="EXWHFvPRpT2atbONyDOtlQ" type="application/ld+json">
    {
    "@context": "https://schema.org",
    "@type": "Product",
    "brand": {"@type": "Organization", "name": "Google"},
    "name": "Google Calendar",
    "description":  "Learn how Google Calendar helps you stay on top of your plans - at home, at work and everywhere in between.",
    "url": "https://calendar.google.com/",
    "logo": "https://fonts.gstatic.com/s/i/productlogos/calendar_2020q4/v13/192px.svg",
    "isRelatedTo": {"@type": "Product", "name": "Google Workspace"},
    "sameAs": [
        "https://twitter.com/googleworkspace",
        "https://cloud.googleblog.com/",
        "https://www.youtube.com/googleworkspace/",
        "https://www.facebook.com/googleworkspace/",
        "https://en.wikipedia.org/wiki/Google_Calendar",
        "https://en.wikipedia.org/wiki/Google_Workspace",
        "https://www.wikidata.org/wiki/Q509284"
    ]
}
   </script>
  </div>
 </body>
</html>
`)
                const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
                const violations = accessibilityScanResults.violations;

                fileReader.writeFile("num_violations2.txt", String(violations.length), function(err) {
                    if (err) console.log(err);
                });

                for (let i = 0; i < violations.length; i++) {
                    fileReader.writeFile("data" + i + ".json", JSON.stringify(violations[i]), function(err) {
                        if (err) console.log(err);
                    });
                }
            });
            