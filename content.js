// Content script: Remove ad elements from DOM
(function() {
  'use strict';

  // Check if blocking is enabled
  chrome.storage.local.get(['enabled'], (result) => {
    if (result.enabled === false) return;

    // Selectors for common ad elements
    const adSelectors = [
      'div[id*="ad"]',
      'div[class*="ad"]',
      'iframe[src*="doubleclick"]',
      'iframe[src*="googlesyndication"]',
      'div[data-ad]',
      'ins.adsbygoogle',
      '.ad-banner',
      '.advertisement'
    ];

    // Function to remove elements
    function removeAds() {
      adSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => el.remove());
      });
    }

    // Initial removal
    removeAds();

    // Observe for dynamically added ads
    const observer = new MutationObserver(removeAds);
    observer.observe(document.body, { childList: true, subtree: true });
  });
})();