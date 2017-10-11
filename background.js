/*
 * This Source Code Form is subject to the terms of the Mozilla Public License,
 * v. 2.0. If a copy of the MPL was not distributed with this file, You can
 * obtain one at https://mozilla.org/MPL/2.0/.
 */

function doNative(whenToHideTitleBar) {
  browser.runtime.sendNativeMessage("hide_title_bar",
    {whenToHideTitleBar: whenToHideTitleBar}).then(response => {
      if ("okay" in response && response.okay) {
        browser.storage.local.set({errorText: "NO_ERROR"});
      } else if ("knownFailure" in response) {
        browser.storage.local.set({errorText: "KNOWN_FAILURE:" + response.knownFailure});
      } else if ("unknownFailure" in response) {
        browser.storage.local.set({errorText: "UNKNOWN_FAILURE:" + response.unknownFailure});
      } else {
        browser.storage.local.set({errorText: "RESPONSE_NOT_UNDERSTOOD:" +
          JSON.stringify(response));
        console.log(response);
      }
    },  failure => {
      browser.storage.local.set({errorText: "NO_RESPONSE"});
      console.log(failure);
    });
}

browser.storage.local.get({ whenToHideTitleBar: "always" }).then(
  prefs => doNative(prefs.whenToHideTitleBar));

browser.storage.onChanged.addListener((changes, areaName) => {
  if (areaName !== "local") return;
  if ("whenToHideTitleBar" in changes) {
    doNative(changes.whenToHideTitleBar.newValue);
  }
});
