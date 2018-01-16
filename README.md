# Retired

This WebExtension has been retired. It is really beyond the scope of what a WebExtension can do; APIs used by HTitle are gone and workarounds aren't really there. Specifically, the lack of window controls would always have remained an unsolved problem. I could have continued to pile hacks upon bodges, but in practice this project would never really have become particularly stable or reliable.

Mozilla are working on doing this properly — it's [bug 1283299](https://bugzilla.mozilla.org/show_bug.cgi?id=1283299) if you want an idea of progress. Ultimately it makes far more sense simply to wait for this to be released.

Many thanks to everyone who commented and submitted code.

George.

># Hide Title Bar
>
>An addon for Firefox, compatible with GTK 3.
>
>## Build
>```bash
>./build.sh
>```
>
>## Install
>Unsigned versions can only be installed on developer editions of Firefox, or temporarily through `about:debugging`.
>
>Releases are at https://addons.mozilla.org/en-US/firefox/addon/hide-title-bar/.
>
>The native script can be installed by hand or through a Debian package; these are both accessed from within the add-on.
>
>An Arch Linux package for the native script exists at https://aur.archlinux.org/pkgbase/hide-ff-title-bar-git/. *This package >was produced by a third party so I cannot accept responsibility for its contents.*
