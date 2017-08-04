function onError(err) {
  console.log(`Error: ${err}`);
}

var select = document.querySelector("select");
browser.storage.local.get({ whenToHideTitleBar: "always" }).then(
  prefs => {
    select.querySelector("[value=" + prefs.whenToHideTitleBar + "]").selected = true;
  }, onError);

select.addEventListener("change", () => {
  browser.storage.local.set({whenToHideTitleBar: select.options[select.selectedIndex].value}).then(null, onError);
});

var installButton = document.querySelector("#install");
installButton.addEventListener("click", () => {
  browser.tabs.create({url: "/native/installer.html"});
});

var error = document.querySelector("#error");
browser.storage.onChanged.addListener((changes, areaName) => {
  if (areaName !== "local") return;
  if ("errorText" in changes) {
    error.innerText = changes.errorText.newValue;
  }
});
