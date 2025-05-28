let currentTab = null;
let timeSpent = 0;

function extractHostname(url) {
  try {
    let hostname = new URL(url).hostname.toLowerCase();
    return hostname.startsWith("www.") ? hostname.slice(4) : hostname;
  } catch {
    return null;
  }
}

chrome.tabs.onActivated.addListener(async (activeInfo) => {
  const tab = await chrome.tabs.get(activeInfo.tabId);
  const newSite = extractHostname(tab.url);
  if (currentTab && timeSpent > 0) {
    sendTrackingData(currentTab, timeSpent);
  }
  currentTab = newSite;
  timeSpent = 0;
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tab.active && changeInfo.url) {
    const hostname = extractHostname(changeInfo.url);
    if (hostname !== currentTab && timeSpent > 0) {
      sendTrackingData(currentTab, timeSpent);
      currentTab = hostname;
      timeSpent = 0;
    }
  }
});

setInterval(() => {
  if (currentTab) {
    timeSpent++;
    if (timeSpent % 60 === 0) {
      sendTrackingData(currentTab, 60);
      timeSpent = 0;
    }
  }
}, 1000);

function sendTrackingData(site, duration) {
  if (!site || !duration) return;
  fetch("http://127.0.0.1:5000/track", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user: "default", site: site, duration: duration })
  })
    .then(res => res.json())
    .then(console.log)
    .catch(console.error);
}
