// Download Results - trigger browser print dialog
document.addEventListener("click", function (e) {
    var btn = e.target.closest("#download-results-pdf");
    if (!btn) return;
    window.print();
});
