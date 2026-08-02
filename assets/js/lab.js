/*
 * Free RHCSA Course — lab guide theme toggle
 * Copyright (C) 2026 Shea's Tech. Licensed under the GNU AGPL v3.0 or later.
 */
(function () {
  "use strict";
  var root = document.documentElement, K = "rhcsa.theme.v1";
  function cur() {
    return root.getAttribute("data-theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  document.addEventListener("click", function (e) {
    if (!e.target.closest("[data-theme-toggle]")) return;
    var next = cur() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem(K, next); } catch (err) {}
  });
})();
