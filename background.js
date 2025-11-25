// Background script: Block trackers and poison data
(function() {
  'use strict';

  // List of known trackers to block
  const blockedDomains = [
    'doubleclick.net',
    'googlesyndication.com',
    'facebook.com/tr',
    'google-analytics.com',
    'googletagmanager.com',
    'amazon-adsystem.com',
    'adsystem.amazon.com'
  ];

  // Function to check if URL should be blocked
  function shouldBlock(url) {
    return blockedDomains.some(domain => url.includes(domain));
  }

  // Poison data: Modify tracking requests with fake data
  function poisonRequest(details) {
    if (shouldBlock(details.url)) {
      // Block the request
      return { cancel: true };
    }

    // For other requests, inject fake user agent or data if it's a tracking pixel
    if (details.url.includes('pixel') || details.url.includes('track')) {
      // Modify headers or body to send fake data
      const fakeData = 'fake_user_id=anomaly&fake_behavior=untrackable';
      return {
        requestHeaders: details.requestHeaders.map(header => {
          if (header.name.toLowerCase() === 'user-agent') {
            header.value = 'SovereignShield/1.0 (Untrackable)';
          }
          return header;
        }),
        // For POST requests, could modify body, but keep simple for now
      };
    }

    return {};
  }

  // Listen for web requests
  chrome.webRequest.onBeforeRequest.addListener(
    poisonRequest,
    { urls: ['<all_urls>'] },
    ['blocking', 'requestHeaders']
  );

  // Store stats
  let blockedCount = 0;
  chrome.webRequest.onBeforeRequest.addListener(
    (details) => {
      if (shouldBlock(details.url)) {
        blockedCount++;
        chrome.storage.local.set({ blockedCount });
      }
    },
    { urls: ['<all_urls>'] }
  );
})();