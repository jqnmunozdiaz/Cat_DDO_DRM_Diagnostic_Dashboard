// Download Results - trigger browser print dialog
document.addEventListener("click", function (e) {
    var btn = e.target.closest("#download-results-pdf, #download-results-pdf-bottom");
    if (!btn) return;
    window.print();
});
