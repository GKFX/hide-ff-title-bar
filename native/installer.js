/*
 * This Source Code Form is subject to the terms of the Mozilla Public License,
 * v. 2.0. If a copy of the MPL was not distributed with this file, You can
 * obtain one at https://mozilla.org/MPL/2.0/.
 */

var field = document.querySelector("#location");
var manifestDLButton = document.querySelector("#manifest-download");
var manifestDLAnchor = document.querySelector("#manifest-a");

var manifest = {
  "name": "hide_title_bar",
  "description": "Hide the Firefox title bar, using GTK",
  "path": "/opt/bateman-hide-title-bar/native.py",
  "type": "stdio",
  "allowed_extensions": ["hidetitlebar@gkfx.github.com"]
}
var blobUri = "";

function makeManifest() {
  if (field.validity.valid) {
    manifest.path = field.value;
    blobUri = URL.createObjectURL(
      new Blob([JSON.stringify(manifest)], {type: "application/octet-stream"})
    );
  } else {
    blobUri = "";
  }
  manifestDLButton.disabled = !field.validity.valid || field.value === "";
  manifestDLAnchor.href = blobUri;
}

field.addEventListener("change", makeManifest);
manifestDLButton.addEventListener("click", () => { manifestDLAnchor.click(); });

makeManifest();
