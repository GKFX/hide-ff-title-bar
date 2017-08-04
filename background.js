function doNative(whenToHideTitleBar) {
  browser.runtime.sendNativeMessage("hide_title_bar",
    {whenToHideTitleBar: whenToHideTitleBar}).then(response => {
      if (response !== true) {
        console.log("Hide title bar native error: " + response)
      }
    },  failure => console.log(failure));
}

browser.storage.local.get({ whenToHideTitleBar: "always" }).then(
  prefs => doNative(prefs.whenToHideTitleBar));

browser.storage.onChanged.addListener((changes, areaName) => {
  if (areaName !== "local") return;
  if ("whenToHideTitleBar" in changes) {
    doNative(changes.whenToHideTitleBar.newValue);
  }
});
