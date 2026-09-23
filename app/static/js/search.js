// /app: mark shown results as stale once any form control changes. Nothing else.
(function () {
  var form = document.querySelector("[data-search-form]");
  var note = document.querySelector(".search-changed");
  if (!form || !note) return;
  function stale() { note.hidden = false; }
  form.addEventListener("change", stale);
  form.addEventListener("input", stale);
})();
