/*
 * This Source Code Form is subject to the terms of the Mozilla Public License,
 * v. 2.0. If a copy of the MPL was not distributed with this file, You can
 * obtain one at https://mozilla.org/MPL/2.0/.
 */

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
